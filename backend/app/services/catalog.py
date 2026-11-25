"""Opportunity queries: public listing filters, recommendations, user context."""
from __future__ import annotations

from datetime import date, timedelta

import sqlalchemy as sa
from sqlalchemy.orm import selectinload

from ..extensions import db
from ..models import (
    Application, Category, Opportunity, SavedOpportunity, opportunity_education_levels, opportunity_states,
)
from ..models.base import INCOME_RANGES
from . import eligibility

INCOME_LOWER = {"below_1l": 0, "1l_to_2_5l": 100_000, "2_5l_to_5l": 250_000, "5l_to_8l": 500_000, "above_8l": 800_000}
CARD_LOAD = (selectinload(Opportunity.category), selectinload(Opportunity.organization), selectinload(Opportunity.states))


def open_clause():
    return sa.and_(
        Opportunity.verification_status.notin_(("expired", "archived")),
        sa.or_(Opportunity.deadline.is_(None), Opportunity.deadline >= date.today()),
    )


def public_query():
    """Everything an ordinary user may see: published and not archived."""
    return (
        sa.select(Opportunity)
        .where(Opportunity.publication_status == "published", Opportunity.verification_status != "archived")
        .options(*CARD_LOAD)
    )


def user_context(user) -> tuple[set, dict]:
    if user is None:
        return set(), {}
    saved = set(db.session.scalars(sa.select(SavedOpportunity.opportunity_id).where(SavedOpportunity.user_id == user.id)))
    apps = dict(db.session.execute(
        sa.select(Application.opportunity_id, Application.status).where(Application.user_id == user.id)
    ).all())
    return saved, apps


def filtered_query(args, user=None):
    q = public_query()
    text = (args.get("q") or "").strip()[:100]
    if text:
        like = f"%{text}%"
        q = q.join(Opportunity.organization).where(sa.or_(
            Opportunity.title.ilike(like), Opportunity.summary.ilike(like),
            Opportunity.eligibility_summary.ilike(like), Opportunity.benefits.ilike(like),
            sa.literal_column("organizations.name").ilike(like),
        ))
    if args.get("category"):
        cats = [c for c in args.get("category").split(",") if c]
        q = q.where(Opportunity.category_id.in_(sa.select(Category.id).where(Category.slug.in_(cats))))
    if args.get("education"):
        level = args.get("education")
        tagged = sa.select(opportunity_education_levels.c.opportunity_id)
        matching = tagged.where(opportunity_education_levels.c.education_level == level)
        q = q.where(sa.or_(Opportunity.id.in_(matching), Opportunity.id.notin_(tagged)))
    if args.get("state"):
        matching = sa.select(opportunity_states.c.opportunity_id).where(opportunity_states.c.state_code == args.get("state"))
        q = q.where(sa.or_(Opportunity.scope == "national", Opportunity.id.in_(matching)))
    if args.get("income") in INCOME_LOWER:
        q = q.where(sa.or_(Opportunity.income_ceiling.is_(None), Opportunity.income_ceiling >= INCOME_LOWER[args.get("income")]))
    if args.get("origin") in ("official", "demo"):
        q = q.where(Opportunity.data_origin == args.get("origin"))
    if args.get("verified") == "1":
        q = q.where(Opportunity.verification_status == "verified")

    status = args.get("status", "open")
    if status == "open":
        q = q.where(open_clause())
    elif status == "closing_soon":
        q = q.where(open_clause(), Opportunity.deadline.is_not(None), Opportunity.deadline <= date.today() + timedelta(days=14))
    elif status == "closed":
        q = q.where(sa.not_(open_clause()))

    deadline_days = args.get("deadline_within")
    if deadline_days and deadline_days.isdigit():
        q = q.where(Opportunity.deadline.is_not(None), Opportunity.deadline <= date.today() + timedelta(days=int(deadline_days)))

    mine = args.get("mine")
    if user is not None and mine in ("saved", "tracked", "not_tracked"):
        saved_q = sa.select(SavedOpportunity.opportunity_id).where(SavedOpportunity.user_id == user.id)
        apps_q = sa.select(Application.opportunity_id).where(Application.user_id == user.id)
        if mine == "saved":
            q = q.where(Opportunity.id.in_(saved_q))
        elif mine == "tracked":
            q = q.where(Opportunity.id.in_(apps_q))
        else:
            q = q.where(Opportunity.id.notin_(apps_q))

    sort = args.get("sort", "relevance")
    if sort == "deadline":
        q = q.order_by(Opportunity.deadline.asc().nulls_last(), Opportunity.id)
    elif sort == "recent":
        q = q.order_by(Opportunity.created_at.desc(), Opportunity.id.desc())
    else:
        rank = sa.case((Opportunity.title.ilike(f"%{text}%"), 0), else_=1) if text else sa.literal(0)
        q = q.order_by(rank, Opportunity.is_featured.desc(), Opportunity.featured_rank.asc().nulls_last(),
                       Opportunity.deadline.asc().nulls_last(), Opportunity.id)
    return q


def recommend(user, limit: int = 6) -> list[dict]:
    """Rule-based, explainable recommendations. Never recommends closed or not-eligible items."""
    profile = user.profile
    q = public_query().where(open_clause()).options(selectinload(Opportunity.criteria))
    candidates = db.session.scalars(q).unique().all()
    interest_ids = {c.id for c in profile.interests} if profile else set()
    _, apps = user_context(user)
    scored = []
    for o in candidates:
        if o.id in apps:  # already tracking it
            continue
        report = eligibility.evaluate(profile, o.criteria)
        if report["verdict"] == "not_eligible":
            continue
        score, reasons = 0, []
        if report["verdict"] == "eligible":
            score += 4
            reasons.append("You meet all checkable rules")
        else:
            score += 1
        if o.category_id in interest_ids:
            score += 3
            reasons.append(f"You're interested in {o.category.name}")
        if profile and profile.state_code and profile.state_code in {s.code for s in o.states}:
            score += 2
            reasons.append("For your state")
        if o.deadline and 0 <= (o.deadline - date.today()).days <= 30:
            score += 1
            reasons.append("Deadline coming up")
        if o.is_featured:
            score += 1
        scored.append((score, o, report["verdict"], reasons[:3]))
    scored.sort(key=lambda t: (-t[0], t[1].deadline or date.max))
    return [(o, verdict, reasons) for _, o, verdict, reasons in scored[:limit]]
