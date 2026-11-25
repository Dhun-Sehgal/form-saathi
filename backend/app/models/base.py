"""Shared column helpers, mixins and enumerations.

Enumerations are stored as VARCHAR + CHECK constraint (native_enum=False). This keeps
migrations simple (adding a value = editing a CHECK, not ALTER TYPE) and works on
both PostgreSQL and SQLite.
"""
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

# JSONB on PostgreSQL, JSON elsewhere.
JSONType = sa.JSON().with_variant(JSONB(), "postgresql")


def str_enum(values: tuple[str, ...], name: str) -> sa.Enum:
    return sa.Enum(
        *values,
        name=name,
        native_enum=False,
        create_constraint=True,
        validate_strings=True,
        length=max(len(v) for v in values),
    )


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False
    )


class CreatedAtMixin:
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
    )


# ---------------------------------------------------------------- enumerations
# Kept here so the API layer and frontend (via /meta) share one definition.

USER_ROLES = ("user", "admin")
LANGUAGES = ("en", "hi", "mr")
GENDERS = ("female", "male", "other", "prefer_not_say")
EDUCATION_LEVELS = (
    "class_10", "class_12", "diploma", "iti", "undergraduate",
    "postgraduate", "doctorate", "not_studying", "other",
)
MARKS_TYPES = ("percentage", "cgpa")
# Bands chosen to line up with common income cut-offs used by Indian schemes (1L / 2.5L / 5L / 8L).
INCOME_RANGES = ("below_1l", "1l_to_2_5l", "2_5l_to_5l", "5l_to_8l", "above_8l", "prefer_not_say")
SOCIAL_CATEGORIES = ("general", "ews", "obc", "sc", "st", "prefer_not_say")
STATE_TYPES = ("state", "union_territory")

ORG_TYPES = (
    "central_government", "state_government", "university", "psu",
    "private", "ngo", "international", "other",
)
VERIFICATION_STATUSES = ("pending_verification", "verified", "expired", "archived")
PUBLICATION_STATUSES = ("draft", "published", "unpublished")
DATA_ORIGINS = ("official", "demo")
APPLICATION_MODES = ("online", "offline", "both")
OPPORTUNITY_SCOPES = ("national", "state", "institution")
BENEFIT_FREQUENCIES = ("one_time", "annual", "monthly", "stipend", "other")

CRITERION_TYPES = (
    "age_min", "age_max", "education_level", "course", "year_of_study",
    "marks_min_percentage", "marks_min_cgpa", "income_max", "state_domicile",
    "social_category", "gender", "disability", "custom",
)
DOCUMENT_SENSITIVITY = ("high", "normal")

APPLICATION_STATUSES = (
    "interested", "saved", "preparing_documents", "ready_to_apply",
    "applied", "under_review", "approved", "rejected",
)
STATUS_SOURCES = ("user", "integration", "system")
REMINDER_CHANNELS = ("in_app", "email", "both")

UPLOAD_STATUSES = ("uploaded", "needs_attention")

CHAT_ROLES = ("user", "assistant")
ELIGIBILITY_VERDICTS = ("eligible", "possibly_eligible", "not_eligible")
EXPLANATION_SOURCES = ("template", "ai")

NOTIFICATION_TYPES = (
    "deadline", "document_missing", "status_reminder", "opportunity_update",
    "correction_update", "announcement", "reminder", "system",
)
VERIFICATION_ACTIONS = (
    "verified", "marked_pending", "marked_expired", "archived",
    "source_updated", "published", "unpublished",
)
CORRECTION_FIELDS = ("deadline", "eligibility", "benefits", "documents", "link", "other")
CORRECTION_STATUSES = ("open", "accepted", "rejected")
ANNOUNCEMENT_AUDIENCES = ("all", "users", "admins")
ANNOUNCEMENT_LEVELS = ("info", "important")
FEEDBACK_KINDS = ("bug", "idea", "praise", "contact", "other")
FEEDBACK_STATUSES = ("new", "read", "closed")
