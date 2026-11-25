"""Real opportunities from shared/opportunities.json (checked against official sources).

Each record is created as official + verified + published, with an audit-log row saying where
and when it was verified. Records whose deadline has passed are stored as expired.
Running it again is safe: existing slugs are skipped unless update=True.
"""
from datetime import date, datetime, timezone

import sqlalchemy as sa

from ..extensions import db
from ..models import (
    Category, DocumentType, EligibilityCriterion, Opportunity, OpportunityDate, Organization, RequiredDocument,
    SourceVerificationLog, State, opportunity_education_levels,
)
from .reference import load_shared, seed_reference


def _d(value):
    return date.fromisoformat(value) if value else None


def seed_opportunities(update: bool = False) -> dict:
    seed_reference()
    data = load_shared("opportunities.json")
    verified_on = date.fromisoformat(data["verified_on"])
    verified_at = datetime(verified_on.year, verified_on.month, verified_on.day, 12, 0, tzinfo=timezone.utc)

    orgs = {}
    for o in data["organizations"]:
        org = db.session.scalar(sa.select(Organization).where(Organization.name == o["name"]))
        if org is None:
            org = Organization(name=o["name"], org_type=o["org_type"], website=o["website"])
            db.session.add(org)
            db.session.flush()
        orgs[o["key"]] = org

    cats = {c.slug: c for c in db.session.scalars(sa.select(Category))}
    docs = {d.slug: d for d in db.session.scalars(sa.select(DocumentType))}
    today = date.today()
    result = {"created": 0, "updated": 0, "skipped": 0}

    for item in data["opportunities"]:
        o = db.session.scalar(sa.select(Opportunity).where(Opportunity.slug == item["slug"]))
        if o is not None and not update:
            result["skipped"] += 1
            continue
        is_new = o is None
        if is_new:
            o = Opportunity(slug=item["slug"])
        deadline = _d(item.get("deadline"))
        o.title, o.summary, o.description = item["title"], item["summary"], item["description"]
        o.category_id, o.organization_id = cats[item["category"]].id, orgs[item["org"]].id
        o.scope = item.get("scope", "national")
        o.eligibility_summary, o.benefits = item["eligibility_summary"], item["benefits"]
        o.benefit_amount_min, o.benefit_amount_max = item.get("benefit_amount_min"), item.get("benefit_amount_max")
        o.benefit_frequency = item.get("benefit_frequency")
        o.application_mode, o.how_to_apply = item.get("application_mode", "online"), item.get("how_to_apply")
        o.official_url, o.apply_url, o.source_url = item.get("official_url"), item.get("apply_url"), item["source_url"]
        o.opens_on, o.deadline = _d(item.get("opens_on")), deadline
        o.is_rolling, o.deadline_note = bool(item.get("rolling")), item.get("deadline_note")
        o.data_origin, o.publication_status = "official", "published"
        o.verification_status = "expired" if deadline and deadline < today else "verified"
        o.last_verified_at = verified_at
        o.is_featured, o.featured_rank = bool(item.get("featured")), item.get("featured")
        o.criteria = [
            EligibilityCriterion(criterion_type=c["type"], value=c.get("value") or {}, description=c["description"],
                                 source_excerpt=c.get("excerpt"), is_mandatory=c.get("mandatory", True), sort_order=i)
            for i, c in enumerate(item["criteria"])
        ]
        o.required_documents = [
            RequiredDocument(document_type_id=docs[d["type"]].id, is_mandatory=d.get("mandatory", True),
                             notes=d.get("notes"))
            for d in item["documents"]
        ]
        o.dates = [OpportunityDate(label=d["label"], event_date=_d(d["date"]), note=d.get("note")) for d in item["dates"]]
        ceilings = [c["value"]["amount"] for c in item["criteria"]
                    if c["type"] == "income_max" and c.get("mandatory", True)]
        o.income_ceiling = min(ceilings) if ceilings else None
        states = {s for c in item["criteria"] if c["type"] == "state_domicile" for s in c["value"]["any_of"]}
        o.states = db.session.scalars(sa.select(State).where(State.code.in_(states))).all() if states else []
        db.session.add(o)
        db.session.flush()

        db.session.execute(sa.delete(opportunity_education_levels).where(
            opportunity_education_levels.c.opportunity_id == o.id))
        levels = sorted({lv for c in item["criteria"] if c["type"] == "education_level" for lv in c["value"]["any_of"]})
        if levels:
            db.session.execute(opportunity_education_levels.insert(),
                               [{"opportunity_id": o.id, "education_level": lv} for lv in levels])
        db.session.add(SourceVerificationLog(
            opportunity_id=o.id, actor_id=None, action="verified", to_status=o.verification_status,
            source_url_checked=o.source_url,
            notes=f"Checked against the official source on {verified_on:%d %b %Y} while setting up FormSaathi."))
        result["created" if is_new else "updated"] += 1

    db.session.commit()
    return result
