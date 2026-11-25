"""Model -> JSON dictionaries. Kept in one place so the API contract is easy to read."""
from __future__ import annotations

from datetime import date

from .models import (
    Application, Category, Collection, CorrectionReport, DocumentType, EligibilityCriterion,
    Notification, Opportunity, Organization, Reminder, UploadedDocument, User, UserProfile,
)
from .utils.helpers import days_until, iso

PROFILE_CORE = [
    ("full_name", "Full name"), ("date_of_birth", "Date of birth"), ("state_code", "State"),
    ("city", "City"), ("education_level", "Education level"), ("institution", "College / institution"),
    ("course", "Course"), ("current_year", "Year of study"), ("marks_value", "Marks / CGPA"),
    ("interests", "Interested categories"), ("skills", "Skills"),
]
PROFILE_OPTIONAL = [
    ("income_range", "Family income range"), ("social_category", "Social category"),
    ("gender", "Gender"), ("has_disability", "Disability status"),
]


def profile_completion(p: UserProfile | None) -> dict:
    if p is None:
        return {"percent": 0, "missing": [label for _, label in PROFILE_CORE], "optional_missing": []}

    def filled(field):
        v = getattr(p, field)
        return bool(v) if isinstance(v, list) or field == "interests" else v is not None and v != ""

    missing = [label for f, label in PROFILE_CORE if not filled(f)]
    optional_missing = [label for f, label in PROFILE_OPTIONAL if getattr(p, f) is None]
    percent = round(100 * (len(PROFILE_CORE) - len(missing)) / len(PROFILE_CORE))
    return {"percent": percent, "missing": missing, "optional_missing": optional_missing}


def category_dict(c: Category) -> dict:
    return {"id": c.id, "slug": c.slug, "name": c.name, "description": c.description, "icon": c.icon,
            "color": c.color, "sort_order": c.sort_order, "is_active": c.is_active}


def document_type_dict(d: DocumentType) -> dict:
    return {"id": d.id, "slug": d.slug, "name": d.name, "description": d.description, "sensitivity": d.sensitivity}


def organization_dict(o: Organization) -> dict:
    return {"id": o.id, "name": o.name, "org_type": o.org_type, "website": o.website}


def profile_dict(p: UserProfile | None) -> dict | None:
    if p is None:
        return None
    return {
        "full_name": p.full_name, "date_of_birth": iso(p.date_of_birth), "gender": p.gender,
        "state_code": p.state_code, "city": p.city, "education_level": p.education_level,
        "institution": p.institution, "course": p.course, "stream": p.stream, "current_year": p.current_year,
        "marks_type": p.marks_type, "marks_value": float(p.marks_value) if p.marks_value is not None else None,
        "income_range": p.income_range, "social_category": p.social_category, "has_disability": p.has_disability,
        "skills": p.skills or [], "career_interests": p.career_interests or [],
        "interests": [c.slug for c in p.interests], "preferred_language": p.preferred_language,
        "onboarding_step": p.onboarding_step, "onboarding_completed_at": iso(p.onboarding_completed_at),
    }


def user_dict(u: User) -> dict:
    return {
        "id": u.id, "email": u.email, "role": u.role, "is_active": u.is_active,
        "email_verified": u.email_verified_at is not None, "created_at": iso(u.created_at),
        "profile": profile_dict(u.profile), "profile_completion": profile_completion(u.profile),
        "onboarding_completed": bool(u.profile and u.profile.onboarding_completed_at),
    }


def opportunity_card(o: Opportunity, saved_ids: set | None = None, app_status: dict | None = None) -> dict:
    return {
        "id": o.id, "slug": o.slug, "title": o.title, "summary": o.summary,
        "category": {"slug": o.category.slug, "name": o.category.name, "icon": o.category.icon, "color": o.category.color},
        "organization": {"name": o.organization.name, "org_type": o.organization.org_type},
        "scope": o.scope, "eligibility_summary": o.eligibility_summary, "benefits": o.benefits,
        "benefit_amount_min": float(o.benefit_amount_min) if o.benefit_amount_min is not None else None,
        "benefit_amount_max": float(o.benefit_amount_max) if o.benefit_amount_max is not None else None,
        "benefit_frequency": o.benefit_frequency,
        "deadline": iso(o.deadline), "is_rolling": o.is_rolling, "deadline_note": o.deadline_note,
        "days_left": days_until(o.deadline), "is_open": o.is_open,
        "official_url": o.official_url, "apply_url": o.apply_url, "source_url": o.source_url,
        "verification_status": o.verification_status, "publication_status": o.publication_status,
        "data_origin": o.data_origin, "last_verified_at": iso(o.last_verified_at),
        "is_featured": o.is_featured, "created_at": iso(o.created_at),
        "states": [s.code for s in o.states],
        "saved": (o.id in saved_ids) if saved_ids is not None else False,
        "application_status": (app_status or {}).get(o.id),
    }


def criterion_dict(c: EligibilityCriterion) -> dict:
    return {"id": c.id, "criterion_type": c.criterion_type, "value": c.value, "description": c.description,
            "source_excerpt": c.source_excerpt, "is_mandatory": c.is_mandatory, "sort_order": c.sort_order}


def opportunity_detail(o: Opportunity, saved_ids=None, app_status=None) -> dict:
    d = opportunity_card(o, saved_ids, app_status)
    d.update({
        "description": o.description, "how_to_apply": o.how_to_apply, "application_mode": o.application_mode,
        "opens_on": iso(o.opens_on), "income_ceiling": float(o.income_ceiling) if o.income_ceiling else None,
        "organization": organization_dict(o.organization),
        "category_id": o.category_id, "organization_id": o.organization_id,
        "criteria": [criterion_dict(c) for c in o.criteria],
        "required_documents": [
            {"document_type": document_type_dict(r.document_type), "is_mandatory": r.is_mandatory, "notes": r.notes}
            for r in o.required_documents
        ],
        "dates": [{"label": x.label, "date": iso(x.event_date), "note": x.note} for x in o.dates],
        "updated_at": iso(o.updated_at),
    })
    return d


def application_dict(a: Application, full: bool = False) -> dict:
    d = {
        "id": a.id, "status": a.status, "status_source": a.status_source, "applied_on": iso(a.applied_on),
        "reference_number": a.reference_number, "created_at": iso(a.created_at), "updated_at": iso(a.updated_at),
        "opportunity": opportunity_card(a.opportunity),
    }
    if full:
        d["history"] = [{"from_status": h.from_status, "to_status": h.to_status, "source": h.source,
                         "note": h.note, "created_at": iso(h.created_at)} for h in a.history]
        d["notes"] = [{"id": n.id, "body": n.body, "created_at": iso(n.created_at)} for n in a.notes]
    return d


def document_dict(d: UploadedDocument) -> dict:
    expired = d.expires_on is not None and d.expires_on < date.today()
    return {
        "id": d.id, "document_type": document_type_dict(d.document_type), "label": d.label,
        "original_filename": d.original_filename, "mime_type": d.mime_type, "size_bytes": d.size_bytes,
        "status": "expired" if expired else d.status, "issued_on": iso(d.issued_on), "expires_on": iso(d.expires_on),
        "created_at": iso(d.created_at),
    }


def notification_dict(n: Notification) -> dict:
    return {"id": n.id, "type": n.type, "title": n.title, "body": n.body, "link": n.link,
            "is_read": n.is_read, "created_at": iso(n.created_at)}


def reminder_dict(r: Reminder) -> dict:
    return {"id": r.id, "title": r.title, "remind_at": iso(r.remind_at), "channel": r.channel,
            "application_id": r.application_id, "opportunity_id": r.opportunity_id,
            "sent_at": iso(r.sent_at), "is_done": r.is_done}


def collection_dict(c: Collection, count: int = 0) -> dict:
    return {"id": c.id, "name": c.name, "count": count}


def correction_dict(c: CorrectionReport) -> dict:
    return {"id": c.id, "field": c.field, "message": c.message, "suggested_source_url": c.suggested_source_url,
            "status": c.status, "admin_note": c.admin_note, "created_at": iso(c.created_at),
            "reviewed_at": iso(c.reviewed_at),
            "opportunity": {"id": c.opportunity.id, "slug": c.opportunity.slug, "title": c.opportunity.title}}
