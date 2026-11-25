"""Saathi AI chat history and eligibility check results."""
from __future__ import annotations

import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db
from .base import (
    CHAT_ROLES, ELIGIBILITY_VERDICTS, EXPLANATION_SOURCES, LANGUAGES,
    CreatedAtMixin, JSONType, TimestampMixin, str_enum,
)


class ChatSession(TimestampMixin, db.Model):
    __tablename__ = "chat_sessions"
    __table_args__ = (sa.Index("ix_chat_sessions_user_updated", "user_id", "updated_at"),)

    id: Mapped[str] = mapped_column(sa.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[int] = mapped_column(sa.ForeignKey("users.id", ondelete="CASCADE"))
    # Optional grounding: the chat was started from this opportunity's page.
    opportunity_id: Mapped[int | None] = mapped_column(sa.ForeignKey("opportunities.id", ondelete="SET NULL"))
    title: Mapped[str] = mapped_column(sa.String(120), default="New conversation")
    language: Mapped[str] = mapped_column(str_enum(LANGUAGES, "chat_language"), default="en")

    messages: Mapped[list[ChatMessage]] = relationship(
        back_populates="session", cascade="all, delete-orphan", order_by="ChatMessage.id"
    )


class ChatMessage(CreatedAtMixin, db.Model):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[str] = mapped_column(sa.ForeignKey("chat_sessions.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(str_enum(CHAT_ROLES, "chat_role"))
    content: Mapped[str] = mapped_column(sa.Text)
    model: Mapped[str | None] = mapped_column(sa.String(80))
    input_tokens: Mapped[int | None]
    output_tokens: Mapped[int | None]

    session: Mapped[ChatSession] = relationship(back_populates="messages")


class EligibilityCheck(CreatedAtMixin, db.Model):
    """Result of the deterministic rule engine (+ optional AI explanation).

    profile_hash / criteria_hash let us reuse a result until the profile or the
    opportunity's rules change.
    """

    __tablename__ = "eligibility_checks"
    __table_args__ = (sa.Index("ix_eligibility_checks_lookup", "user_id", "opportunity_id", "created_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(sa.ForeignKey("users.id", ondelete="CASCADE"))
    opportunity_id: Mapped[int] = mapped_column(sa.ForeignKey("opportunities.id", ondelete="CASCADE"))
    verdict: Mapped[str] = mapped_column(str_enum(ELIGIBILITY_VERDICTS, "eligibility_verdict"))
    results: Mapped[list] = mapped_column(JSONType)  # [{criterion_id, outcome, reason}]
    explanation: Mapped[dict | None] = mapped_column(JSONType)
    explanation_source: Mapped[str] = mapped_column(
        str_enum(EXPLANATION_SOURCES, "explanation_source"), default="template"
    )
    profile_hash: Mapped[str] = mapped_column(sa.String(64))
    criteria_hash: Mapped[str] = mapped_column(sa.String(64))
