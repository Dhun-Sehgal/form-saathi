"""What a user does with opportunities: save, collect, track, note, remind."""
from __future__ import annotations

from datetime import date, datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db
from .base import (
    APPLICATION_STATUSES, REMINDER_CHANNELS, STATUS_SOURCES, CreatedAtMixin,
    TimestampMixin, str_enum,
)


class Collection(TimestampMixin, db.Model):
    """User-named bookmark folders, e.g. 'Final year', 'Summer internships'."""

    __tablename__ = "collections"
    __table_args__ = (sa.UniqueConstraint("user_id", "name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(sa.ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(sa.String(60))


class SavedOpportunity(CreatedAtMixin, db.Model):
    __tablename__ = "saved_opportunities"
    __table_args__ = (sa.UniqueConstraint("user_id", "opportunity_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(sa.ForeignKey("users.id", ondelete="CASCADE"), index=True)
    opportunity_id: Mapped[int] = mapped_column(sa.ForeignKey("opportunities.id", ondelete="CASCADE"), index=True)
    collection_id: Mapped[int | None] = mapped_column(sa.ForeignKey("collections.id", ondelete="SET NULL"))

    opportunity: Mapped["Opportunity"] = relationship()  # noqa: F821


class Application(TimestampMixin, db.Model):
    """A user's tracked application. Status is user-confirmed unless status_source says otherwise."""

    __tablename__ = "applications"
    __table_args__ = (
        sa.UniqueConstraint("user_id", "opportunity_id"),
        sa.Index("ix_applications_user_status", "user_id", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(sa.ForeignKey("users.id", ondelete="CASCADE"))
    opportunity_id: Mapped[int] = mapped_column(sa.ForeignKey("opportunities.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(
        str_enum(APPLICATION_STATUSES, "application_status"), default="interested", server_default="interested"
    )
    status_source: Mapped[str] = mapped_column(
        str_enum(STATUS_SOURCES, "status_source"), default="user", server_default="user"
    )
    applied_on: Mapped[date | None]
    reference_number: Mapped[str | None] = mapped_column(sa.String(80))  # entered by the user

    opportunity: Mapped["Opportunity"] = relationship()  # noqa: F821
    history: Mapped[list[ApplicationStatusHistory]] = relationship(
        back_populates="application", cascade="all, delete-orphan",
        order_by="ApplicationStatusHistory.created_at",
    )
    notes: Mapped[list[ApplicationNote]] = relationship(
        back_populates="application", cascade="all, delete-orphan", order_by="ApplicationNote.created_at.desc()"
    )


class ApplicationStatusHistory(CreatedAtMixin, db.Model):
    __tablename__ = "application_status_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(sa.ForeignKey("applications.id", ondelete="CASCADE"), index=True)
    from_status: Mapped[str | None] = mapped_column(str_enum(APPLICATION_STATUSES, "history_from_status"))
    to_status: Mapped[str] = mapped_column(str_enum(APPLICATION_STATUSES, "history_to_status"))
    source: Mapped[str] = mapped_column(str_enum(STATUS_SOURCES, "history_source"), default="user")
    note: Mapped[str | None] = mapped_column(sa.String(300))

    application: Mapped[Application] = relationship(back_populates="history")


class ApplicationNote(TimestampMixin, db.Model):
    __tablename__ = "application_notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(sa.ForeignKey("applications.id", ondelete="CASCADE"), index=True)
    body: Mapped[str] = mapped_column(sa.Text)

    application: Mapped[Application] = relationship(back_populates="notes")


class Reminder(TimestampMixin, db.Model):
    """Personal reminders. The worker picks up due rows (remind_at <= now AND sent_at IS NULL)."""

    __tablename__ = "reminders"
    __table_args__ = (sa.Index("ix_reminders_due", "sent_at", "remind_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(sa.ForeignKey("users.id", ondelete="CASCADE"), index=True)
    application_id: Mapped[int | None] = mapped_column(sa.ForeignKey("applications.id", ondelete="CASCADE"))
    opportunity_id: Mapped[int | None] = mapped_column(sa.ForeignKey("opportunities.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(sa.String(160))
    remind_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True))
    channel: Mapped[str] = mapped_column(str_enum(REMINDER_CHANNELS, "reminder_channel"), default="in_app")
    sent_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))
    is_done: Mapped[bool] = mapped_column(default=False, server_default=sa.false())
