"""End-to-end API behaviour through the Flask test client."""
import io

import sqlalchemy as sa

from app.models import Opportunity, User
from app.seed import ensure_admin


def opp_id(db, slug):
    return db.session.scalar(sa.select(Opportunity.id).where(Opportunity.slug == slug))


# ------------------------------------------------------------------ auth
def test_register_login_me_logout(api):
    r = api.register()
    assert r.status_code == 201
    assert r.get_json()["user"]["email"] == "asha@example.com"
    assert api.get("/api/v1/auth/me").status_code == 200

    assert api.post("/api/v1/auth/logout").status_code == 200
    assert api.get("/api/v1/auth/me").status_code == 401

    bad = api.post("/api/v1/auth/login", {"email": "asha@example.com", "password": "wrong1234"})
    assert bad.status_code == 401 and bad.get_json()["error"]["code"] == "invalid_credentials"
    ok = api.post("/api/v1/auth/login", {"email": "ASHA@example.com", "password": "secret123"})
    assert ok.status_code == 200


def test_password_rules_and_duplicates(api):
    weak = api.post("/api/v1/auth/register", {"email": "x@example.com", "password": "short", "full_name": "X Y",
                                              "accept_terms": True})
    assert weak.status_code == 422 and "password" in weak.get_json()["error"]["fields"]
    api.register()
    dup = api.register()
    assert dup.status_code == 409


def test_password_is_hashed(api, db):
    api.register()
    user = db.session.scalar(sa.select(User))
    assert user.password_hash.startswith("$argon2")


def test_lockout_after_failed_attempts(api):
    api.register()
    api.post("/api/v1/auth/logout")
    for _ in range(5):
        api.post("/api/v1/auth/login", {"email": "asha@example.com", "password": "nope12345"})
    locked = api.post("/api/v1/auth/login", {"email": "asha@example.com", "password": "secret123"})
    assert locked.status_code == 429


def test_csrf_required_for_writes(api, client):
    api.register()
    r = client.put("/api/v1/profile", json={"city": "Pune"})  # no X-CSRF-TOKEN header
    assert r.status_code == 401 and r.get_json()["error"]["code"] == "csrf_failed"


def test_password_reset_flow(api, app, db):
    api.register()
    api.post("/api/v1/auth/logout")
    app.debug = True  # dev mode returns the link because email isn't configured
    r = api.post("/api/v1/auth/forgot-password", {"email": "asha@example.com"})
    token = r.get_json()["dev_reset_link"].rsplit("/", 1)[1]
    assert api.post("/api/v1/auth/reset-password", {"token": token, "password": "newpass123"}).status_code == 200
    assert api.post("/api/v1/auth/reset-password", {"token": token, "password": "again1234"}).status_code == 400
    assert api.post("/api/v1/auth/login", {"email": "asha@example.com", "password": "newpass123"}).status_code == 200


def test_unknown_email_gets_same_reset_message(api):
    r = api.post("/api/v1/auth/forgot-password", {"email": "nobody@example.com"})
    assert r.status_code == 200 and "If an account exists" in r.get_json()["message"]


# ------------------------------------------------------------------ profile & onboarding
def test_profile_update_and_completion(api, seeded):
    api.register()
    r = api.put("/api/v1/profile", {"state_code": "maharashtra", "education_level": "undergraduate",
                                    "marks_type": "cgpa", "marks_value": 8.2, "interests": ["scholarships"]})
    user = r.get_json()["user"]
    assert user["profile"]["interests"] == ["scholarships"]
    assert 0 < user["profile_completion"]["percent"] < 100
    bad = api.put("/api/v1/profile", {"marks_type": "cgpa", "marks_value": 42})
    assert bad.status_code == 422
    done = api.post("/api/v1/profile/onboarding/complete")
    assert done.get_json()["user"]["onboarding_completed"] is True


def test_export_and_delete_account(api, db):
    api.register()
    assert api.get("/api/v1/profile/export").get_json()["account"]["email"] == "asha@example.com"
    assert api.delete("/api/v1/profile/account", {"password": "wrong"}).status_code == 422
    assert api.delete("/api/v1/profile/account", {"password": "secret123"}).status_code == 200
    assert db.session.scalar(sa.select(sa.func.count(User.id))) == 0


# ------------------------------------------------------------------ discovery
def test_listing_hides_expired_by_default(client, seeded):
    items = client.get("/api/v1/opportunities?per_page=48").get_json()["items"]
    slugs = {i["slug"] for i in items}
    assert "demo-closed-research-internship" not in slugs
    assert all(i["data_origin"] == "demo" for i in items)
    closed = client.get("/api/v1/opportunities?status=closed").get_json()["items"]
    assert [i["slug"] for i in closed] == ["demo-closed-research-internship"]


def test_listing_filters(client, seeded):
    sch = client.get("/api/v1/opportunities?category=scholarships").get_json()["items"]
    assert sch and all(i["category"]["slug"] == "scholarships" for i in sch)
    kerala = client.get("/api/v1/opportunities?state=kerala&per_page=48").get_json()["items"]
    assert "demo-state-skill-certification" not in {i["slug"] for i in kerala}  # Maharashtra-only
    q = client.get("/api/v1/opportunities?q=internship").get_json()["items"]
    assert q[0]["slug"] == "demo-summer-software-internship"
    by_deadline = client.get("/api/v1/opportunities?sort=deadline&per_page=48").get_json()["items"]
    dated = [i["deadline"] for i in by_deadline if i["deadline"]]
    assert dated == sorted(dated)


def test_detail_and_404(client, seeded):
    d = client.get("/api/v1/opportunities/demo-merit-cum-means-scholarship").get_json()["opportunity"]
    assert d["criteria"] and d["required_documents"] and d["source_url"].startswith("https://example.org/")
    assert client.get("/api/v1/opportunities/nope").status_code == 404


def test_save_and_collections(api, db, seeded):
    api.register()
    oid = opp_id(db, "demo-rural-policy-fellowship")
    col = api.post("/api/v1/collections", {"name": "Final year"}).get_json()["collection"]
    assert api.post("/api/v1/saved", {"opportunity_id": oid, "collection_id": col["id"]}).status_code == 201
    assert api.post("/api/v1/saved", {"opportunity_id": oid}).status_code == 201  # idempotent
    saved = api.get("/api/v1/saved").get_json()["items"]
    assert len(saved) == 1
    assert api.delete(f"/api/v1/saved/{oid}").get_json()["saved"] is False


# ------------------------------------------------------------------ eligibility & AI
def test_eligibility_check_uses_rules_not_ai(api, db, seeded):
    api.register()
    api.put("/api/v1/profile", {"education_level": "undergraduate", "income_range": "below_1l",
                                "marks_type": "percentage", "marks_value": 75})
    oid = opp_id(db, "demo-merit-cum-means-scholarship")
    r = api.post(f"/api/v1/eligibility/{oid}", {}).get_json()
    assert r["report"]["verdict"] == "possibly_eligible"  # one custom rule needs the user's review
    assert r["explanation_source"] == "template" and r["ai_configured"] is False


def test_ai_chat_reports_not_configured(api, seeded):
    api.register()
    s = api.post("/api/v1/ai/sessions", {"language": "hi"}).get_json()["session"]
    r = api.post(f"/api/v1/ai/sessions/{s['id']}/messages", {"content": "Domicile certificate kya hai?"})
    assert r.status_code == 503 and r.get_json()["error"]["code"] == "ai_not_configured"


def test_recommendations_exclude_not_eligible_and_closed(api, seeded):
    api.register()
    api.put("/api/v1/profile", {"education_level": "class_12", "gender": "male"})
    items = api.get("/api/v1/opportunities/recommended?limit=20").get_json()["items"]
    slugs = {i["slug"] for i in items}
    assert "demo-women-in-stem-scholarship" not in slugs
    assert "demo-closed-research-internship" not in slugs
    assert all("match" in i for i in items)


# ------------------------------------------------------------------ tracker, documents, notifications
def test_tracker_flow_and_history(api, db, seeded):
    api.register()
    oid = opp_id(db, "demo-summer-software-internship")
    a = api.post("/api/v1/applications", {"opportunity_id": oid}).get_json()["application"]
    again = api.post("/api/v1/applications", {"opportunity_id": oid})
    assert again.status_code == 200 and again.get_json()["created"] is False
    api.patch(f"/api/v1/applications/{a['id']}", {"status": "preparing_documents"})
    r = api.patch(f"/api/v1/applications/{a['id']}", {"status": "applied", "applied_on": "2000-01-01",
                                                     "reference_number": "ABC123"}).get_json()["application"]
    assert [h["to_status"] for h in r["history"]] == ["interested", "preparing_documents", "applied"]
    assert r["status_source"] == "user"
    note = api.post(f"/api/v1/applications/{a['id']}/notes", {"body": "Called the office"}).get_json()["note"]
    assert api.delete(f"/api/v1/applications/{a['id']}/notes/{note['id']}").status_code == 200


def test_users_cannot_touch_each_others_data(api, client, db, seeded):
    api.register()
    oid = opp_id(db, "demo-summer-software-internship")
    a = api.post("/api/v1/applications", {"opportunity_id": oid}).get_json()["application"]
    api.post("/api/v1/auth/logout")
    api.register(email="other@example.com")
    assert api.get(f"/api/v1/applications/{a['id']}").status_code == 404
    assert api.delete(f"/api/v1/applications/{a['id']}").status_code == 404


def test_document_upload_validation_and_checklist(api, db, seeded):
    api.register()
    from app.models import DocumentType

    resume = db.session.scalar(sa.select(DocumentType.id).where(DocumentType.slug == "resume"))
    fake = api.c.post("/api/v1/documents", data={"document_type_id": resume,
                                                 "file": (io.BytesIO(b"MZ fake exe"), "cv.pdf")},
                      headers=api._headers("/api/v1/documents"), content_type="multipart/form-data")
    assert fake.status_code == 422  # extension says PDF, bytes say otherwise

    pdf = io.BytesIO(b"%PDF-1.4\n%demo\n")
    ok = api.c.post("/api/v1/documents", data={"document_type_id": resume, "file": (pdf, "cv.pdf")},
                    headers=api._headers("/api/v1/documents"), content_type="multipart/form-data")
    assert ok.status_code == 201
    doc = ok.get_json()["document"]
    f = api.get(f"/api/v1/documents/{doc['id']}/file")
    assert f.status_code == 200 and f.data.startswith(b"%PDF") and f.headers["Cache-Control"] == "private, no-store"

    oid = opp_id(db, "demo-summer-software-internship")
    cl = api.get(f"/api/v1/documents/checklist/{oid}").get_json()
    statuses = {i["document_type"]["slug"]: i["status"] for i in cl["items"]}
    assert statuses == {"resume": "ready", "bonafide-certificate": "missing"}

    assert api.delete(f"/api/v1/documents/{doc['id']}").status_code == 200
    assert api.get(f"/api/v1/documents/{doc['id']}/file").status_code == 404


def test_dashboard_and_deadline_notifications(api, db, seeded):
    api.register()
    oid = opp_id(db, "demo-merit-cum-means-scholarship")  # deadline in 6 days
    api.post("/api/v1/saved", {"opportunity_id": oid})
    d = api.get("/api/v1/dashboard").get_json()
    assert d["stats"]["saved"] == 1 and len(d["weekly_activity"]) == 7
    n1 = api.get("/api/v1/notifications").get_json()
    n2 = api.get("/api/v1/notifications").get_json()
    deadline_notes = [n for n in n2["items"] if n["type"] == "deadline"]
    assert len(deadline_notes) == 1 and n1["unread"] == n2["unread"]  # no duplicates on repeat sync


# ------------------------------------------------------------------ admin
ADMIN_PAYLOAD = {
    "title": "Test Official Scholarship", "summary": "A test record entered by an admin.",
    "description": "Long description of the test record.", "category_id": 1,
    "organization_name": "Test Department", "organization_type": "state_government",
    "eligibility_summary": "Residents of Kerala.", "benefits": "Rs 1,000",
    "source_url": "https://example.gov.in/notification.pdf", "deadline": "2099-01-01",
    "criteria": [{"criterion_type": "state_domicile", "value": {"any_of": ["kerala"]}, "description": "Kerala residents",
                  "source_excerpt": "The applicant should be a native of Kerala."},
                 {"criterion_type": "income_max", "value": {"amount": 100000}, "description": "Income up to 1 lakh"}],
    "required_documents": [{"document_type_id": 1}], "dates": [],
}


def test_admin_rbac(api):
    api.register()
    assert api.get("/api/v1/admin/stats").status_code == 403
    assert api.post("/api/v1/admin/opportunities", ADMIN_PAYLOAD).status_code == 403


def test_admin_create_verify_publish(api, db, seeded):
    ensure_admin("admin@example.com", "adminpass1")
    api.post("/api/v1/auth/login", {"email": "admin@example.com", "password": "adminpass1"})
    o = api.post("/api/v1/admin/opportunities", ADMIN_PAYLOAD).get_json()["opportunity"]
    assert o["states"] == ["kerala"] and o["income_ceiling"] == 100000  # derived from criteria
    oid = o["id"]
    blocked = api.post(f"/api/v1/admin/opportunities/{oid}/status", {"action": "publish"})
    assert blocked.status_code == 409  # official data must be verified first
    assert api.post(f"/api/v1/admin/opportunities/{oid}/status", {"action": "verify"}).status_code == 200
    assert api.post(f"/api/v1/admin/opportunities/{oid}/status", {"action": "publish"}).status_code == 200
    detail = api.get(f"/api/v1/admin/opportunities/{oid}").get_json()["opportunity"]
    assert detail["verification_status"] == "verified" and detail["last_verified_at"]
    assert [l["action"] for l in detail["logs"]][:2] == ["published", "verified"]

    demo_id = opp_id(db, "demo-rural-policy-fellowship")
    assert api.post(f"/api/v1/admin/opportunities/{demo_id}/status", {"action": "verify"}).status_code == 409
    assert api.get("/api/v1/admin/stats").get_json()["opportunities"]["demo"] >= 10


def test_corrections_flow_notifies_reporter(api, db, seeded):
    api.register()
    oid = opp_id(db, "demo-rural-policy-fellowship")
    assert api.post(f"/api/v1/opportunities/{oid}/corrections",
                    {"field": "deadline", "message": "The deadline on the official site is different."}).status_code == 201
    api.post("/api/v1/auth/logout")
    ensure_admin("admin@example.com", "adminpass1")
    api.post("/api/v1/auth/login", {"email": "admin@example.com", "password": "adminpass1"})
    c = api.get("/api/v1/admin/corrections?status=open").get_json()["items"][0]
    api.patch(f"/api/v1/admin/corrections/{c['id']}", {"status": "accepted", "admin_note": "Fixed, thanks"})
    api.post("/api/v1/auth/logout")
    api.post("/api/v1/auth/login", {"email": "asha@example.com", "password": "secret123"})
    notes = api.get("/api/v1/notifications").get_json()["items"]
    assert any(n["type"] == "correction_update" for n in notes)


def test_meta_and_health(client, seeded):
    m = client.get("/api/v1/meta").get_json()
    assert len(m["states"]) == 36 and m["features"]["ai"] is False
    assert any(p["url"] == "https://scholarships.gov.in" for p in m["portals"])
    h = client.get("/api/v1/health")
    assert h.headers["X-Content-Type-Options"] == "nosniff"
