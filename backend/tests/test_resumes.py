"""ATS resume builder API."""
from app.api.resumes import MAX_RESUMES

SAMPLE = {
    "basics": {"name": "Asha Patil", "email": "asha@example.com", "links": [{"label": "GitHub", "url": "https://github.com/asha"}]},
    "summary": "Data science student.",
    "experience": [{"role": "Intern", "org": "Acme", "start": "Jun 2026", "end": "Aug 2026",
                    "bullets": ["Built a dashboard used by 12 analysts"]}],
    "skills": [{"group": "Languages", "items": "Python, SQL"}],
}


def test_create_from_profile_uses_only_known_data(api):
    api.register()
    api.put("/api/v1/profile", {"institution": "IIT Madras", "course": "B.S. Data Science", "marks_type": "cgpa",
                                "marks_value": 7.7, "skills": ["Python", "SQL"]})
    r = api.post("/api/v1/resumes", {"title": "My resume", "from_profile": True})
    assert r.status_code == 201
    data = r.get_json()["resume"]["data"]
    assert data["basics"]["name"] == "Asha Patil" and data["basics"]["email"] == "asha@example.com"
    assert data["education"][0]["school"] == "IIT Madras" and data["education"][0]["score"] == "CGPA: 7.7"
    assert data["skills"][0]["items"] == "Python, SQL"
    assert data["experience"] == [] and data["summary"] == ""  # nothing invented


def test_crud_duplicate_and_ownership(api):
    api.register()
    rid = api.post("/api/v1/resumes", {"title": "SDE", "data": SAMPLE}).get_json()["resume"]["id"]
    upd = api.put(f"/api/v1/resumes/{rid}", {"title": "SDE v2", "template": "modern", "data": SAMPLE}).get_json()["resume"]
    assert upd["title"] == "SDE v2" and upd["template"] == "modern"
    assert upd["data"]["experience"][0]["bullets"] == ["Built a dashboard used by 12 analysts"]
    dup = api.post(f"/api/v1/resumes/{rid}/duplicate").get_json()["resume"]
    assert dup["title"] == "SDE v2 (copy)"
    assert len(api.get("/api/v1/resumes").get_json()["items"]) == 2

    api.post("/api/v1/auth/logout")
    api.register(email="other@example.com")
    assert api.get(f"/api/v1/resumes/{rid}").status_code == 404
    assert api.delete(f"/api/v1/resumes/{rid}").status_code == 404


def test_validation_and_limit(api):
    api.register()
    bad = api.post("/api/v1/resumes", {"title": "x", "template": "fancy"})
    assert bad.status_code == 422
    too_many_bullets = dict(SAMPLE, experience=[dict(SAMPLE["experience"][0], bullets=["b"] * 9)])
    assert api.post("/api/v1/resumes", {"title": "x", "data": too_many_bullets}).status_code == 422
    for i in range(MAX_RESUMES):
        assert api.post("/api/v1/resumes", {"title": f"r{i}"}).status_code == 201
    assert api.post("/api/v1/resumes", {"title": "one too many"}).status_code == 409


def test_improve_bullet_reports_ai_not_configured(api):
    api.register()
    r = api.post("/api/v1/resumes/improve-bullet", {"bullet": "made a website for college"})
    assert r.status_code == 503 and r.get_json()["error"]["code"] == "ai_not_configured"


def test_account_deletion_removes_resumes(api, db):
    import sqlalchemy as sa
    from app.models import Resume

    api.register()
    api.post("/api/v1/resumes", {"title": "SDE", "data": SAMPLE})
    api.delete("/api/v1/profile/account", {"password": "secret123"})
    assert db.session.scalar(sa.select(sa.func.count(Resume.id))) == 0
