"""FormSaathi Flask application factory."""
import logging
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, g, request, send_from_directory

from .config import CONFIGS
from .extensions import db, jwt, limiter, migrate


def create_app(config_name: str | None = None) -> Flask:
    load_dotenv()
    config_name = config_name or os.getenv("FLASK_ENV", "development")

    app = Flask(__name__, instance_relative_config=True, static_folder=None)
    app.config.from_object(CONFIGS.get(config_name, CONFIGS["development"]))

    logging.basicConfig(
        level=logging.DEBUG if app.debug else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    if config_name == "production" and app.config["SECRET_KEY"].startswith("dev-only"):
        raise RuntimeError("Set SECRET_KEY and JWT_SECRET_KEY environment variables in production.")

    db.init_app(app)
    from . import models  # noqa: F401  (register models with SQLAlchemy metadata)

    migrate.init_app(app, db, render_as_batch=True)  # batch mode keeps SQLite migrations working
    jwt.init_app(app)
    limiter.init_app(app)

    from .api import admin, ai, auth, documents, meta, opportunities, profile, resumes, tracker
    from .utils.errors import register_error_handlers

    for module in (auth, profile, meta, opportunities, ai, documents, tracker, resumes, admin):
        app.register_blueprint(module.bp)
    auth.register_jwt_callbacks(jwt)
    register_error_handlers(app)

    from .seed import register_cli

    register_cli(app)
    _register_request_logging(app)
    _register_security_headers(app)
    _register_spa(app)
    return app


def _register_request_logging(app: Flask) -> None:
    log = logging.getLogger("formsaathi.request")

    @app.before_request
    def _start():
        g._t0 = time.perf_counter()

    @app.after_request
    def _log(resp):
        if request.path.startswith("/api/"):
            ms = (time.perf_counter() - g.get("_t0", time.perf_counter())) * 1000
            log.info("%s %s %s %.0fms", request.method, request.path, resp.status_code, ms)  # no bodies, no PII
        return resp


def _register_security_headers(app: Flask) -> None:
    @app.after_request
    def _headers(resp):
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("X-Frame-Options", "DENY")
        resp.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        resp.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        if not app.debug:
            resp.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        if not request.path.startswith("/api/"):
            resp.headers.setdefault(
                "Content-Security-Policy",
                "default-src 'self'; img-src 'self' data: blob:; style-src 'self' 'unsafe-inline'; "
                "font-src 'self' data:; script-src 'self'; connect-src 'self'; frame-src 'self'; "
                "object-src 'none'; base-uri 'self'; frame-ancestors 'none'",
            )
        if request.path.startswith("/api/"):
            resp.headers.setdefault("Cache-Control", "no-store")
        return resp


def _register_spa(app: Flask) -> None:
    """Serve the built Vue app (frontend/dist) from the same origin as the API."""
    dist = Path(app.config["STATIC_DIR"])

    @app.get("/", defaults={"path": ""})
    @app.get("/<path:path>")
    def spa(path):
        if path.startswith("api/"):
            from .utils.errors import not_found

            raise not_found("Endpoint")
        if not (dist / "index.html").exists():
            return ("FormSaathi API is running. Build the frontend (cd frontend && npm run build) "
                    "or run the Vite dev server on port 5173."), 200
        target = (dist / path).resolve()
        if path and target.is_file() and dist.resolve() in target.parents:
            resp = send_from_directory(dist, path)
            if path.startswith("assets/"):
                resp.headers["Cache-Control"] = "public, max-age=31536000, immutable"
            return resp
        return send_from_directory(dist, "index.html", max_age=0)
