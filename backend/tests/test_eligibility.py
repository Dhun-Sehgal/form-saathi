"""The deterministic rule engine: every outcome type and the verdict logic."""
from datetime import date

from app.services.eligibility import evaluate, template_explanation

TODAY = date.today()


def crit(type_, value, mandatory=True, desc="rule"):
    return {"id": None, "criterion_type": type_, "value": value, "description": desc,
            "source_excerpt": None, "is_mandatory": mandatory}


def profile(**kw):
    base = {"date_of_birth": date(TODAY.year - 20, 1, 1), "education_level": "undergraduate",
            "course": "B.Tech Computer Science", "stream": None, "current_year": 3, "marks_type": "percentage",
            "marks_value": 72, "income_range": "1l_to_2_5l", "state_code": "maharashtra",
            "social_category": None, "gender": "female", "has_disability": None}
    base.update(kw)
    return base


def test_all_met_is_eligible():
    r = evaluate(profile(), [crit("education_level", {"any_of": ["undergraduate"]}),
                             crit("income_max", {"amount": 250000}),
                             crit("marks_min_percentage", {"value": 60}),
                             crit("age_max", {"years": 25})])
    assert r["verdict"] == "eligible"
    assert r["counts"]["met"] == 4


def test_mandatory_not_met_is_not_eligible():
    r = evaluate(profile(education_level="class_12"), [crit("education_level", {"any_of": ["undergraduate"]})])
    assert r["verdict"] == "not_eligible"


def test_optional_not_met_does_not_block():
    r = evaluate(profile(), [crit("gender", {"any_of": ["male"]}, mandatory=False)])
    assert r["verdict"] == "eligible"


def test_missing_profile_data_is_unknown_not_rejected():
    r = evaluate(profile(social_category=None), [crit("social_category", {"any_of": ["sc", "st"]})])
    assert r["verdict"] == "possibly_eligible"
    assert r["results"][0]["outcome"] == "unknown"
    assert r["missing_fields"] == ["social_category"]


def test_prefer_not_say_is_respected_as_unknown():
    r = evaluate(profile(income_range="prefer_not_say"), [crit("income_max", {"amount": 250000})])
    assert r["results"][0]["outcome"] == "unknown"


def test_income_band_boundaries():
    over = evaluate(profile(income_range="5l_to_8l"), [crit("income_max", {"amount": 250000})])
    assert over["verdict"] == "not_eligible"
    straddle = evaluate(profile(income_range="2_5l_to_5l"), [crit("income_max", {"amount": 300000})])
    assert straddle["results"][0]["outcome"] == "unknown"


def test_custom_rule_needs_review():
    r = evaluate(profile(), [crit("custom", {})])
    assert r["verdict"] == "possibly_eligible"
    assert r["results"][0]["outcome"] == "needs_review"


def test_cgpa_vs_percentage_is_not_guessed():
    r = evaluate(profile(marks_type="cgpa", marks_value=8.1), [crit("marks_min_percentage", {"value": 60})])
    assert r["results"][0]["outcome"] == "needs_review"


def test_age_limits():
    young = evaluate(profile(date_of_birth=date(TODAY.year - 17, 1, 1)), [crit("age_min", {"years": 18})])
    assert young["verdict"] == "not_eligible"
    no_dob = evaluate(profile(date_of_birth=None), [crit("age_min", {"years": 18})])
    assert no_dob["results"][0]["missing_field"] == "date_of_birth"


def test_state_and_course_matching():
    r = evaluate(profile(), [crit("state_domicile", {"any_of": ["maharashtra"]}),
                             crit("course", {"any_of": ["computer"]})])
    assert r["verdict"] == "eligible"
    other = evaluate(profile(course="BA History"), [crit("course", {"any_of": ["computer"]})])
    assert other["results"][0]["outcome"] == "needs_review"  # course names vary; never a hard "no"


def test_no_profile_means_possibly():
    assert evaluate(None, [crit("age_min", {"years": 18})])["verdict"] == "possibly_eligible"


def test_template_explanation_has_steps():
    r = evaluate(profile(), [crit("custom", {})])
    e = template_explanation(r, "Demo")
    assert e["summary"] and e["next_steps"]
