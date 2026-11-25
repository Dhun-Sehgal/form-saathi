"""Admin workflow tables: verification audit log, user corrections, announcements, feedback."""
from __future__ import annotations

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db
from .base import (
    ANNOUNCEMENT_AUDIENCES, ANNOUNCEMENT_LEVELS, CORRECTION_FIELDS, CORRECTION_STATUSES,
    FEEDBACK_KINDS, FEEDBACK_STATUSES, VERIFICATION_ACTIONS, VERIFICATION_STATUSES,
    CreatedAtMixin, TimestampMixin, str_enum,
)


class SourceVerificationLog(CreatedAtMixin, db.Model):
    """Append-only audit trail of every verification / status change on an opportunity."""

    __tablename__ = "source_verification_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    opportunity_id: Mapped[int] = mapped_column(sa.ForeignKey("opportunities.id", ondelete="CASCADE"), index=True)
    actor_id: Mapped[int | None] = mapped_column(sa.ForeignKey("users.id", ondelete="SET NULL"))  # NULL = system job
    action: Mapped[str] = mapped_column(str_enum(VERIFICATION_ACTIONS, "verification_action"))
    from_status: Mapped[str | None] = mapped_column(str_enum(VERIFICATION_STATUSES, "log_from_status"))
    to_status: Mapped[str | None] = mapped_column(str_enum(VERIFICATION_STATUSES, "log_to_status"))
    source_url_checked: Mapped[str | None] = mapped_column(sa.String(500))
    notes: Mapped[str | None] = mapped_column(sa.Text)


class CorrectionReport(TimestampMixin, db.Model):
    """A user's suggestion that an opportunity record is wrong. Users can't edit records directly."""

    __tablename__ = "correction_reports"
    __table_args__ = (sa.Index("ix_correction_reports_status", "status", "created_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    opportunity_id: Mapped[int] = mapped_column(sa.ForeignKey("opportunities.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int | None] = mapped_column(sa.ForeignKey("users.id", ondelete="SET NULL"))
    field: Mapped[str] = mapped_column(str_enum(CORRECTION_FIELDS, "correction_field"))
    message: Mapped[str] = mapped_column(sa.Text)
    suggested_source_url: Mapped[str | None] = mapped_column(sa.String(500))
    status: Mapped[str] = mapped_column(
        str_enum(CORRECTION_STATUSES, "correction_status"), default="open", server_default="open"
    )
    admin_note: Mapped[str | None] = mapped_column(sa.Text)
    reviewed_by_id: Mapped[int | None] = mapped_column(sa.ForeignKey("users.id", ondelete="SET NULL"))
    reviewed_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))

    opportunity: Mapped["Opportunity"] = relationship()  # noqa: F821


class Announcement(TimestampMixin, db.Model):
    __tablename__ = "announcements"
    __table_args__ = (
        sa.CheckConstraint("ends_at IS NULL OR starts_at IS NULL OR ends_at > starts_at", name="window_order"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(sa.String(160))
    body: Mapped[str] = mapped_column(sa.Text)
    audience: Mapped[str] = mapped_column(str_enum(ANNOUNCEMENT_AUDIENCES, "announcement_audience"), default="all")
    level: Mapped[str] = mapped_column(str_enum(ANNOUNCEMENT_LEVELS, "announcement_level"), default="info")
    starts_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))
    ends_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(default=True, server_default=sa.true())
    created_by_id: Mapped[int | None] = mapped_column(sa.ForeignKey("users.id", ondelete="SET NULL"))


class Feedback(CreatedAtMixin, db.Model):
    """In-app feedback and the public contact form."""

    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(sa.ForeignKey("users.id", ondelete="SET NULL"))
    contact_email: Mapped[str | None] = mapped_column(sa.String(254))  # only for logged-out contact form
    kind: Mapped[str] = mapped_column(str_enum(FEEDBACK_KINDS, "feedback_kind"))
    message: Mapped[str] = mapped_column(sa.Text)
    page: Mapped[str | None] = mapped_column(sa.String(200))
    status: Mapped[str] = mapped_column(str_enum(FEEDBACK_STATUSES, "feedback_status"), default="new")
