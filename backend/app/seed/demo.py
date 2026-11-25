"""Demo opportunities for automated tests only (backend/tests/fixtures/demo_data.json).
Always data_origin='demo', never verified. Real users see shared/opportunities.json instead."""
import json
from datetime import date, timedelta
from pathlib import Path

import sqlalchemy as sa

from ..extensions import db
from ..models import (
    Category, DocumentType, EligibilityCriterion, Opportunity, OpportunityDate, Organization, RequiredDocument,
    State, opportunity_education_levels,
)
from .reference import seed_reference

FIXTURE = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "demo_data.json"


def seed_demo(reset: bool = False, path: Path = FIXTURE) -> int:
    seed_reference()
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if reset:
        purge_demo()

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
    created = 0
    for rank, item in enumerate(data["opportunities"], start=1):
        if db.session.scalar(sa.select(Opportunity.id).where(Opportunity.slug == item["slug"])):
            continue
        offset = lambda k: today + timedelta(days=item[k]) if item.get(k) is not None else None  # noqa: E731
        deadline = offset("deadline_in_days")
        o = Opportunity(
            slug=item["slug"], title=item["title"], summary=item["summary"], description=item["description"],
            category_id=cats[item["category"]].id, organization_id=orgs[item["org"]].id, scope=item["scope"],
            eligibility_summary=item["eligibility_summary"], benefits=item["benefits"],
            benefit_amount_min=item.get("benefit_amount_min"), benefit_amount_max=item.get("benefit_amount_max"),
            benefit_frequency=item.get("benefit_frequency"), application_mode=item["application_mode"],
            how_to_apply=item["how_to_apply"],
            official_url=f"https://example.org/formsaathi-demo/{item['slug']}",
            apply_url=f"https://example.org/formsaathi-demo/{item['slug']}/apply",
            source_url=f"https://example.org/formsaathi-demo/{item['slug']}/notification",
            opens_on=offset("opens_in_days"), deadline=deadline, is_rolling=item.get("is_rolling", False),
            deadline_note=item.get("deadline_note"), data_origin="demo", publication_status="published",
            verification_status="expired" if deadline and deadline < today else "pending_verification",
            is_featured=item.get("is_featured", False), featured_rank=rank if item.get("is_featured") else None,
        )
        o.criteria = [EligibilityCriterion(criterion_type=c["type"], value=c["value"], description=c["description"],
                                           source_excerpt=c.get("excerpt"), is_mandatory=c.get("mandatory", True),
                                           sort_order=i) for i, c in enumerate(item["criteria"])]
        o.required_documents = [RequiredDocument(document_type_id=docs[d["type"]].id, is_mandatory=d.get("mandatory", True),
                                                 notes=d.get("notes")) for d in item["documents"]]
        o.dates = [OpportunityDate(label=d["label"], event_date=today + timedelta(days=d["in_days"])) for d in item["dates"]]
        states = {s for c in item["criteria"] if c["type"] == "state_domicile" for s in c["value"]["any_of"]}
        o.states = db.session.scalars(sa.select(State).where(State.code.in_(states))).all() if states else []
        ceilings = [c["value"]["amount"] for c in item["criteria"] if c["type"] == "income_max"]
        o.income_ceiling = min(ceilings) if ceilings else None
        db.session.add(o)
        db.session.flush()
        levels = {lv for c in item["criteria"] if c["type"] == "education_level" for lv in c["value"]["any_of"]}
        if levels:
            db.session.execute(opportunity_education_levels.insert(),
                               [{"opportunity_id": o.id, "education_level": lv} for lv in sorted(levels)])
        created += 1
    db.session.commit()
    return created


def purge_demo() -> int:
    rows = db.session.scalars(sa.select(Opportunity).where(Opportunity.data_origin == "demo")).all()
    for o in rows:
        db.session.delete(o)
    db.session.commit()
    return len(rows)
