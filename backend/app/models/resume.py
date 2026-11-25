"""Resumes built with the ATS resume builder. The content is one JSON document per resume."""
from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from ..extensions import db
from .base import JSONType, TimestampMixin, str_enum

RESUME_TEMPLATES = ("classic", "modern")


class Resume(TimestampMixin, db.Model):
    __tablename__ = "resumes"
    __table_args__ = (sa.Index("ix_resumes_user_updated", "user_id", "updated_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(sa.ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(sa.String(120))
    target_role: Mapped[str | None] = mapped_column(sa.String(120))
    template: Mapped[str] = mapped_column(str_enum(RESUME_TEMPLATES, "resume_template"), default="classic",
                                          server_default="classic")
    data: Mapped[dict] = mapped_column(JSONType, default=dict)
