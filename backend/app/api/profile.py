"""Profile, onboarding, privacy (export / delete account)."""
import sqlalchemy as sa
from flask import Blueprint, jsonify
from marshmallow import Schema, ValidationError, fields, validate, validates_schema

from ..extensions import db
from ..models import (
    Application, Category, ChatSession, Notification, Reminder, SavedOpportunity, State, UploadedDocument, User,
)
from ..models.base import EDUCATION_LEVELS, GENDERS, INCOME_RANGES, LANGUAGES, MARKS_TYPES, SOCIAL_CATEGORIES
from ..serializers import (
    application_dict, document_dict, notification_dict, profile_dict, reminder_dict, user_dict,
)
from ..services import storage
from ..utils.auth import current_user, login_required, verify_password
from ..utils.errors import APIError
from ..utils.helpers import body, iso, utcnow

bp = Blueprint("profile", __name__, url_prefix="/api/v1/profile")


def _choice(values):
    return validate.OneOf(values)


class ProfileSchema(Schema):
    full_name = fields.String(validate=validate.Length(min=2, max=120))
    date_of_birth = fields.Date(allow_none=True)
    gender = fields.String(allow_none=True, validate=_choice(GENDERS))
    state_code = fields.String(allow_none=True, validate=validate.Length(max=40))
    city = fields.String(allow_none=True, validate=validate.Length(max=80))
    education_level = fields.String(allow_none=True, validate=_choice(EDUCATION_LEVELS))
    institution = fields.String(allow_none=True, validate=validate.Length(max=160))
    course = fields.String(allow_none=True, validate=validate.Length(max=120))
    stream = fields.String(allow_none=True, validate=validate.Length(max=120))
    current_year = fields.Integer(allow_none=True, validate=validate.Range(1, 10))
    marks_type = fields.String(allow_none=True, validate=_choice(MARKS_TYPES))
    marks_value = fields.Float(allow_none=True, validate=validate.Range(0, 100))
    income_range = fields.String(allow_none=True, validate=_choice(INCOME_RANGES))
    social_category = fields.String(allow_none=True, validate=_choice(SOCIAL_CATEGORIES))
    has_disability = fields.Boolean(allow_none=True)
    skills = fields.List(fields.String(validate=validate.Length(max=40)), validate=validate.Length(max=30))
    career_interests = fields.List(fields.String(validate=validate.Length(max=60)), validate=validate.Length(max=20))
    interests = fields.List(fields.String(), validate=validate.Length(max=10))
    preferred_language = fields.String(validate=_choice(LANGUAGES))
    onboarding_step = fields.Integer(validate=validate.Range(0, 5))

    @validates_schema
    def _marks(self, data, **_):
        mtype, value = data.get("marks_type"), data.get("marks_value")
        if value is not None and mtype == "cgpa" and value > 10:
            raise ValidationError({"marks_value": "CGPA must be between 0 and 10."})
        if value is not None and not mtype:
            raise ValidationError({"marks_type": "Choose percentage or CGPA."})


class DeleteAccountSchema(Schema):
    password = fields.String(required=True)


@bp.get("")
@login_required
def get_profile():
    return jsonify(user=user_dict(current_user()))


@bp.put("")
@login_required
def update_profile():
    data = body(ProfileSchema(), partial=True)
    user = current_user()
    p = user.profile
    if "state_code" in data and data["state_code"] and db.session.get(State, data["state_code"]) is None:
        raise APIError("Unknown state.", 422, "validation_error", {"state_code": "Choose a state from the list."})
    interests = data.pop("interests", None)
    for key, value in data.items():
        if isinstance(value, str):
            value = value.strip() or None
        setattr(p, key, value)
    if interests is not None:
        p.interests = db.session.scalars(sa.select(Category).where(Category.slug.in_(interests))).all()
    db.session.commit()
    return jsonify(user=user_dict(user))


@bp.post("/onboarding/complete")
@login_required
def complete_onboarding():
    user = current_user()
    user.profile.onboarding_completed_at = user.profile.onboarding_completed_at or utcnow()
    user.profile.onboarding_step = 5
    db.session.commit()
    return jsonify(user=user_dict(user))


@bp.get("/export")
@login_required
def export():
    """Everything we store about the user, as JSON (right to access)."""
    u = current_user()
    q = lambda model: db.session.scalars(sa.select(model).where(model.user_id == u.id)).all()  # noqa: E731
    chats = []
    for s in q(ChatSession):
        chats.append({"title": s.title, "created_at": iso(s.created_at),
                      "messages": [{"role": m.role, "content": m.content, "at": iso(m.created_at)} for m in s.messages]})
    data = {
        "exported_at": iso(utcnow()),
        "account": {"email": u.email, "role": u.role, "created_at": iso(u.created_at)},
        "profile": profile_dict(u.profile),
        "saved_opportunities": [s.opportunity.title for s in q(SavedOpportunity)],
        "applications": [application_dict(a, full=True) for a in q(Application)],
        "documents": [document_dict(d) for d in q(UploadedDocument) if d.deleted_at is None],
        "reminders": [reminder_dict(r) for r in q(Reminder)],
        "notifications": [notification_dict(n) for n in q(Notification)],
        "chats": chats,
    }
    resp = jsonify(data)
    resp.headers["Content-Disposition"] = "attachment; filename=formsaathi-my-data.json"
    return resp


@bp.delete("/account")
@login_required
def delete_account():
    data = body(DeleteAccountSchema())
    user = current_user()
    if not verify_password(user.password_hash, data["password"]):
        raise APIError("Password is incorrect.", 422, "validation_error", {"password": "Incorrect."})
    if user.role == "admin" and db.session.scalar(
            sa.select(sa.func.count(User.id)).where(User.role == "admin")) <= 1:
        raise APIError("You are the only admin. Promote another admin before deleting this account.", 409, "last_admin")
    storage.delete_all(user.id)
    db.session.delete(user)  # cascades to every personal-data table
    db.session.commit()
    from flask_jwt_extended import unset_jwt_cookies

    resp = jsonify(message="Your account and personal data have been deleted.")
    unset_jwt_cookies(resp)
    return resp
