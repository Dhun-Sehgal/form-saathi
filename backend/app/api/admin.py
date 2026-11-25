"""Admin panel API. Every route requires role == admin."""
import re
from datetime import timedelta

import sqlalchemy as sa
from flask import Blueprint, jsonify, request
from marshmallow import Schema, ValidationError, fields, validate, validates_schema
from sqlalchemy.orm import selectinload

from ..extensions import db
from ..models import (
    Announcement, Application, Category, ChatMessage, CorrectionReport, DocumentType, EligibilityCriterion, Feedback,
    Opportunity, OpportunityDate, Organization, RequiredDocument, SavedOpportunity, SourceVerificationLog, State,
    UploadedDocument, User, opportunity_education_levels,
)
from ..models import base as enums
from ..serializers import category_dict, correction_dict, opportunity_card, opportunity_detail, organization_dict
from ..services import notify
from ..utils.auth import admin_required, current_user
from ..utils.errors import APIError, not_found
from ..utils.helpers import body, int_arg, iso, paginate, utcnow

bp = Blueprint("admin", __name__, url_prefix="/api/v1/admin")
URL = fields.Url(schemes={"http", "https"}, validate=validate.Length(max=500))


class CriterionIn(Schema):
    criterion_type = fields.String(required=True, validate=validate.OneOf(enums.CRITERION_TYPES))
    value = fields.Dict(load_default=dict)
    description = fields.String(required=True, validate=validate.Length(min=3, max=500))
    source_excerpt = fields.String(load_default=None, allow_none=True)
    is_mandatory = fields.Boolean(load_default=True)


class DocIn(Schema):
    document_type_id = fields.Integer(required=True)
    is_mandatory = fields.Boolean(load_default=True)
    notes = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=300))


class DateIn(Schema):
    label = fields.String(required=True, validate=validate.Length(min=2, max=120))
    date = fields.Date(required=True)
    note = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=200))


class OpportunityIn(Schema):
    title = fields.String(required=True, validate=validate.Length(min=5, max=200))
    slug = fields.String(load_default=None, allow_none=True, validate=validate.Regexp(r"^[a-z0-9-]{3,160}$"))
    summary = fields.String(required=True, validate=validate.Length(min=10, max=400))
    description = fields.String(required=True, validate=validate.Length(min=10))
    category_id = fields.Integer(required=True)
    organization_id = fields.Integer(load_default=None, allow_none=True)
    organization_name = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=200))
    organization_type = fields.String(load_default="other", validate=validate.OneOf(enums.ORG_TYPES))
    scope = fields.String(load_default="national", validate=validate.OneOf(enums.OPPORTUNITY_SCOPES))
    eligibility_summary = fields.String(required=True, validate=validate.Length(min=5, max=500))
    benefits = fields.String(required=True, validate=validate.Length(min=3))
    benefit_amount_min = fields.Decimal(load_default=None, allow_none=True, places=2, validate=validate.Range(0))
    benefit_amount_max = fields.Decimal(load_default=None, allow_none=True, places=2, validate=validate.Range(0))
    benefit_frequency = fields.String(load_default=None, allow_none=True, validate=validate.OneOf(enums.BENEFIT_FREQUENCIES))
    application_mode = fields.String(load_default="online", validate=validate.OneOf(enums.APPLICATION_MODES))
    how_to_apply = fields.String(load_default=None, allow_none=True)
    official_url = fields.Url(load_default=None, allow_none=True, schemes={"http", "https"})
    apply_url = fields.Url(load_default=None, allow_none=True, schemes={"http", "https"})
    source_url = fields.Url(required=True, schemes={"http", "https"})
    opens_on = fields.Date(load_default=None, allow_none=True)
    deadline = fields.Date(load_default=None, allow_none=True)
    is_rolling = fields.Boolean(load_default=False)
    deadline_note = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=200))
    data_origin = fields.String(load_default="official", validate=validate.OneOf(enums.DATA_ORIGINS))
    is_featured = fields.Boolean(load_default=False)
    criteria = fields.List(fields.Nested(CriterionIn), load_default=list)
    required_documents = fields.List(fields.Nested(DocIn), load_default=list)
    dates = fields.List(fields.Nested(DateIn), load_default=list)

    @validates_schema
    def _checks(self, data, **_):
        errs = {}
        if not data.get("organization_id") and not data.get("organization_name"):
            errs["organization_id"] = "Choose an organisation or enter a new one."
        lo, hi = data.get("benefit_amount_min"), data.get("benefit_amount_max")
        if lo is not None and hi is not None and hi < lo:
            errs["benefit_amount_max"] = "Maximum must be at least the minimum."
        if data.get("opens_on") and data.get("deadline") and data["deadline"] < data["opens_on"]:
            errs["deadline"] = "Deadline can't be before the opening date."
        if not data.get("deadline") and not data.get("is_rolling"):
            errs["deadline"] = "Enter a deadline or mark it as rolling."
        if errs:
            raise ValidationError(errs)


class StatusIn(Schema):
    action = fields.String(required=True, validate=validate.OneOf(
        ("verify", "mark_pending", "expire", "archive", "publish", "unpublish")))
    notes = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=2000))
    source_url_checked = fields.Url(load_default=None, allow_none=True, schemes={"http", "https"})


class CategoryIn(Schema):
    name = fields.String(required=True, validate=validate.Length(min=2, max=80))
    slug = fields.String(required=True, validate=validate.Regexp(r"^[a-z0-9-]{2,60}$"))
    description = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=300))
    icon = fields.String(load_default="sparkles", validate=validate.Length(max=40))
    color = fields.String(load_default="lavender", validate=validate.Length(max=20))
    sort_order = fields.Integer(load_default=0)
    is_active = fields.Boolean(load_default=True)


class UserPatch(Schema):
    role = fields.String(validate=validate.OneOf(enums.USER_ROLES))
    is_active = fields.Boolean()


class CorrectionPatch(Schema):
    status = fields.String(required=True, validate=validate.OneOf(("accepted", "rejected", "open")))
    admin_note = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=2000))


class AnnouncementIn(Schema):
    title = fields.String(required=True, validate=validate.Length(min=3, max=160))
    body = fields.String(required=True, validate=validate.Length(min=3, max=2000))
    audience = fields.String(load_default="all", validate=validate.OneOf(enums.ANNOUNCEMENT_AUDIENCES))
    level = fields.String(load_default="info", validate=validate.OneOf(enums.ANNOUNCEMENT_LEVELS))
    starts_at = fields.AwareDateTime(load_default=None, allow_none=True)
    ends_at = fields.AwareDateTime(load_default=None, allow_none=True)
    is_active = fields.Boolean(load_default=True)


def _slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:150] or "opportunity"


def _get_opp(oid) -> Opportunity:
    o = db.session.scalars(sa.select(Opportunity).where(Opportunity.id == oid).options(
        selectinload(Opportunity.criteria), selectinload(Opportunity.required_documents),
        selectinload(Opportunity.dates), selectinload(Opportunity.states))).first()
    if o is None:
        raise not_found("Opportunity")
    return o


def _log(o, action, from_status=None, to_status=None, notes=None, url=None):
    db.session.add(SourceVerificationLog(opportunity_id=o.id, actor_id=current_user().id, action=action,
                                         from_status=from_status, to_status=to_status, notes=notes,
                                         source_url_checked=url))


def _apply(o: Opportunity, data: dict) -> None:
    """Write the payload onto an opportunity, rebuilding children and deriving audience tags from criteria."""
    with db.session.no_autoflush:
        _apply_fields(o, data)
    db.session.add(o)
    db.session.flush()
    _sync_education_levels(o, data)


def _apply_fields(o: Opportunity, data: dict) -> None:
    if db.session.get(Category, data["category_id"]) is None:
        raise APIError("Unknown category.", 422, "validation_error", {"category_id": "Invalid."})
    if data.get("organization_id"):
        if db.session.get(Organization, data["organization_id"]) is None:
            raise APIError("Unknown organisation.", 422, "validation_error", {"organization_id": "Invalid."})
        o.organization_id = data["organization_id"]
    else:
        name = data["organization_name"].strip()
        org = db.session.scalar(sa.select(Organization).where(Organization.name == name))
        if org is None:
            org = Organization(name=name, org_type=data["organization_type"])
            db.session.add(org)
            db.session.flush()
        o.organization_id = org.id

    slug = data.get("slug") or _slugify(data["title"])
    clash = db.session.scalar(sa.select(Opportunity.id).where(Opportunity.slug == slug, Opportunity.id != (o.id or 0)))
    if clash:
        raise APIError("Another opportunity already uses this URL slug.", 409, "duplicate", {"slug": "Already used."})
    o.slug = slug

    for k in ("title", "summary", "description", "category_id", "scope", "eligibility_summary", "benefits",
              "benefit_amount_min", "benefit_amount_max", "benefit_frequency", "application_mode", "how_to_apply",
              "official_url", "apply_url", "source_url", "opens_on", "deadline", "is_rolling", "deadline_note",
              "data_origin", "is_featured"):
        setattr(o, k, data[k])
    if o.data_origin == "demo" and o.verification_status == "verified":
        o.verification_status, o.last_verified_at = "pending_verification", None

    doc_ids = {d["document_type_id"] for d in data["required_documents"]}
    known = set(db.session.scalars(sa.select(DocumentType.id).where(DocumentType.id.in_(doc_ids))))
    if doc_ids - known:
        raise APIError("Unknown document type in required documents.", 422, "validation_error")
    if len(doc_ids) != len(data["required_documents"]):
        raise APIError("Each document type can only be listed once.", 422, "validation_error")

    o.criteria = [EligibilityCriterion(sort_order=i, **c) for i, c in enumerate(data["criteria"])]
    o.required_documents = [RequiredDocument(**d) for d in data["required_documents"]]
    o.dates = [OpportunityDate(label=d["label"], event_date=d["date"], note=d["note"]) for d in data["dates"]]

    # Audience tags + income ceiling are derived from the criteria -> one source of truth.
    states, levels, ceilings = set(), set(), []
    for c in data["criteria"]:
        if c["criterion_type"] == "state_domicile":
            states |= set(c["value"].get("any_of", []))
        elif c["criterion_type"] == "education_level":
            levels |= {v for v in c["value"].get("any_of", []) if v in enums.EDUCATION_LEVELS}
        elif c["criterion_type"] == "income_max" and c["value"].get("amount"):
            ceilings.append(c["value"]["amount"])
    o.states = db.session.scalars(sa.select(State).where(State.code.in_(states))).all() if states else []
    o.income_ceiling = min(ceilings) if ceilings else None


def _sync_education_levels(o: Opportunity, data: dict) -> None:
    levels = {v for c in data["criteria"] if c["criterion_type"] == "education_level"
              for v in c["value"].get("any_of", []) if v in enums.EDUCATION_LEVELS}
    db.session.execute(sa.delete(opportunity_education_levels).where(opportunity_education_levels.c.opportunity_id == o.id))
    if levels:
        db.session.execute(opportunity_education_levels.insert(),
                           [{"opportunity_id": o.id, "education_level": lv} for lv in sorted(levels)])


# ------------------------------------------------------------------ stats
@bp.get("/stats")
@admin_required
def stats():
    count = lambda q: db.session.scalar(q) or 0  # noqa: E731
    week_ago = utcnow() - timedelta(days=7)
    by_ver = dict(db.session.execute(sa.select(Opportunity.verification_status, sa.func.count()).group_by(
        Opportunity.verification_status)).all())
    by_app = dict(db.session.execute(sa.select(Application.status, sa.func.count()).group_by(Application.status)).all())
    top = db.session.execute(sa.select(Opportunity.title, sa.func.count(SavedOpportunity.id).label("n")).join(
        SavedOpportunity).group_by(Opportunity.id, Opportunity.title).order_by(sa.desc("n")).limit(5)).all()
    stale = count(sa.select(sa.func.count(Opportunity.id)).where(
        Opportunity.verification_status == "verified",
        Opportunity.last_verified_at < utcnow() - timedelta(days=30)))
    return jsonify(
        users={"total": count(sa.select(sa.func.count(User.id))),
               "new_7d": count(sa.select(sa.func.count(User.id)).where(User.created_at >= week_ago)),
               "admins": count(sa.select(sa.func.count(User.id)).where(User.role == "admin"))},
        opportunities={"total": count(sa.select(sa.func.count(Opportunity.id))),
                       "published": count(sa.select(sa.func.count(Opportunity.id)).where(Opportunity.publication_status == "published")),
                       "by_verification": by_ver, "stale_verification": stale,
                       "demo": count(sa.select(sa.func.count(Opportunity.id)).where(Opportunity.data_origin == "demo"))},
        applications={"total": sum(by_app.values()), "by_status": by_app},
        saved=count(sa.select(sa.func.count(SavedOpportunity.id))),
        documents=count(sa.select(sa.func.count(UploadedDocument.id)).where(UploadedDocument.deleted_at.is_(None))),
        ai_messages=count(sa.select(sa.func.count(ChatMessage.id)).where(ChatMessage.role == "user")),
        open_corrections=count(sa.select(sa.func.count(CorrectionReport.id)).where(CorrectionReport.status == "open")),
        new_feedback=count(sa.select(sa.func.count(Feedback.id)).where(Feedback.status == "new")),
        top_saved=[{"title": t, "count": n} for t, n in top],
    )


# ------------------------------------------------------------------ opportunities
@bp.get("/opportunities")
@admin_required
def list_opps():
    q = sa.select(Opportunity).options(selectinload(Opportunity.category), selectinload(Opportunity.organization),
                                       selectinload(Opportunity.states))
    if request.args.get("q"):
        q = q.where(Opportunity.title.ilike(f"%{request.args['q'][:100]}%"))
    for f in ("verification_status", "publication_status", "data_origin"):
        if request.args.get(f):
            q = q.where(getattr(Opportunity, f) == request.args[f])
    if request.args.get("queue") == "stale":
        q = q.where(Opportunity.verification_status == "verified",
                    Opportunity.last_verified_at < utcnow() - timedelta(days=30))
    q = q.order_by(Opportunity.updated_at.desc(), Opportunity.id.desc())
    return jsonify(paginate(q, int_arg("page", 1, 1, 1000), int_arg("per_page", 20, 1, 100), db, opportunity_card))


@bp.post("/opportunities")
@admin_required
def create_opp():
    data = body(OpportunityIn())
    o = Opportunity(created_by_id=current_user().id, updated_by_id=current_user().id)
    _apply(o, data)
    _log(o, "marked_pending", None, "pending_verification", "Created")
    db.session.commit()
    return jsonify(opportunity=opportunity_detail(_get_opp(o.id))), 201


@bp.get("/opportunities/<int:oid>")
@admin_required
def get_opp(oid):
    o = _get_opp(oid)
    d = opportunity_detail(o)
    d["logs"] = [{"action": l.action, "from_status": l.from_status, "to_status": l.to_status, "notes": l.notes,
                  "source_url_checked": l.source_url_checked, "created_at": iso(l.created_at),
                  "actor": (db.session.get(User, l.actor_id).email if l.actor_id and db.session.get(User, l.actor_id) else "system")}
                 for l in db.session.scalars(sa.select(SourceVerificationLog).where(
                     SourceVerificationLog.opportunity_id == o.id).order_by(SourceVerificationLog.created_at.desc(), SourceVerificationLog.id.desc()))]
    d["education_levels"] = list(db.session.scalars(sa.select(opportunity_education_levels.c.education_level).where(
        opportunity_education_levels.c.opportunity_id == o.id)))
    return jsonify(opportunity=d)


@bp.put("/opportunities/<int:oid>")
@admin_required
def update_opp(oid):
    o = _get_opp(oid)
    data = body(OpportunityIn())
    old_source = o.source_url
    _apply(o, data)
    o.updated_by_id = current_user().id
    if old_source != o.source_url and o.verification_status == "verified":
        _log(o, "source_updated", "verified", "pending_verification", "Source URL changed; needs re-verification.")
        o.verification_status, o.last_verified_at = "pending_verification", None
        if o.data_origin == "official":
            o.publication_status = "unpublished"
    db.session.commit()
    return jsonify(opportunity=opportunity_detail(_get_opp(o.id)))


@bp.post("/opportunities/<int:oid>/status")
@admin_required
def change_status(oid):
    o = _get_opp(oid)
    data = body(StatusIn())
    action, before = data["action"], o.verification_status
    if action == "verify":
        if o.data_origin == "demo":
            raise APIError("Demo data can't be marked as verified.", 409, "demo_not_verifiable")
        o.verification_status, o.last_verified_at, o.verified_by_id = "verified", utcnow(), current_user().id
        _log(o, "verified", before, "verified", data["notes"], data["source_url_checked"] or o.source_url)
    elif action == "mark_pending":
        o.verification_status = "pending_verification"
        _log(o, "marked_pending", before, "pending_verification", data["notes"])
    elif action == "expire":
        o.verification_status = "expired"
        _log(o, "marked_expired", before, "expired", data["notes"])
    elif action == "archive":
        o.verification_status, o.publication_status, o.archived_at = "archived", "unpublished", utcnow()
        _log(o, "archived", before, "archived", data["notes"])
    elif action == "publish":
        if o.data_origin == "official" and o.verification_status != "verified":
            raise APIError("Verify the official source before publishing.", 409, "needs_verification")
        if o.verification_status == "archived":
            raise APIError("Archived opportunities can't be published.", 409, "archived")
        o.publication_status = "published"
        _log(o, "published", before, before, data["notes"])
    elif action == "unpublish":
        o.publication_status = "unpublished"
        _log(o, "unpublished", before, before, data["notes"])
    db.session.commit()
    return jsonify(opportunity=opportunity_card(o))


@bp.delete("/opportunities/<int:oid>")
@admin_required
def delete_opp(oid):
    o = _get_opp(oid)
    used = db.session.scalar(sa.select(sa.func.count(Application.id)).where(Application.opportunity_id == o.id)) + \
        db.session.scalar(sa.select(sa.func.count(SavedOpportunity.id)).where(SavedOpportunity.opportunity_id == o.id))
    if used:
        raise APIError("Users have saved or tracked this opportunity. Archive it instead of deleting.", 409, "in_use")
    db.session.delete(o)
    db.session.commit()
    return jsonify(ok=True)


@bp.put("/featured")
@admin_required
def set_featured():
    ids = (request.get_json(silent=True) or {}).get("ids", [])
    if not isinstance(ids, list) or not all(isinstance(i, int) for i in ids) or len(ids) > 12:
        raise APIError("Send up to 12 opportunity ids in order.", 422, "validation_error")
    db.session.execute(sa.update(Opportunity).values(is_featured=False, featured_rank=None))
    for rank, oid in enumerate(ids, start=1):
        db.session.execute(sa.update(Opportunity).where(Opportunity.id == oid).values(is_featured=True, featured_rank=rank))
    db.session.commit()
    return jsonify(ok=True)


@bp.get("/organizations")
@admin_required
def organizations():
    rows = db.session.scalars(sa.select(Organization).order_by(Organization.name)).all()
    return jsonify(items=[organization_dict(o) for o in rows])


# ------------------------------------------------------------------ categories
@bp.get("/categories")
@admin_required
def list_categories():
    counts = dict(db.session.execute(sa.select(Opportunity.category_id, sa.func.count()).group_by(Opportunity.category_id)).all())
    rows = db.session.scalars(sa.select(Category).order_by(Category.sort_order)).all()
    return jsonify(items=[{**category_dict(c), "count": counts.get(c.id, 0)} for c in rows])


@bp.post("/categories")
@admin_required
def create_category():
    data = body(CategoryIn())
    if db.session.scalar(sa.select(Category.id).where(sa.or_(Category.slug == data["slug"], Category.name == data["name"]))):
        raise APIError("A category with this name or slug exists.", 409, "duplicate")
    c = Category(**data)
    db.session.add(c)
    db.session.commit()
    return jsonify(category=category_dict(c)), 201


@bp.put("/categories/<int:cid>")
@admin_required
def update_category(cid):
    c = db.session.get(Category, cid)
    if c is None:
        raise not_found("Category")
    data = body(CategoryIn())
    if db.session.scalar(sa.select(Category.id).where(
            sa.or_(Category.slug == data["slug"], Category.name == data["name"]), Category.id != cid)):
        raise APIError("A category with this name or slug exists.", 409, "duplicate")
    for k, v in data.items():
        setattr(c, k, v)
    db.session.commit()
    return jsonify(category=category_dict(c))


@bp.delete("/categories/<int:cid>")
@admin_required
def delete_category(cid):
    c = db.session.get(Category, cid)
    if c is None:
        raise not_found("Category")
    if db.session.scalar(sa.select(sa.func.count(Opportunity.id)).where(Opportunity.category_id == cid)):
        raise APIError("This category has opportunities. Deactivate it instead.", 409, "in_use")
    db.session.delete(c)
    db.session.commit()
    return jsonify(ok=True)


# ------------------------------------------------------------------ users
@bp.get("/users")
@admin_required
def list_users():
    q = sa.select(User)
    if request.args.get("q"):
        q = q.where(User.email.ilike(f"%{request.args['q'][:100].lower()}%"))
    if request.args.get("role") in enums.USER_ROLES:
        q = q.where(User.role == request.args["role"])
    q = q.order_by(User.created_at.desc(), User.id.desc())
    ser = lambda u: {"id": u.id, "email": u.email, "role": u.role, "is_active": u.is_active,  # noqa: E731
                     "full_name": u.profile.full_name if u.profile else None, "created_at": iso(u.created_at),
                     "last_login_at": iso(u.last_login_at),
                     "onboarding_completed": bool(u.profile and u.profile.onboarding_completed_at)}
    return jsonify(paginate(q, int_arg("page", 1, 1, 1000), int_arg("per_page", 20, 1, 100), db, ser))


@bp.patch("/users/<int:uid>")
@admin_required
def patch_user(uid):
    u = db.session.get(User, uid)
    if u is None:
        raise not_found("User")
    data = body(UserPatch(), partial=True)
    if u.id == current_user().id and (data.get("role") == "user" or data.get("is_active") is False):
        raise APIError("You can't demote or deactivate your own account.", 409, "self_change")
    for k, v in data.items():
        setattr(u, k, v)
    db.session.commit()
    return jsonify(ok=True, user={"id": u.id, "role": u.role, "is_active": u.is_active})


# ------------------------------------------------------------------ corrections & feedback
@bp.get("/corrections")
@admin_required
def list_corrections():
    q = sa.select(CorrectionReport)
    if request.args.get("status") in enums.CORRECTION_STATUSES:
        q = q.where(CorrectionReport.status == request.args["status"])
    q = q.order_by(CorrectionReport.created_at.desc(), CorrectionReport.id.desc())
    return jsonify(paginate(q, int_arg("page", 1, 1, 1000), 20, db, correction_dict))


@bp.patch("/corrections/<int:cid>")
@admin_required
def review_correction(cid):
    c = db.session.get(CorrectionReport, cid)
    if c is None:
        raise not_found("Correction")
    data = body(CorrectionPatch())
    c.status, c.admin_note = data["status"], data["admin_note"]
    c.reviewed_by_id, c.reviewed_at = current_user().id, utcnow()
    if c.user_id and data["status"] != "open":
        reporter = db.session.get(User, c.user_id)
        verdict = "accepted — thank you!" if data["status"] == "accepted" else "reviewed"
        notify.push(reporter, "correction_update", f"Your correction for {c.opportunity.title} was {verdict}",
                    data["admin_note"], f"/app/opportunities/{c.opportunity.slug}", f"correction:{c.id}:{data['status']}")
    db.session.commit()
    return jsonify(correction=correction_dict(c))


@bp.get("/feedback")
@admin_required
def list_feedback():
    q = sa.select(Feedback).order_by(Feedback.created_at.desc(), Feedback.id.desc())
    ser = lambda f: {"id": f.id, "kind": f.kind, "message": f.message, "page": f.page, "status": f.status,  # noqa: E731
                     "contact_email": f.contact_email, "user_id": f.user_id, "created_at": iso(f.created_at)}
    return jsonify(paginate(q, int_arg("page", 1, 1, 1000), 20, db, ser))


@bp.patch("/feedback/<int:fid>")
@admin_required
def patch_feedback(fid):
    f = db.session.get(Feedback, fid)
    if f is None:
        raise not_found("Feedback")
    status = (request.get_json(silent=True) or {}).get("status")
    if status not in enums.FEEDBACK_STATUSES:
        raise APIError("Invalid status.", 422, "validation_error")
    f.status = status
    db.session.commit()
    return jsonify(ok=True)


# ------------------------------------------------------------------ announcements
def _ann(a):
    return {"id": a.id, "title": a.title, "body": a.body, "audience": a.audience, "level": a.level,
            "starts_at": iso(a.starts_at), "ends_at": iso(a.ends_at), "is_active": a.is_active, "created_at": iso(a.created_at)}


@bp.get("/announcements")
@admin_required
def list_announcements():
    return jsonify(items=[_ann(a) for a in db.session.scalars(sa.select(Announcement).order_by(Announcement.created_at.desc()))])


@bp.post("/announcements")
@admin_required
def create_announcement():
    a = Announcement(created_by_id=current_user().id, **body(AnnouncementIn()))
    if a.starts_at and a.ends_at and a.ends_at <= a.starts_at:
        raise APIError("End must be after start.", 422, "validation_error", {"ends_at": "Must be after start."})
    db.session.add(a)
    db.session.commit()
    return jsonify(announcement=_ann(a)), 201


@bp.put("/announcements/<int:aid>")
@admin_required
def update_announcement(aid):
    a = db.session.get(Announcement, aid)
    if a is None:
        raise not_found("Announcement")
    for k, v in body(AnnouncementIn()).items():
        setattr(a, k, v)
    db.session.commit()
    return jsonify(announcement=_ann(a))


@bp.delete("/announcements/<int:aid>")
@admin_required
def delete_announcement(aid):
    a = db.session.get(Announcement, aid)
    if a is None:
        raise not_found("Announcement")
    db.session.delete(a)
    db.session.commit()
    return jsonify(ok=True)
