"""Auth helpers: password hashing, current user lookup, role decorator."""
from functools import wraps

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
from flask import g
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from ..extensions import db
from ..models import User
from .errors import APIError

_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def current_user() -> User:
    """The authenticated, active user. Call only inside a protected route."""
    uid = int(get_jwt_identity())
    cached = g.get("current_user")
    if cached is None or cached.id != uid:  # never reuse a user object across identities
        user = db.session.get(User, uid)
        if user is None or not user.is_active:
            raise APIError("Your session is no longer valid. Please log in again.", 401, "unauthorized")
        g.current_user = user
    return g.current_user


def optional_user() -> User | None:
    try:
        verify_jwt_in_request(optional=True)
    except Exception:  # expired/invalid token on a public route -> treat as anonymous
        return None
    identity = get_jwt_identity()
    if identity is None:
        return None
    user = db.session.get(User, int(identity))
    return user if user and user.is_active else None


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        current_user()
        return fn(*args, **kwargs)

    return wrapper


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        if current_user().role != "admin":
            raise APIError("Admins only.", 403, "forbidden")
        return fn(*args, **kwargs)

    return wrapper
