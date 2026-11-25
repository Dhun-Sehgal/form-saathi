"""Reference data: states/UTs, categories, document types (from shared/reference.json).

Factual lookup data only — no opportunities, amounts, dates or URLs. Idempotent.
"""
import json
from pathlib import Path

from flask import current_app

from ..extensions import db
from ..models import Category, DocumentType, State


def load_shared(name: str) -> dict:
    return json.loads((Path(current_app.config["SHARED_DIR"]) / name).read_text(encoding="utf-8"))


def state_code(name: str) -> str:
    return name.lower().replace(" and ", "-").replace(" ", "-")


def seed_reference() -> dict[str, int]:
    data = load_shared("reference.json")
    created = {"states": 0, "categories": 0, "document_types": 0}

    for name, kind in data["states"]:
        if not db.session.get(State, state_code(name)):
            db.session.add(State(code=state_code(name), name=name, kind=kind))
            created["states"] += 1

    for order, c in enumerate(data["categories"]):
        if db.session.scalar(db.select(Category).filter_by(slug=c["slug"])) is None:
            db.session.add(Category(sort_order=order, **c))
            created["categories"] += 1

    for order, d in enumerate(data["document_types"]):
        if db.session.scalar(db.select(DocumentType).filter_by(slug=d["slug"])) is None:
            db.session.add(DocumentType(sort_order=order, **d))
            created["document_types"] += 1

    db.session.commit()
    return created
