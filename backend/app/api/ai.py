"""Eligibility checks and Saathi AI chat."""
import json

import sqlalchemy as sa
from flask import Blueprint, jsonify
from marshmallow import Schema, fields, validate
from sqlalchemy.orm import selectinload

from ..extensions import db, limiter
from ..models import ChatMessage, ChatSession, EligibilityCheck, Opportunity
from ..models.base import LANGUAGES
from ..services import catalog, eligibility, llm
from ..utils.auth import current_user, login_required
from ..utils.errors import APIError, not_found
from ..utils.helpers import body, iso

bp = Blueprint("ai", __name__, url_prefix="/api/v1")

AI_OFF = APIError(
    "Saathi AI isn't configured on this server yet. The eligibility rules still work without it.",
    503, "ai_not_configured")


class AskSchema(Schema):
    content = fields.String(required=True, validate=validate.Length(min=1, max=2000))


class SessionSchema(Schema):
    opportunity_id = fields.Integer(load_default=None, allow_none=True)
    language = fields.String(load_default="en", validate=validate.OneOf(LANGUAGES))


class CheckSchema(Schema):
    explain = fields.Boolean(load_default=True)
    language = fields.String(load_default="en", validate=validate.OneOf(LANGUAGES))


def _opportunity(opportunity_id) -> Opportunity:
    o = db.session.scalars(catalog.public_query().where(Opportunity.id == opportunity_id).options(
        selectinload(Opportunity.criteria), selectinload(Opportunity.required_documents),
        selectinload(Opportunity.dates))).first()
    if o is None:
        raise not_found("Opportunity")
    return o


# ------------------------------------------------------------------ eligibility
@bp.post("/eligibility/<int:opportunity_id>")
@login_required
@limiter.limit("60 per hour")
def check_eligibility(opportunity_id):
    data = body(CheckSchema())
    user = current_user()
    o = _opportunity(opportunity_id)
    report = eligibility.evaluate(user.profile, o.criteria)
    p_hash, c_hash = eligibility.profile_hash(user.profile), eligibility.criteria_hash(o.criteria)

    # Reuse a cached AI explanation if neither the profile nor the rules changed.
    cached = db.session.scalar(sa.select(EligibilityCheck).where(
        EligibilityCheck.user_id == user.id, EligibilityCheck.opportunity_id == o.id,
        EligibilityCheck.profile_hash == p_hash, EligibilityCheck.criteria_hash == c_hash,
        EligibilityCheck.explanation_source == "ai").order_by(EligibilityCheck.created_at.desc()))
    explanation, source = None, "template"
    if cached and (cached.explanation or {}).get("language") == data["language"]:
        explanation, source = cached.explanation, "ai"
    elif data["explain"] and llm.is_configured() and o.criteria:
        try:
            explanation = llm.explain_eligibility(o.title, report, data["language"])
            explanation["language"] = data["language"]
            source = "ai"
        except Exception:  # any AI failure falls back to the deterministic template
            explanation = None
    if explanation is None:
        explanation = eligibility.template_explanation(report, o.title)

    db.session.add(EligibilityCheck(user_id=user.id, opportunity_id=o.id, verdict=report["verdict"],
                                    results=report["results"], explanation=explanation, explanation_source=source,
                                    profile_hash=p_hash, criteria_hash=c_hash))
    db.session.commit()
    return jsonify(
        opportunity={"id": o.id, "slug": o.slug, "title": o.title, "data_origin": o.data_origin,
                     "verification_status": o.verification_status, "source_url": o.source_url},
        report=report, explanation=explanation, explanation_source=source, ai_configured=llm.is_configured(),
    )


# ------------------------------------------------------------------ Saathi AI chat
def _session(session_id) -> ChatSession:
    s = db.session.get(ChatSession, session_id)
    if s is None or s.user_id != current_user().id:
        raise not_found("Conversation")
    return s


def _session_dict(s: ChatSession, messages=False) -> dict:
    d = {"id": s.id, "title": s.title, "language": s.language, "opportunity_id": s.opportunity_id,
         "created_at": iso(s.created_at), "updated_at": iso(s.updated_at)}
    if messages:
        d["messages"] = [{"id": m.id, "role": m.role, "content": m.content, "created_at": iso(m.created_at)}
                         for m in s.messages]
        if s.opportunity_id:
            o = db.session.get(Opportunity, s.opportunity_id)
            d["opportunity"] = {"id": o.id, "slug": o.slug, "title": o.title} if o else None
    return d


def _opportunity_context(o: Opportunity) -> str:
    record = {
        "title": o.title, "organization": o.organization.name, "category": o.category.name,
        "data": "DEMO (sample, not a real opportunity)" if o.data_origin == "demo" else "official",
        "verification_status": o.verification_status,
        "last_verified": iso(o.last_verified_at), "summary": o.summary, "description": o.description,
        "eligibility_rules": [{"rule": c.description, "official_text": c.source_excerpt, "mandatory": c.is_mandatory}
                              for c in o.criteria],
        "benefits": o.benefits, "required_documents": [
            {"document": r.document_type.name, "mandatory": r.is_mandatory, "notes": r.notes} for r in o.required_documents],
        "deadline": iso(o.deadline), "rolling": o.is_rolling, "important_dates": [
            {"label": d.label, "date": iso(d.event_date)} for d in o.dates],
        "how_to_apply": o.how_to_apply, "official_source": o.source_url, "apply_url": o.apply_url,
    }
    return "\n\nOPPORTUNITY RECORD (the only source of facts about this opportunity):\n" + json.dumps(
        record, ensure_ascii=False, indent=1)


def _profile_context(user) -> str:
    p = user.profile
    if not p:
        return ""
    # Only non-sensitive fields are shared with the AI provider.
    bits = {"education_level": p.education_level, "course": p.course, "year": p.current_year, "state": p.state_code}
    bits = {k: v for k, v in bits.items() if v}
    return "\n\nUser context (for personalising explanations): " + json.dumps(bits) if bits else ""


@bp.get("/ai/status")
def ai_status():
    return jsonify(configured=llm.is_configured())


@bp.get("/ai/sessions")
@login_required
def list_sessions():
    rows = db.session.scalars(sa.select(ChatSession).where(ChatSession.user_id == current_user().id)
                              .order_by(ChatSession.updated_at.desc()).limit(50)).all()
    return jsonify(items=[_session_dict(s) for s in rows], configured=llm.is_configured())


@bp.post("/ai/sessions")
@login_required
def create_session():
    data = body(SessionSchema())
    title = "New conversation"
    if data["opportunity_id"]:
        title = _opportunity(data["opportunity_id"]).title[:110]
    s = ChatSession(user_id=current_user().id, opportunity_id=data["opportunity_id"], language=data["language"],
                    title=title)
    db.session.add(s)
    db.session.commit()
    return jsonify(session=_session_dict(s, messages=True)), 201


@bp.get("/ai/sessions/<session_id>")
@login_required
def get_session(session_id):
    return jsonify(session=_session_dict(_session(session_id), messages=True), configured=llm.is_configured())


@bp.delete("/ai/sessions/<session_id>")
@login_required
def delete_session(session_id):
    db.session.delete(_session(session_id))
    db.session.commit()
    return jsonify(ok=True)


@bp.post("/ai/sessions/<session_id>/messages")
@login_required
@limiter.limit("20 per minute; 200 per day")
def send_message(session_id):
    if not llm.is_configured():
        raise AI_OFF
    data = body(AskSchema())
    s = _session(session_id)
    user = current_user()

    system = llm.SAATHI_SYSTEM.format(language=llm.LANGUAGE_NAMES.get(s.language, "English"))
    if s.opportunity_id:
        o = db.session.get(Opportunity, s.opportunity_id)
        if o is not None:
            system += _opportunity_context(o)
    system += _profile_context(user)

    history = [{"role": m.role, "content": m.content} for m in s.messages[-20:]]
    history.append({"role": "user", "content": data["content"].strip()})
    try:
        answer = llm.chat(system, history)
    except llm.AIUnavailable as e:
        raise APIError(str(e), 503, "ai_unavailable")

    user_msg = ChatMessage(session_id=s.id, role="user", content=data["content"].strip())
    ai_msg = ChatMessage(session_id=s.id, role="assistant", **answer)
    db.session.add_all([user_msg, ai_msg])
    if s.title == "New conversation":
        s.title = data["content"].strip()[:60]
    s.updated_at = sa.func.now()
    db.session.commit()
    as_dict = lambda m: {"id": m.id, "role": m.role, "content": m.content, "created_at": iso(m.created_at)}  # noqa: E731
    return jsonify(user_message=as_dict(user_msg), assistant_message=as_dict(ai_msg), title=s.title)
