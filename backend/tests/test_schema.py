"""Phase 1: the schema builds, relationships work, and the data-integrity rules hold."""
from datetime import date, datetime, timezone

import pytest
from sqlalchemy.exc import IntegrityError, StatementError

from app.models import (
    Application, ApplicationStatusHistory, Category, DocumentType, EligibilityCriterion,
    Notification, Opportunity, Organization, RequiredDocument, SavedOpportunity, State,
    User, UserProfile,
)
from app.seed.reference import seed_reference

EXPECTED_TABLES = {
    "users", "user_profiles", "user_tokens", "revoked_tokens", "states", "profile_interest_categories",
    "categories", "organizations", "opportunities", "opportunity_states", "opportunity_education_levels",
    "eligibility_criteria", "document_types", "required_documents", "opportunity_dates",
    "collections", "saved_opportunities", "applications", "application_status_history",
    "application_notes", "reminders", "uploaded_documents", "chat_sessions", "chat_messages",
    "eligibility_checks", "notifications", "notification_preferences",
    "source_verification_logs", "correction_reports", "announcements", "feedback",
}


def make_opportunity(db, **overrides):
    seed_reference()
    org = Organization(name="Demo Education Trust", org_type="ngo")
    db.session.add(org)
    db.session.flush()
    fields = dict(
        slug="demo-merit-scholarship", title="Demo Merit Scholarship",
        summary="Sample record for UI demonstration.", description="Demo only.",
        category_id=db.session.scalar(db.select(Category.id).filter_by(slug="scholarships")),
        organization_id=org.id, eligibility_summary="Demo", benefits="Demo",
        source_url="https://example.org/demo", data_origin="demo",
    )
    fields.update(overrides)
    opp = Opportunity(**fields)
    db.session.add(opp)
    db.session.commit()
    return opp


def make_user(db, email="student@example.com"):
    user = User(email=email, password_hash="x")
    db.session.add(user)
    db.session.commit()
    return user


def test_all_tables_created(db):
    assert EXPECTED_TABLES <= set(db.metadata.tables)


def test_health_endpoint_reports_unconfigured_services(client):
    body = client.get("/api/v1/health").get_json()
    assert body["status"] == "ok"
    assert body["ai_configured"] is False  # no key in test env -> honest status


def test_reference_seed_is_idempotent(db):
    first = seed_reference()
    second = seed_reference()
    assert first["states"] == 36  # 28 states + 8 union territories
    assert first["categories"] >= 7 and first["document_types"] >= 9
    assert second == {"states": 0, "categories": 0, "document_types": 0}
    assert db.session.get(State, "maharashtra").name == "Maharashtra"


def test_profile_relationships(db):
    seed_reference()
    user = make_user(db)
    profile = UserProfile(user_id=user.id, full_name="Asha", state_code="maharashtra",
                          education_level="undergraduate", marks_type="cgpa", marks_value=8.4)
    profile.interests.append(db.session.scalar(db.select(Category).filter_by(slug="internships")))
    db.session.add(profile)
    db.session.commit()
    assert user.profile.state.name == "Maharashtra"
    assert [c.slug for c in user.profile.interests] == ["internships"]


def test_email_must_be_lowercase(db):
    db.session.add(User(email="Mixed@Example.com", password_hash="x"))
    with pytest.raises(IntegrityError):
        db.session.commit()


def test_cgpa_out_of_range_rejected(db):
    user = make_user(db)
    db.session.add(UserProfile(user_id=user.id, marks_type="cgpa", marks_value=42))
    with pytest.raises(IntegrityError):
        db.session.commit()


def test_invalid_enum_value_rejected(db):
    db.session.add(User(email="a@example.com", password_hash="x", role="superuser"))
    with pytest.raises((StatementError, LookupError)):
        db.session.commit()


def test_demo_data_can_never_be_marked_verified(db):
    opp = make_opportunity(db)
    opp.verification_status = "verified"
    opp.last_verified_at = datetime.now(timezone.utc)
    with pytest.raises(IntegrityError):
        db.session.commit()


def test_verified_requires_last_verified_date(db):
    opp = make_opportunity(db, data_origin="official")
    opp.verification_status = "verified"
    with pytest.raises(IntegrityError):
        db.session.commit()


def test_deadline_cannot_precede_opening(db):
    with pytest.raises(IntegrityError):
        make_opportunity(db, opens_on=date(2026, 7, 1), deadline=date(2026, 6, 1))


def test_opportunity_children_and_cascade(db):
    opp = make_opportunity(db)
    opp.criteria.append(EligibilityCriterion(
        criterion_type="income_max", value={"amount": 250000},
        description="Family income up to Rs 2.5 lakh per year (demo rule)",
    ))
    doc_type = db.session.scalar(db.select(DocumentType).filter_by(slug="income-certificate"))
    opp.required_documents.append(RequiredDocument(document_type_id=doc_type.id))
    db.session.commit()

    db.session.delete(opp)
    db.session.commit()
    assert db.session.scalar(db.select(db.func.count(EligibilityCriterion.id))) == 0
    assert db.session.scalar(db.select(db.func.count(RequiredDocument.id))) == 0


def test_no_duplicate_saves_or_applications(db):
    opp, user = make_opportunity(db), make_user(db)
    db.session.add_all([
        SavedOpportunity(user_id=user.id, opportunity_id=opp.id),
        SavedOpportunity(user_id=user.id, opportunity_id=opp.id),
    ])
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()

    db.session.add_all([
        Application(user_id=user.id, opportunity_id=opp.id),
        Application(user_id=user.id, opportunity_id=opp.id),
    ])
    with pytest.raises(IntegrityError):
        db.session.commit()


def test_application_history(db):
    opp, user = make_opportunity(db), make_user(db)
    app_row = Application(user_id=user.id, opportunity_id=opp.id)
    app_row.history.append(ApplicationStatusHistory(to_status="interested"))
    app_row.history.append(ApplicationStatusHistory(from_status="interested", to_status="preparing_documents"))
    db.session.add(app_row)
    db.session.commit()
    assert app_row.status_source == "user"
    assert [h.to_status for h in app_row.history] == ["interested", "preparing_documents"]


def test_notification_dedupe_key(db):
    user = make_user(db)
    db.session.add_all([
        Notification(user_id=user.id, type="deadline", title="3 days left", dedupe_key="deadline:1:3d"),
        Notification(user_id=user.id, type="deadline", title="3 days left", dedupe_key="deadline:1:3d"),
    ])
    with pytest.raises(IntegrityError):
        db.session.commit()


def test_is_open_logic(db):
    opp = make_opportunity(db, publication_status="published", deadline=date(2000, 1, 1))
    assert opp.is_open is False  # expired deadline is never "open"
    opp.deadline = None
    assert opp.is_open is True
