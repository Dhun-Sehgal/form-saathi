import pytest

from app import create_app
from app.extensions import db as _db


@pytest.fixture()
def app(tmp_path):
    app = create_app("testing")
    app.config["UPLOAD_DIR"] = str(tmp_path / "uploads")
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def db(app):
    return _db


@pytest.fixture()
def client(app):
    return app.test_client()


class Api:
    """Test helper that behaves like the frontend: sends the CSRF header from the cookie."""

    def __init__(self, client):
        self.c = client

    def _headers(self, url):
        name = "csrf_refresh_token" if url.endswith("/auth/refresh") else "csrf_access_token"
        cookie = self.c.get_cookie(name)
        return {"X-CSRF-TOKEN": cookie.value} if cookie else {}

    def get(self, url, **kw):
        return self.c.get(url, **kw)

    def post(self, url, json=None, **kw):
        return self.c.post(url, json=json, headers=self._headers(url), **kw)

    def put(self, url, json=None):
        return self.c.put(url, json=json, headers=self._headers(url))

    def patch(self, url, json=None):
        return self.c.patch(url, json=json, headers=self._headers(url))

    def delete(self, url, json=None):
        return self.c.delete(url, json=json, headers=self._headers(url))

    def register(self, email="asha@example.com", password="secret123", name="Asha Patil"):
        return self.post("/api/v1/auth/register",
                         {"email": email, "password": password, "full_name": name, "accept_terms": True})


@pytest.fixture()
def api(client):
    return Api(client)


@pytest.fixture()
def seeded(app):
    from app.seed.demo import seed_demo

    seed_demo()
    return app
