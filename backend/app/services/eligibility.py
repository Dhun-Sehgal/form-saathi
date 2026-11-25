"""Deterministic eligibility engine.

Rules decide, AI explains: this module compares admin-entered, structured criteria against
the user's profile. It never guesses. Missing profile data -> "unknown"; free-text criteria
-> "needs_review". The same logic is mirrored in frontend/src/api/preview/eligibility.js
for the browser-only preview build.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import date

MET, NOT_MET, UNKNOWN, NEEDS_REVIEW = "met", "not_met", "unknown", "needs_review"

# Income bands -> [lower, upper) in INR per year. None upper = no limit.
INCOME_BANDS = {
    "below_1l": (0, 100_000),
    "1l_to_2_5l": (100_000, 250_000),
    "2_5l_to_5l": (250_000, 500_000),
    "5l_to_8l": (500_000, 800_000),
    "above_8l": (800_000, None),
}

LABELS = {
    "class_10": "Class 10", "class_12": "Class 12", "diploma": "Diploma", "iti": "ITI",
    "undergraduate": "Undergraduate", "postgraduate": "Postgraduate", "doctorate": "Doctorate",
    "not_studying": "Not currently studying", "other": "Other",
    "general": "General", "ews": "EWS", "obc": "OBC", "sc": "SC", "st": "ST",
    "female": "Female", "male": "Male",
}


@dataclass
class CriterionResult:
    criterion_id: int | None
    criterion_type: str
    description: str
    source_excerpt: str | None
    is_mandatory: bool
    outcome: str
    reason: str
    missing_field: str | None = None


def _label(v: str) -> str:
    return LABELS.get(v, v.replace("_", " ").title())


def age_on(dob: date | None, on: date) -> int | None:
    if dob is None:
        return None
    return on.year - dob.year - ((on.month, on.day) < (dob.month, dob.day))


def _get(profile, field):
    return getattr(profile, field, None) if not isinstance(profile, dict) else profile.get(field)


def check(criterion_type: str, value: dict, profile, today: date | None = None) -> tuple[str, str, str | None]:
    """Return (outcome, reason, missing_profile_field)."""
    today = today or date.today()
    value = value or {}

    if criterion_type in ("age_min", "age_max"):
        as_on = date.fromisoformat(value["as_on"]) if value.get("as_on") else today
        age = age_on(_get(profile, "date_of_birth"), as_on)
        limit = value.get("years")
        if age is None:
            return UNKNOWN, "Add your date of birth so we can check the age limit.", "date_of_birth"
        ok = age >= limit if criterion_type == "age_min" else age <= limit
        word = "at least" if criterion_type == "age_min" else "at most"
        return (MET if ok else NOT_MET), f"You are {age}; the rule requires {word} {limit}.", None

    if criterion_type == "education_level":
        level = _get(profile, "education_level")
        allowed = value.get("any_of", [])
        if not level:
            return UNKNOWN, "Add your education level to check this.", "education_level"
        names = ", ".join(_label(a) for a in allowed)
        if level in allowed:
            return MET, f"Your education level ({_label(level)}) is accepted.", None
        return NOT_MET, f"Accepted levels: {names}. Yours: {_label(level)}.", None

    if criterion_type == "course":
        course = " ".join(filter(None, [_get(profile, "course"), _get(profile, "stream")])).lower()
        keywords = [k.lower() for k in value.get("any_of", [])]
        if not course.strip():
            return UNKNOWN, "Add your course and stream to check this.", "course"
        if any(k in course for k in keywords):
            return MET, "Your course matches the required field.", None
        # Course names vary a lot between institutions, so a non-match is never a hard "no".
        return NEEDS_REVIEW, "We couldn't match your course name automatically. Check the official list of eligible courses.", None

    if criterion_type == "year_of_study":
        year = _get(profile, "current_year")
        if year is None:
            return UNKNOWN, "Add your current year of study.", "current_year"
        lo, hi = value.get("min", 1), value.get("max", 10)
        ok = lo <= year <= hi
        return (MET if ok else NOT_MET), f"You are in year {year}; accepted: year {lo} to {hi}.", None

    if criterion_type in ("marks_min_percentage", "marks_min_cgpa"):
        want_type = "percentage" if criterion_type == "marks_min_percentage" else "cgpa"
        mtype, marks = _get(profile, "marks_type"), _get(profile, "marks_value")
        need = value.get("value")
        unit = "%" if want_type == "percentage" else " CGPA"
        if marks is None or not mtype:
            return UNKNOWN, "Add your latest marks or CGPA.", "marks_value"
        if mtype != want_type:
            return NEEDS_REVIEW, (
                f"The rule uses {want_type} (minimum {need}{unit}) but your profile has {mtype}. "
                "Conversion formulas differ by university, so please check with your institution."
            ), None
        ok = float(marks) >= float(need)
        return (MET if ok else NOT_MET), f"Your score is {float(marks):g}{unit}; minimum required is {need}{unit}.", None

    if criterion_type == "income_max":
        band = _get(profile, "income_range")
        limit = value.get("amount")
        limit_txt = f"Rs {limit:,}"
        if not band or band == "prefer_not_say":
            return UNKNOWN, f"This needs family income up to {limit_txt}/year. Add your income range (optional) to check.", "income_range"
        lower, upper = INCOME_BANDS[band]
        if upper is not None and upper <= limit:
            return MET, f"Your family income band is within the {limit_txt} limit.", None
        if lower > limit:
            return NOT_MET, f"Your income band is above the {limit_txt} limit.", None
        return UNKNOWN, f"Your income band crosses the {limit_txt} limit; your exact income certificate decides.", None

    if criterion_type == "state_domicile":
        state = _get(profile, "state_code")
        allowed = value.get("any_of", [])
        if not state:
            return UNKNOWN, "Add your state to check the residence rule.", "state_code"
        if state in allowed:
            return MET, "Your state is eligible. You'll need a domicile certificate as proof.", None
        return NOT_MET, "This is only for residents of: " + ", ".join(a.replace("-", " ").title() for a in allowed) + ".", None

    if criterion_type == "social_category":
        cat = _get(profile, "social_category")
        allowed = value.get("any_of", [])
        names = ", ".join(_label(a) for a in allowed)
        if not cat or cat == "prefer_not_say":
            return UNKNOWN, f"Open to: {names}. Add your category (optional) to check.", "social_category"
        if cat in allowed:
            return MET, f"Your category ({_label(cat)}) is eligible.", None
        return NOT_MET, f"Open only to: {names}.", None

    if criterion_type == "gender":
        gender = _get(profile, "gender")
        allowed = value.get("any_of", [])
        names = ", ".join(_label(a) for a in allowed)
        if not gender or gender == "prefer_not_say":
            return UNKNOWN, f"Open to: {names}. Add your gender (optional) to check.", "gender"
        return (MET, "Matches the gender criterion.", None) if gender in allowed else (NOT_MET, f"Open only to: {names}.", None)

    if criterion_type == "disability":
        has = _get(profile, "has_disability")
        if has is None:
            return UNKNOWN, "This is for persons with disabilities. Update your profile (optional) to check.", "has_disability"
        return (MET, "Matches the disability criterion.", None) if has else (NOT_MET, "Only for persons with disabilities.", None)

    return NEEDS_REVIEW, "This rule can't be checked automatically. Read it carefully and confirm it applies to you.", None


def evaluate(profile, criteria) -> dict:
    """profile: UserProfile or dict. criteria: iterable of EligibilityCriterion or dicts."""
    results: list[CriterionResult] = []
    for c in criteria:
        get = (lambda k: c.get(k)) if isinstance(c, dict) else (lambda k: getattr(c, k))
        outcome, reason, missing = check(get("criterion_type"), get("value"), profile) if profile is not None else (
            UNKNOWN, "Complete your profile to check this.", None
        )
        results.append(CriterionResult(
            criterion_id=get("id"), criterion_type=get("criterion_type"), description=get("description"),
            source_excerpt=get("source_excerpt"), is_mandatory=bool(get("is_mandatory")),
            outcome=outcome, reason=reason, missing_field=missing,
        ))

    mandatory = [r for r in results if r.is_mandatory]
    if any(r.outcome == NOT_MET for r in mandatory):
        verdict = "not_eligible"
    elif any(r.outcome in (UNKNOWN, NEEDS_REVIEW) for r in mandatory):
        verdict = "possibly_eligible"
    else:
        verdict = "eligible"

    counts = {k: sum(1 for r in results if r.outcome == k) for k in (MET, NOT_MET, UNKNOWN, NEEDS_REVIEW)}
    return {
        "verdict": verdict,
        "counts": counts,
        "results": [asdict(r) for r in results],
        "missing_fields": sorted({r.missing_field for r in results if r.missing_field}),
    }


def template_explanation(report: dict, title: str) -> dict:
    """Plain-language explanation used when AI is not configured (or fails)."""
    v, c = report["verdict"], report["counts"]
    if v == "eligible":
        summary = f"Based on your profile, you meet all {c['met']} checkable rules for {title}."
        steps = ["Gather the required documents.", "Read the official notification once before applying.",
                 "Apply on the official portal before the deadline."]
    elif v == "possibly_eligible":
        pending = c["unknown"] + c["needs_review"]
        summary = f"You may be eligible for {title}. {c['met']} rule(s) match, and {pending} need more information or your review."
        steps = []
        if report["missing_fields"]:
            steps.append("Complete the missing profile details highlighted below.")
        if c["needs_review"]:
            steps.append("Read the rules marked 'Needs your review' in the official notification.")
        steps.append("Re-run this check after updating your profile.")
    else:
        summary = f"Based on your profile, you do not meet {c['not_met']} required rule(s) for {title}."
        steps = ["Check the reasons below. If your profile is out of date, update it and check again.",
                 "Explore similar opportunities that match your profile."]
    return {"summary": summary, "next_steps": steps}


def _digest(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()


PROFILE_FIELDS = ("date_of_birth", "education_level", "course", "stream", "current_year", "marks_type",
                  "marks_value", "income_range", "state_code", "social_category", "gender", "has_disability")


def profile_hash(profile) -> str:
    return _digest({f: _get(profile, f) for f in PROFILE_FIELDS} if profile else {})


def criteria_hash(criteria) -> str:
    return _digest([(c.id, c.criterion_type, c.value, c.is_mandatory, c.description) for c in criteria])
