"""ATS resume builder: save/load resumes, prefill from profile, optional AI bullet rewriting.

The ATS readiness checks and job-keyword matching run in the browser (frontend/src/utils/ats.js),
so they work the same in the full app and the browser-only preview, and no resume text leaves
the user's device for analysis.
"""
import sqlalchemy as sa
from flask import Blueprint, jsonify
from marshmallow import Schema, fields, validate

from ..extensions import db, limiter
from ..models import Resume
from ..models.resume import RESUME_TEMPLATES
from ..services import llm
from ..utils.auth import current_user, login_required
from ..utils.errors import APIError, not_found
from ..utils.helpers import body, iso

bp = Blueprint("resumes", __name__, url_prefix="/api/v1/resumes")
MAX_RESUMES = 10

S = lambda n: fields.String(load_default="", validate=validate.Length(max=n))  # noqa: E731
Bullets = lambda: fields.List(fields.String(validate=validate.Length(max=400)), load_default=list,  # noqa: E731
                              validate=validate.Length(max=8))


class LinkIn(Schema):
    label = S(40)
    url = S(300)


class BasicsIn(Schema):
    name = S(120)
    headline = S(160)
    email = S(254)
    phone = S(40)
    location = S(120)
    links = fields.List(fields.Nested(LinkIn), load_default=list, validate=validate.Length(max=6))


class ExperienceIn(Schema):
    role = S(120)
    org = S(160)
    location = S(120)
    start = S(40)
    end = S(40)
    bullets = Bullets()


class ProjectIn(Schema):
    name = S(160)
    tech = S(200)
    link = S(300)
    bullets = Bullets()


class EducationIn(Schema):
    school = S(160)
    degree = S(200)
    start = S(40)
    end = S(40)
    score = S(60)
    details = S(400)


class SkillGroupIn(Schema):
    group = S(60)
    items = S(400)


class ResumeData(Schema):
    basics = fields.Nested(BasicsIn, load_default=dict)
    summary = S(1200)
    experience = fields.List(fields.Nested(ExperienceIn), load_default=list, validate=validate.Length(max=10))
    projects = fields.List(fields.Nested(ProjectIn), load_default=list, validate=validate.Length(max=10))
    education = fields.List(fields.Nested(EducationIn), load_default=list, validate=validate.Length(max=6))
    skills = fields.List(fields.Nested(SkillGroupIn), load_default=list, validate=validate.Length(max=10))
    achievements = fields.List(fields.String(validate=validate.Length(max=300)), load_default=list,
                               validate=validate.Length(max=10))
    certifications = fields.List(fields.String(validate=validate.Length(max=300)), load_default=list,
                                 validate=validate.Length(max=10))


class ResumeIn(Schema):
    title = fields.String(required=True, validate=validate.Length(min=1, max=120))
    target_role = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=120))
    template = fields.String(load_default="classic", validate=validate.OneOf(RESUME_TEMPLATES))
    data = fields.Nested(ResumeData, load_default=dict)
    from_profile = fields.Boolean(load_default=False, load_only=True)


class ImproveIn(Schema):
    bullet = fields.String(required=True, validate=validate.Length(min=3, max=400))
    role = fields.String(load_default="", validate=validate.Length(max=120))


def _dict(r: Resume, full: bool = True) -> dict:
    d = {"id": r.id, "title": r.title, "target_role": r.target_role, "template": r.template,
         "created_at": iso(r.created_at), "updated_at": iso(r.updated_at)}
    if full:
        d["data"] = r.data or {}
    return d


def _own(rid) -> Resume:
    r = db.session.get(Resume, rid)
    if r is None or r.user_id != current_user().id:
        raise not_found("Resume")
    return r


def profile_prefill(user) -> dict:
    """Start a resume from what the user already told FormSaathi (nothing is invented)."""
    p = user.profile
    labels = {"class_10": "Class 10", "class_12": "Class 12", "diploma": "Diploma", "iti": "ITI",
              "undergraduate": "Bachelor's degree", "postgraduate": "Master's degree", "doctorate": "PhD"}
    education = []
    if p and (p.institution or p.course):
        degree = " ".join(filter(None, [p.course, f"({p.stream})" if p.stream else None])) or labels.get(p.education_level, "")
        score = ""
        if p.marks_value is not None:
            score = f"CGPA: {float(p.marks_value):g}" if p.marks_type == "cgpa" else f"{float(p.marks_value):g}%"
        education.append({"school": p.institution or "", "degree": degree, "start": "", "end": "", "score": score,
                          "details": ""})
    state_city = ", ".join(filter(None, [p.city if p else None, p.state.name if p and p.state else None]))
    return {
        "basics": {"name": (p.full_name if p else "") or "", "headline": "", "email": user.email, "phone": "",
                   "location": state_city, "links": []},
        "summary": "",
        "experience": [],
        "projects": [],
        "education": education,
        "skills": [{"group": "Skills", "items": ", ".join(p.skills or [])}] if p and p.skills else [],
        "achievements": [],
        "certifications": [],
    }


@bp.get("")
@login_required
def list_resumes():
    rows = db.session.scalars(sa.select(Resume).where(Resume.user_id == current_user().id)
                              .order_by(Resume.updated_at.desc(), Resume.id.desc())).all()
    return jsonify(items=[_dict(r, full=False) for r in rows], ai_configured=llm.is_configured())


@bp.post("")
@login_required
def create_resume():
    data = body(ResumeIn())
    user = current_user()
    count = db.session.scalar(sa.select(sa.func.count(Resume.id)).where(Resume.user_id == user.id))
    if count >= MAX_RESUMES:
        raise APIError(f"You can keep up to {MAX_RESUMES} resumes. Delete one to create another.", 409, "limit_reached")
    content = profile_prefill(user) if data.pop("from_profile") else data["data"]
    r = Resume(user_id=user.id, title=data["title"].strip(), target_role=data["target_role"],
               template=data["template"], data=content)
    db.session.add(r)
    db.session.commit()
    return jsonify(resume=_dict(r)), 201


@bp.get("/<int:rid>")
@login_required
def get_resume(rid):
    return jsonify(resume=_dict(_own(rid)), ai_configured=llm.is_configured())


@bp.put("/<int:rid>")
@login_required
def update_resume(rid):
    r = _own(rid)
    data = body(ResumeIn())
    data.pop("from_profile", None)
    r.title, r.target_role, r.template, r.data = data["title"].strip(), data["target_role"], data["template"], data["data"]
    db.session.commit()
    return jsonify(resume=_dict(r))


@bp.post("/<int:rid>/duplicate")
@login_required
def duplicate_resume(rid):
    src = _own(rid)
    user = current_user()
    count = db.session.scalar(sa.select(sa.func.count(Resume.id)).where(Resume.user_id == user.id))
    if count >= MAX_RESUMES:
        raise APIError(f"You can keep up to {MAX_RESUMES} resumes. Delete one to create another.", 409, "limit_reached")
    r = Resume(user_id=user.id, title=f"{src.title} (copy)"[:120], target_role=src.target_role,
               template=src.template, data=dict(src.data or {}))
    db.session.add(r)
    db.session.commit()
    return jsonify(resume=_dict(r)), 201


@bp.delete("/<int:rid>")
@login_required
def delete_resume(rid):
    db.session.delete(_own(rid))
    db.session.commit()
    return jsonify(ok=True)


@bp.post("/improve-bullet")
@login_required
@limiter.limit("30 per hour")
def improve_bullet():
    data = body(ImproveIn())
    if not llm.is_configured():
        raise APIError("Saathi AI isn't configured on this server yet. The ATS checks still work without it.",
                       503, "ai_not_configured")
    try:
        suggestions = llm.improve_bullet(data["bullet"], data["role"])
    except llm.AIUnavailable as e:
        raise APIError(str(e), 503, "ai_unavailable")
    except Exception:
        raise APIError("Saathi AI couldn't rewrite this bullet right now. Please try again.", 503, "ai_unavailable")
    return jsonify(suggestions=suggestions)
