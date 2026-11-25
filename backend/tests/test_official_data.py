"""The real, source-checked dataset in shared/opportunities.json."""
import json
from datetime import date
from pathlib import Path

import sqlalchemy as sa

from app.models import Opportunity, SourceVerificationLog
from app.models.base import CRITERION_TYPES
from app.seed.official import seed_opportunities

DATA = json.loads((Path(__file__).resolve().parents[2] / "shared" / "opportunities.json").read_text(encoding="utf-8"))


def test_dataset_is_well_formed():
    slugs = [o["slug"] for o in DATA["opportunities"]]
    assert len(slugs) == len(set(slugs)) and len(slugs) >= 15
    orgs = {o["key"] for o in DATA["organizations"]}
    for o in DATA["opportunities"]:
        assert o["org"] in orgs
        assert o["source_url"].startswith("https://"), o["slug"]
        assert "example.org" not in json.dumps(o), o["slug"]
        assert o.get("deadline") or o.get("rolling"), f"{o['slug']} needs a deadline or rolling"
        for c in o["criteria"]:
            assert c["type"] in CRITERION_TYPES


def test_seed_creates_verified_official_listings(db):
    result = seed_opportunities()
    assert result["created"] == len(DATA["opportunities"])
    rows = db.session.scalars(sa.select(Opportunity)).all()
    assert all(o.data_origin == "official" and o.publication_status == "published" for o in rows)
    assert all(o.last_verified_at is not None for o in rows)
    for o in rows:
        if o.deadline and o.deadline < date.today():
            assert o.verification_status == "expired"
        else:
            assert o.verification_status == "verified"
    logs = db.session.scalar(sa.select(sa.func.count(SourceVerificationLog.id)))
    assert logs == len(rows)
    assert seed_opportunities() == {"created": 0, "updated": 0, "skipped": len(rows)}


def test_official_listings_show_in_public_listing(client, db):
    seed_opportunities()
    items = client.get("/api/v1/opportunities?status=all&per_page=48").get_json()["items"]
    assert {i["data_origin"] for i in items} == {"official"}
    detail = client.get("/api/v1/opportunities/pm-usp-csss-scholarship-2026-27").get_json()["opportunity"]
    assert any(c["source_excerpt"] for c in detail["criteria"])
