"""Discovery: listing, detail, featured, recommended, compare, corrections. Plus saved & collections."""
import sqlalchemy as sa
from flask import Blueprint, jsonify, request
from marshmallow import Schema, fields, validate
from sqlalchemy.orm import selectinload

from ..extensions import db, limiter
from ..models import Collection, CorrectionReport, Opportunity, SavedOpportunity
from ..models.base import CORRECTION_FIELDS
from ..serializers import collection_dict, opportunity_card, opportunity_detail
from ..services import catalog
from ..utils.auth import current_user, login_required, optional_user
from ..utils.errors import APIError, not_found
from ..utils.helpers import body, int_arg, paginate

bp = Blueprint("opportunities", __name__, url_prefix="/api/v1")


class CorrectionSchema(Schema):
    field = fields.String(required=True, validate=validate.OneOf(CORRECTION_FIELDS))
    message = fields.String(required=True, validate=validate.Length(min=10, max=2000))
    suggested_source_url = fields.Url(load_default=None, schemes={"http", "https"})


class SaveSchema(Schema):
    opportunity_id = fields.Integer(required=True)
    collection_id = fields.Integer(load_default=None, allow_none=True)


class CollectionSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=60))


def _visible(opportunity_id=None, slug=None) -> Opportunity:
    q = catalog.public_query().options(
        selectinload(Opportunity.criteria), selectinload(Opportunity.required_documents), selectinload(Opportunity.dates))
    q = q.where(Opportunity.id == opportunity_id) if opportunity_id else q.where(Opportunity.slug == slug)
    o = db.session.scalars(q).first()
    if o is None:
        raise not_found("Opportunity")
    return o


@bp.get("/opportunities")
def list_opportunities():
    user = optional_user()
    saved, apps = catalog.user_context(user)
    q = catalog.filtered_query(request.args, user)
    return jsonify(paginate(q, int_arg("page", 1, 1, 1000), int_arg("per_page", 12, 1, 48), db,
                            lambda o: opportunity_card(o, saved, apps)))


@bp.get("/opportunities/featured")
def featured():
    user = optional_user()
    saved, apps = catalog.user_context(user)
    q = catalog.public_query().where(catalog.open_clause(), Opportunity.is_featured.is_(True)).order_by(
        Opportunity.featured_rank.asc().nulls_last(), Opportunity.deadline.asc().nulls_last()).limit(6)
    return jsonify(items=[opportunity_card(o, saved, apps) for o in db.session.scalars(q).unique()])


@bp.get("/opportunities/recommended")
@login_required
def recommended():
    user = current_user()
    saved, apps = catalog.user_context(user)
    items = []
    for o, verdict, reasons in catalog.recommend(user, int_arg("limit", 6, 1, 20)):
        card = opportunity_card(o, saved, apps)
        card.update(match={"verdict": verdict, "reasons": reasons})
        items.append(card)
    return jsonify(items=items)


@bp.get("/opportunities/compare")
def compare():
    try:
        ids = [int(x) for x in request.args.get("ids", "").split(",") if x.strip()][:3]
    except ValueError:
        raise APIError("ids must be numbers.", 400)
    user = optional_user()
    saved, apps = catalog.user_context(user)
    return jsonify(items=[opportunity_detail(_visible(opportunity_id=i), saved, apps) for i in ids])


@bp.get("/opportunities/<slug>")
def detail(slug):
    user = optional_user()
    saved, apps = catalog.user_context(user)
    o = _visible(slug=slug)
    data = opportunity_detail(o, saved, apps)
    similar = db.session.scalars(catalog.public_query().where(
        catalog.open_clause(), Opportunity.category_id == o.category_id, Opportunity.id != o.id).limit(3)).unique()
    data["similar"] = [opportunity_card(s, saved, apps) for s in similar]
    return jsonify(opportunity=data)


@bp.post("/opportunities/<int:opportunity_id>/corrections")
@login_required
@limiter.limit("10 per hour")
def report_correction(opportunity_id):
    o = _visible(opportunity_id=opportunity_id)
    data = body(CorrectionSchema())
    db.session.add(CorrectionReport(opportunity_id=o.id, user_id=current_user().id, **data))
    db.session.commit()
    return jsonify(message="Thanks! Our team will review this and update the listing if needed."), 201


# ------------------------------------------------------------------ saved & collections
@bp.get("/saved")
@login_required
def list_saved():
    user = current_user()
    q = sa.select(SavedOpportunity).where(SavedOpportunity.user_id == user.id)
    if request.args.get("collection_id"):
        q = q.where(SavedOpportunity.collection_id == int_arg("collection_id", 0, 0, 10**9))
    rows = db.session.scalars(q.order_by(SavedOpportunity.created_at.desc())).all()
    saved, apps = catalog.user_context(user)
    items = []
    for s in rows:
        card = opportunity_card(s.opportunity, saved, apps)
        card.update(saved_at=s.created_at.isoformat() if s.created_at else None, collection_id=s.collection_id)
        items.append(card)
    return jsonify(items=items)


def _own_collection(collection_id):
    if collection_id is None:
        return None
    c = db.session.get(Collection, collection_id)
    if c is None or c.user_id != current_user().id:
        raise not_found("Collection")
    return c


@bp.post("/saved")
@login_required
def save():
    data = body(SaveSchema())
    user = current_user()
    o = _visible(opportunity_id=data["opportunity_id"])
    _own_collection(data["collection_id"])
    row = db.session.scalar(sa.select(SavedOpportunity).where(
        SavedOpportunity.user_id == user.id, SavedOpportunity.opportunity_id == o.id))
    if row is None:
        row = SavedOpportunity(user_id=user.id, opportunity_id=o.id, collection_id=data["collection_id"])
        db.session.add(row)
    else:
        row.collection_id = data["collection_id"]
    db.session.commit()
    return jsonify(saved=True, opportunity_id=o.id, collection_id=row.collection_id), 201


@bp.delete("/saved/<int:opportunity_id>")
@login_required
def unsave(opportunity_id):
    db.session.execute(sa.delete(SavedOpportunity).where(
        SavedOpportunity.user_id == current_user().id, SavedOpportunity.opportunity_id == opportunity_id))
    db.session.commit()
    return jsonify(saved=False, opportunity_id=opportunity_id)


@bp.get("/collections")
@login_required
def list_collections():
    user = current_user()
    counts = dict(db.session.execute(sa.select(SavedOpportunity.collection_id, sa.func.count()).where(
        SavedOpportunity.user_id == user.id).group_by(SavedOpportunity.collection_id)).all())
    rows = db.session.scalars(sa.select(Collection).where(Collection.user_id == user.id).order_by(Collection.name)).all()
    return jsonify(items=[collection_dict(c, counts.get(c.id, 0)) for c in rows], uncategorised=counts.get(None, 0))


@bp.post("/collections")
@login_required
def create_collection():
    data = body(CollectionSchema())
    user = current_user()
    name = data["name"].strip()
    if db.session.scalar(sa.select(Collection.id).where(Collection.user_id == user.id, Collection.name == name)):
        raise APIError("You already have a collection with this name.", 409, "duplicate", {"name": "Already exists."})
    c = Collection(user_id=user.id, name=name)
    db.session.add(c)
    db.session.commit()
    return jsonify(collection=collection_dict(c)), 201


@bp.patch("/collections/<int:collection_id>")
@login_required
def rename_collection(collection_id):
    c = _own_collection(collection_id)
    c.name = body(CollectionSchema())["name"].strip()
    db.session.commit()
    return jsonify(collection=collection_dict(c))


@bp.delete("/collections/<int:collection_id>")
@login_required
def delete_collection(collection_id):
    c = _own_collection(collection_id)
    db.session.delete(c)  # saved items stay saved (collection_id -> NULL)
    db.session.commit()
    return jsonify(ok=True)
