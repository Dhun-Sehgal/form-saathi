"""Configuration classes. All secrets come from environment variables."""
import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # backend/
REPO_DIR = BASE_DIR.parent


def _bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def _database_url() -> str:
    url = os.getenv("DATABASE_URL", "sqlite:///formsaathi_dev.db")
    # Hosting providers hand out postgres:// URLs; SQLAlchemy + psycopg 3 needs this prefix.
    if url.startswith("postgres://"):
        url = "postgresql+psycopg://" + url[len("postgres://"):]
    elif url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-insecure-key-change-me-0123456789")
    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    UPLOAD_DIR = os.getenv("UPLOAD_DIR", str(BASE_DIR / "instance" / "uploads"))
    MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "5"))
    MAX_CONTENT_LENGTH = (MAX_UPLOAD_MB + 1) * 1024 * 1024  # small headroom for multipart overhead
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
    STATIC_DIR = os.getenv("STATIC_DIR", str(REPO_DIR / "frontend" / "dist"))
    SHARED_DIR = os.getenv("SHARED_DIR", str(REPO_DIR / "shared"))

    # --- Auth: JWT in HttpOnly cookies + double-submit CSRF
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-only-insecure-jwt-key-change-me-0123456789")
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=14)
    JWT_COOKIE_SECURE = _bool("COOKIE_SECURE", False)
    JWT_COOKIE_SAMESITE = "Lax"
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_SESSION_COOKIE = False

    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", "memory://")
    RATELIMIT_HEADERS_ENABLED = True

    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "anthropic")
    LLM_API_KEY = os.getenv("LLM_API_KEY", "")
    LLM_MODEL = os.getenv("LLM_MODEL", "") or "claude-opus-5-5"

    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_USE_TLS = _bool("SMTP_USE_TLS", True)
    MAIL_FROM = os.getenv("MAIL_FROM", "FormSaathi <no-reply@formsaathi.local>")


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")
    SQLALCHEMY_ENGINE_OPTIONS = {}
    LLM_API_KEY = ""
    SMTP_HOST = ""
    RATELIMIT_ENABLED = False


class ProductionConfig(BaseConfig):
    DEBUG = False
    JWT_COOKIE_SECURE = _bool("COOKIE_SECURE", True)


CONFIGS = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
