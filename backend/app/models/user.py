"""Identity, profile and auth-token tables."""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db
from .base import (
    EDUCATION_LEVELS, GENDERS, INCOME_RANGES, LANGUAGES, MARKS_TYPES,
    SOCIAL_CATEGORIES, STATE_TYPES, USER_ROLES, CreatedAtMixin, JSONType,
    TimestampMixin, str_enum,
)

# Many-to-many: categories a user is interested in.
profile_interest_categories = sa.Table(
    "profile_interest_categories",
    db.metadata,
    sa.Column("user_id", sa.ForeignKey("user_profiles.user_id", ondelete="CASCADE"), primary_key=True),
    sa.Column("category_id", sa.ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True),
)


class State(db.Model):
    """Indian states and union territories (reference data)."""

    __tablename__ = "states"

    code: Mapped[str] = mapped_column(sa.String(40), primary_key=True)  # slug, e.g. "maharashtra"
    name: Mapped[str] = mapped_column(sa.String(80), unique=True)
    kind: Mapped[str] = mapped_column(str_enum(STATE_TYPES, "state_kind"))


class User(TimestampMixin, db.Model):
    __tablename__ = "users"
    __table_args__ = (sa.CheckConstraint("email = lower(email)", name="email_lowercase"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(sa.String(254), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(sa.String(255))
    role: Mapped[str] = mapped_column(str_enum(USER_ROLES, "user_role"), default="user", server_default="user")
    is_active: Mapped[bool] = mapped_column(default=True, server_default=sa.true())
    email_verified_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))
    last_login_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))
    failed_login_attempts: Mapped[int] = mapped_column(sa.SmallInteger, default=0, server_default="0")
    locked_until: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))

    profile: Mapped[UserProfile | None] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    def __repr__(self) -> str:
        return f"<User {self.id} {self.role}>"


class UserProfile(TimestampMixin, db.Model):
    """Personalisation data. Every sensitive field is optional (nullable)."""

    __tablename__ = "user_profiles"
    __table_args__ = (
        sa.CheckConstraint("current_year IS NULL OR current_year BETWEEN 1 AND 10", name="current_year_range"),
        sa.CheckConstraint(
            "marks_value IS NULL OR (marks_type = 'percentage' AND marks_value BETWEEN 0 AND 100)"
            " OR (marks_type = 'cgpa' AND marks_value BETWEEN 0 AND 10)",
            name="marks_range",
        ),
        sa.CheckConstraint("onboarding_step BETWEEN 0 AND 5", name="onboarding_step_range"),
    )

    user_id: Mapped[int] = mapped_column(sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    full_name: Mapped[str | None] = mapped_column(sa.String(120))
    date_of_birth: Mapped[date | None]
    gender: Mapped[str | None] = mapped_column(str_enum(GENDERS, "gender"))
    state_code: Mapped[str | None] = mapped_column(sa.ForeignKey("states.code", ondelete="SET NULL"), index=True)
    city: Mapped[str | None] = mapped_column(sa.String(80))

    education_level: Mapped[str | None] = mapped_column(str_enum(EDUCATION_LEVELS, "education_level"), index=True)
    institution: Mapped[str | None] = mapped_column(sa.String(160))
    course: Mapped[str | None] = mapped_column(sa.String(120))
    stream: Mapped[str | None] = mapped_column(sa.String(120))
    current_year: Mapped[int | None] = mapped_column(sa.SmallInteger)
    marks_type: Mapped[str | None] = mapped_column(str_enum(MARKS_TYPES, "marks_type"))
    marks_value: Mapped[Decimal | None] = mapped_column(sa.Numeric(5, 2))

    # Optional, explained in the UI, used only for eligibility matching.
    income_range: Mapped[str | None] = mapped_column(str_enum(INCOME_RANGES, "income_range"))
    social_category: Mapped[str | None] = mapped_column(str_enum(SOCIAL_CATEGORIES, "social_category"))
    has_disability: Mapped[bool | None]

    skills: Mapped[list] = mapped_column(JSONType, default=list)
    career_interests: Mapped[list] = mapped_column(JSONType, default=list)
    preferred_language: Mapped[str] = mapped_column(str_enum(LANGUAGES, "language"), default="en", server_default="en")

    onboarding_step: Mapped[int] = mapped_column(sa.SmallInteger, default=0, server_default="0")
    onboarding_completed_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))

    user: Mapped[User] = relationship(back_populates="profile")
    state: Mapped[State | None] = relationship()
    interests: Mapped[list["Category"]] = relationship(secondary=profile_interest_categories)  # noqa: F821


class UserToken(CreatedAtMixin, db.Model):
    """Single-use tokens for password reset and email verification. Only a SHA-256 hash is stored."""

    __tablename__ = "user_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(sa.ForeignKey("users.id", ondelete="CASCADE"), index=True)
    purpose: Mapped[str] = mapped_column(str_enum(("reset_password", "verify_email"), "token_purpose"))
    token_hash: Mapped[str] = mapped_column(sa.String(64), unique=True)
    expires_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True))
    used_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))


class RevokedToken(CreatedAtMixin, db.Model):
    """JWT IDs revoked at logout. Rows past expires_at are purged by the worker."""

    __tablename__ = "revoked_tokens"

    jti: Mapped[str] = mapped_column(sa.String(36), primary_key=True)
    expires_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), index=True)
