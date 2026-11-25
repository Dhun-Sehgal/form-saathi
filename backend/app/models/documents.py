"""Private document vault. Files live outside any public folder under a random name."""
from __future__ import annotations

from datetime import date, datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db
from .base import UPLOAD_STATUSES, TimestampMixin, str_enum


class UploadedDocument(TimestampMixin, db.Model):
    __tablename__ = "uploaded_documents"
    __table_args__ = (
        sa.CheckConstraint("size_bytes > 0", name="size_positive"),
        sa.Index("ix_uploaded_documents_user_type", "user_id", "document_type_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(sa.ForeignKey("users.id", ondelete="CASCADE"))
    document_type_id: Mapped[int] = mapped_column(sa.ForeignKey("document_types.id", ondelete="RESTRICT"))
    label: Mapped[str | None] = mapped_column(sa.String(120))  # e.g. "Semester 5 marksheet"
    original_filename: Mapped[str] = mapped_column(sa.String(255))
    stored_filename: Mapped[str] = mapped_column(sa.String(64), unique=True)  # uuid4 hex + ext
    mime_type: Mapped[str] = mapped_column(sa.String(100))
    size_bytes: Mapped[int]
    sha256: Mapped[str] = mapped_column(sa.String(64))
    status: Mapped[str] = mapped_column(str_enum(UPLOAD_STATUSES, "upload_status"), default="uploaded")
    issued_on: Mapped[date | None]
    expires_on: Mapped[date | None]  # e.g. income certificates are valid for a limited period
    deleted_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))

    document_type: Mapped["DocumentType"] = relationship()  # noqa: F821
