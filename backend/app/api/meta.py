"""Reference data, announcements, feedback, health."""
import json
from pathlib import Path

import sqlalchemy as sa
from flask import Blueprint, current_app, jsonify
from marshmallow import Schema, fields, validate

from ..extensions import db, limiter
from ..models import Announcement, Category, DocumentType, Feedback, State
from ..models import base as enums
from ..serializers import category_dict, document_type_dict
from ..services import llm, mailer
from ..utils.auth import optional_user
from ..utils.helpers import body, iso, utcnow

bp = Blueprint("meta", __name__, url_prefix="/api/v1")


class FeedbackSchema(Schema):
    kind = fields.String(required=True, validate=validate.OneOf(enums.FEEDBACK_KINDS))
    message = fields.String(required=True, validate=validate.Length(min=5, max=3000))
    page = fields.String(load_default=None, validate=validate.Length(max=200))
    contact_email = fields.Email(load_default=None)


def portals() -> list:
    path = Path(current_app.config["SHARED_DIR"]) / "reference.json"
    return json.loads(path.read_text(encoding="utf-8")).get("portals", [])


@bp.get("/health")
def health():
    return jsonify(status="ok", ai_configured=llm.is_configured(), email_configured=mailer.is_configured())


@bp.get("/meta")
def meta():
    cats = db.session.scalars(sa.select(Category).where(Category.is_active.is_(True)).order_by(Category.sort_order)).all()
    states = db.session.scalars(sa.select(State).order_by(State.name)).all()
    docs = db.session.scalars(sa.select(DocumentType).order_by(DocumentType.sort_order)).all()
    return jsonify(
        categories=[category_dict(c) for c in cats],
        states=[{"code": s.code, "name": s.name, "kind": s.kind} for s in states],
        document_types=[document_type_dict(d) for d in docs],
        enums={k.lower(): list(getattr(enums, k)) for k in (
            "EDUCATION_LEVELS", "INCOME_RANGES", "SOCIAL_CATEGORIES", "GENDERS", "LANGUAGES",
            "APPLICATION_STATUSES", "CRITERION_TYPES", "VERIFICATION_STATUSES", "PUBLICATION_STATUSES",
            "ORG_TYPES", "BENEFIT_FREQUENCIES", "APPLICATION_MODES", "OPPORTUNITY_SCOPES", "CORRECTION_FIELDS",
            "FEEDBACK_KINDS", "NOTIFICATION_TYPES")},
        portals=portals(),
        features={"ai": llm.is_configured(), "email": mailer.is_configured(), "preview": False},
    )


@bp.get("/announcements")
def announcements():
    now = utcnow()
    user = optional_user()
    audiences = ["all", "users"] + (["admins"] if user and user.role == "admin" else [])
    rows = db.session.scalars(sa.select(Announcement).where(
        Announcement.is_active.is_(True), Announcement.audience.in_(audiences),
        sa.or_(Announcement.starts_at.is_(None), Announcement.starts_at <= now),
        sa.or_(Announcement.ends_at.is_(None), Announcement.ends_at >= now),
    ).order_by(Announcement.created_at.desc()).limit(3)).all()
    return jsonify(items=[{"id": a.id, "title": a.title, "body": a.body, "level": a.level,
                           "created_at": iso(a.created_at)} for a in rows])


@bp.post("/feedback")
@limiter.limit("10 per hour")
def feedback():
    data = body(FeedbackSchema())
    user = optional_user()
    db.session.add(Feedback(user_id=user.id if user else None, kind=data["kind"], message=data["message"].strip(),
                            page=data["page"], contact_email=None if user else data["contact_email"]))
    db.session.commit()
    return jsonify(message="Thank you! Your feedback has been received."), 201
