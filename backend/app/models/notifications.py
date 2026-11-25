"""In-app notifications and per-user preferences."""
from __future__ import annotations

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from ..extensions import db
from .base import NOTIFICATION_TYPES, CreatedAtMixin, TimestampMixin, str_enum


class Notification(CreatedAtMixin, db.Model):
    __tablename__ = "notifications"
    __table_args__ = (
        # dedupe_key (e.g. "deadline:42:7d") stops the worker sending the same reminder twice.
        sa.UniqueConstraint("user_id", "dedupe_key"),
        sa.Index("ix_notifications_user_unread", "user_id", "is_read", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(sa.ForeignKey("users.id", ondelete="CASCADE"))
    type: Mapped[str] = mapped_column(str_enum(NOTIFICATION_TYPES, "notification_type"))
    title: Mapped[str] = mapped_column(sa.String(160))
    body: Mapped[str | None] = mapped_column(sa.String(500))
    link: Mapped[str | None] = mapped_column(sa.String(300))  # in-app route
    dedupe_key: Mapped[str | None] = mapped_column(sa.String(120))
    is_read: Mapped[bool] = mapped_column(default=False, server_default=sa.false())
    read_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))
    emailed_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))


class NotificationPreference(TimestampMixin, db.Model):
    __tablename__ = "notification_preferences"
    __table_args__ = (sa.CheckConstraint("deadline_days_before BETWEEN 1 AND 60", name="days_before_range"),)

    user_id: Mapped[int] = mapped_column(sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    email_enabled: Mapped[bool] = mapped_column(default=True, server_default=sa.true())
    deadline_reminders: Mapped[bool] = mapped_column(default=True, server_default=sa.true())
    deadline_days_before: Mapped[int] = mapped_column(sa.SmallInteger, default=7, server_default="7")
    document_reminders: Mapped[bool] = mapped_column(default=True, server_default=sa.true())
    status_reminders: Mapped[bool] = mapped_column(default=True, server_default=sa.true())
    opportunity_updates: Mapped[bool] = mapped_column(default=True, server_default=sa.true())
    weekly_digest: Mapped[bool] = mapped_column(default=False, server_default=sa.false())
