"""Registration, login/logout, token refresh, password reset."""
import hashlib
import logging
import re
import secrets
from datetime import timedelta

import sqlalchemy as sa
from flask import Blueprint, current_app, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token, get_jwt, get_jwt_identity, jwt_required,
    set_access_cookies, set_refresh_cookies, unset_jwt_cookies, verify_jwt_in_request,
)
from marshmallow import Schema, ValidationError, fields, validate, validates

from ..extensions import db, limiter
from ..models import NotificationPreference, RevokedToken, User, UserProfile, UserToken
from ..serializers import user_dict
from ..services import mailer
from ..utils.auth import current_user, hash_password, login_required, verify_password
from ..utils.errors import APIError
from ..utils.helpers import aware, body, utcnow

bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")
log = logging.getLogger("formsaathi.auth")

MAX_FAILED_LOGINS = 5
LOCK_MINUTES = 15


def _password_rules(value: str):
    if len(value) < 8 or not re.search(r"[A-Za-z]", value) or not re.search(r"\d", value):
        raise ValidationError("Use at least 8 characters with letters and numbers.")


class RegisterSchema(Schema):
    email = fields.Email(required=True, validate=validate.Length(max=254))
    password = fields.String(required=True, validate=[validate.Length(max=128), _password_rules], load_only=True)
    full_name = fields.String(required=True, validate=validate.Length(min=2, max=120))
    accept_terms = fields.Boolean(required=True)

    @validates("accept_terms")
    def _terms(self, value, **_):
        if not value:
            raise ValidationError("Please accept the terms and privacy policy.")


class LoginSchema(Schema):
    email = fields.String(required=True, validate=validate.Length(max=254))
    password = fields.String(required=True, validate=validate.Length(max=128))


class EmailSchema(Schema):
    email = fields.String(required=True, validate=validate.Length(max=254))


class ResetSchema(Schema):
    token = fields.String(required=True, validate=validate.Length(min=20, max=200))
    password = fields.String(required=True, validate=[validate.Length(max=128), _password_rules])


class ChangePasswordSchema(Schema):
    current_password = fields.String(required=True)
    new_password = fields.String(required=True, validate=[validate.Length(max=128), _password_rules])


def _login_response(user: User, status: int = 200):
    user.last_login_at = utcnow()
    db.session.commit()
    resp = jsonify(user=user_dict(user))
    set_access_cookies(resp, create_access_token(identity=str(user.id), additional_claims={"role": user.role}))
    set_refresh_cookies(resp, create_refresh_token(identity=str(user.id)))
    return resp, status


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


@bp.post("/register")
@limiter.limit("10 per hour")
def register():
    data = body(RegisterSchema())
    email = data["email"].strip().lower()
    if db.session.scalar(sa.select(User.id).where(User.email == email)):
        raise APIError("An account with this email already exists. Try logging in.", 409, "email_taken",
                       {"email": "Already registered."})
    user = User(email=email, password_hash=hash_password(data["password"]))
    user.profile = UserProfile(full_name=data["full_name"].strip())
    db.session.add(user)
    db.session.flush()
    db.session.add(NotificationPreference(user_id=user.id))
    return _login_response(user, 201)


@bp.post("/login")
@limiter.limit("20 per minute; 100 per hour")
def login():
    data = body(LoginSchema())
    user = db.session.scalar(sa.select(User).where(User.email == data["email"].strip().lower()))
    generic = APIError("Email or password is incorrect.", 401, "invalid_credentials")
    if user is None:
        verify_password(hash_password("timing-equaliser"), data["password"])  # keep timing similar
        raise generic
    if user.locked_until and aware(user.locked_until) > utcnow():
        raise APIError("Too many failed attempts. Please try again in a few minutes or reset your password.",
                       429, "account_locked")
    if not verify_password(user.password_hash, data["password"]):
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= MAX_FAILED_LOGINS:
            user.locked_until = utcnow() + timedelta(minutes=LOCK_MINUTES)
            user.failed_login_attempts = 0
        db.session.commit()
        raise generic
    if not user.is_active:
        raise APIError("This account has been deactivated. Contact support.", 403, "account_disabled")
    user.failed_login_attempts, user.locked_until = 0, None
    return _login_response(user)


@bp.post("/logout")
def logout():
    # Revoke whatever tokens are present; logging out should never fail for the user.
    for refresh in (False, True):
        try:
            verify_jwt_in_request(optional=True, refresh=refresh, verify_type=True)
            claims = get_jwt()
            if claims.get("jti"):
                db.session.merge(RevokedToken(jti=claims["jti"], expires_at=utcnow() + timedelta(days=15)))
        except Exception:
            pass
    db.session.commit()
    resp = jsonify(ok=True)
    unset_jwt_cookies(resp)
    return resp


@bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    user = db.session.get(User, int(get_jwt_identity()))
    if user is None or not user.is_active:
        raise APIError("Please log in again.", 401, "unauthorized")
    resp = jsonify(user=user_dict(user))
    set_access_cookies(resp, create_access_token(identity=str(user.id), additional_claims={"role": user.role}))
    return resp


@bp.get("/me")
@login_required
def me():
    return jsonify(user=user_dict(current_user()))


@bp.post("/forgot-password")
@limiter.limit("5 per hour")
def forgot_password():
    data = body(EmailSchema())
    user = db.session.scalar(sa.select(User).where(User.email == data["email"].strip().lower()))
    extra = {}
    if user and user.is_active:
        token = secrets.token_urlsafe(32)
        db.session.add(UserToken(user_id=user.id, purpose="reset_password", token_hash=_hash_token(token),
                                 expires_at=utcnow() + timedelta(minutes=30)))
        db.session.commit()
        link = f"{current_app.config['FRONTEND_URL'].rstrip('/')}/reset-password/{token}"
        sent = mailer.send(user.email, "Reset your FormSaathi password",
                           f"Use this link within 30 minutes to set a new password:\n\n{link}\n\n"
                           "If you didn't ask for this, you can ignore this email.")
        if not sent and current_app.debug:
            extra["dev_reset_link"] = link  # local development only, never in production
    return jsonify(
        message="If an account exists for that email, we've sent a reset link.",
        email_configured=mailer.is_configured(), **extra,
    )


@bp.post("/reset-password")
@limiter.limit("10 per hour")
def reset_password():
    data = body(ResetSchema())
    row = db.session.scalar(sa.select(UserToken).where(
        UserToken.token_hash == _hash_token(data["token"]), UserToken.purpose == "reset_password"))
    if row is None or row.used_at is not None or aware(row.expires_at) < utcnow():
        raise APIError("This reset link is invalid or has expired. Please request a new one.", 400, "invalid_token")
    user = db.session.get(User, row.user_id)
    user.password_hash = hash_password(data["password"])
    user.failed_login_attempts, user.locked_until = 0, None
    row.used_at = utcnow()
    db.session.commit()
    return jsonify(message="Password updated. You can log in now.")


@bp.post("/change-password")
@login_required
def change_password():
    data = body(ChangePasswordSchema())
    user = current_user()
    if not verify_password(user.password_hash, data["current_password"]):
        raise APIError("Current password is incorrect.", 422, "validation_error", {"current_password": "Incorrect."})
    user.password_hash = hash_password(data["new_password"])
    db.session.commit()
    return jsonify(message="Password changed.")


def register_jwt_callbacks(jwt):
    @jwt.token_in_blocklist_loader
    def _revoked(_header, payload):
        return db.session.get(RevokedToken, payload["jti"]) is not None

    def _err(message, code, status=401):
        return jsonify(error={"code": code, "message": message}), status

    jwt.expired_token_loader(lambda h, p: _err("Your session expired.", "token_expired"))
    jwt.invalid_token_loader(lambda reason: _err("Please log in again.", "unauthorized"))
    jwt.unauthorized_loader(lambda reason: _err(
        "Security check failed. Please refresh the page." if "CSRF" in reason else "Please log in to continue.",
        "csrf_failed" if "CSRF" in reason else "unauthorized"))
    jwt.revoked_token_loader(lambda h, p: _err("Please log in again.", "unauthorized"))
