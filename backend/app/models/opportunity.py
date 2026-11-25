"""Official opportunity records and their structured details.

Only admins write to these tables. Ordinary users can read published rows and
submit CorrectionReports (see admin.py).
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db
from .base import (
    APPLICATION_MODES, BENEFIT_FREQUENCIES, CRITERION_TYPES, DATA_ORIGINS,
    DOCUMENT_SENSITIVITY, EDUCATION_LEVELS, OPPORTUNITY_SCOPES, ORG_TYPES,
    PUBLICATION_STATUSES, VERIFICATION_STATUSES, JSONType, TimestampMixin, str_enum,
)

# Audience tags used by discovery filters (state / education). The admin editor keeps them
# in sync with the matching eligibility criteria; the eligibility engine reads the criteria.
opportunity_states = sa.Table(
    "opportunity_states",
    db.metadata,
    sa.Column("opportunity_id", sa.ForeignKey("opportunities.id", ondelete="CASCADE"), primary_key=True),
    sa.Column("state_code", sa.ForeignKey("states.code", ondelete="CASCADE"), primary_key=True, index=True),
)

opportunity_education_levels = sa.Table(
    "opportunity_education_levels",
    db.metadata,
    sa.Column("opportunity_id", sa.ForeignKey("opportunities.id", ondelete="CASCADE"), primary_key=True),
    sa.Column("education_level", str_enum(EDUCATION_LEVELS, "opp_education_level"), primary_key=True, index=True),
)


class Category(TimestampMixin, db.Model):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(sa.String(60), unique=True)
    name: Mapped[str] = mapped_column(sa.String(80), unique=True)
    description: Mapped[str | None] = mapped_column(sa.String(300))
    icon: Mapped[str] = mapped_column(sa.String(40), default="sparkles")  # Lucide icon name
    color: Mapped[str] = mapped_column(sa.String(20), default="lavender")  # design token name
    sort_order: Mapped[int] = mapped_column(default=0, server_default="0")
    is_active: Mapped[bool] = mapped_column(default=True, server_default=sa.true())


class Organization(TimestampMixin, db.Model):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(200), unique=True)
    org_type: Mapped[str] = mapped_column(str_enum(ORG_TYPES, "org_type"))
    website: Mapped[str | None] = mapped_column(sa.String(500))
    state_code: Mapped[str | None] = mapped_column(sa.ForeignKey("states.code", ondelete="SET NULL"))


class DocumentType(db.Model):
    """Reference list: Aadhaar, income certificate, marksheet, ..."""

    __tablename__ = "document_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(sa.String(60), unique=True)
    name: Mapped[str] = mapped_column(sa.String(100))
    description: Mapped[str | None] = mapped_column(sa.String(300))
    sensitivity: Mapped[str] = mapped_column(str_enum(DOCUMENT_SENSITIVITY, "doc_sensitivity"), default="normal")
    sort_order: Mapped[int] = mapped_column(default=0, server_default="0")


class Opportunity(TimestampMixin, db.Model):
    __tablename__ = "opportunities"
    __table_args__ = (
        sa.CheckConstraint(
            "benefit_amount_min IS NULL OR benefit_amount_max IS NULL OR benefit_amount_max >= benefit_amount_min",
            name="benefit_range",
        ),
        sa.CheckConstraint("opens_on IS NULL OR deadline IS NULL OR deadline >= opens_on", name="date_order"),
        # Truth guarantees enforced by the database itself:
        sa.CheckConstraint(
            "verification_status <> 'verified' OR last_verified_at IS NOT NULL", name="verified_has_date"
        ),
        sa.CheckConstraint(
            "NOT (data_origin = 'demo' AND verification_status = 'verified')", name="demo_never_verified"
        ),
        sa.Index("ix_opportunities_listing", "publication_status", "verification_status", "deadline"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(sa.String(160), unique=True)
    title: Mapped[str] = mapped_column(sa.String(200), index=True)
    summary: Mapped[str] = mapped_column(sa.String(400))
    description: Mapped[str] = mapped_column(sa.Text)

    category_id: Mapped[int] = mapped_column(sa.ForeignKey("categories.id", ondelete="RESTRICT"), index=True)
    organization_id: Mapped[int] = mapped_column(sa.ForeignKey("organizations.id", ondelete="RESTRICT"), index=True)
    scope: Mapped[str] = mapped_column(str_enum(OPPORTUNITY_SCOPES, "opp_scope"), default="national")

    eligibility_summary: Mapped[str] = mapped_column(sa.String(500))
    benefits: Mapped[str] = mapped_column(sa.Text)
    benefit_amount_min: Mapped[Decimal | None] = mapped_column(sa.Numeric(12, 2))
    benefit_amount_max: Mapped[Decimal | None] = mapped_column(sa.Numeric(12, 2))
    benefit_frequency: Mapped[str | None] = mapped_column(str_enum(BENEFIT_FREQUENCIES, "benefit_frequency"))
    income_ceiling: Mapped[Decimal | None] = mapped_column(sa.Numeric(12, 2))  # annual family income, INR

    application_mode: Mapped[str] = mapped_column(str_enum(APPLICATION_MODES, "application_mode"), default="online")
    how_to_apply: Mapped[str | None] = mapped_column(sa.Text)
    official_url: Mapped[str | None] = mapped_column(sa.String(500))  # information page
    apply_url: Mapped[str | None] = mapped_column(sa.String(500))  # application portal
    source_url: Mapped[str] = mapped_column(sa.String(500))  # the document/page we verified against

    opens_on: Mapped[date | None]
    deadline: Mapped[date | None]
    is_rolling: Mapped[bool] = mapped_column(default=False, server_default=sa.false())
    deadline_note: Mapped[str | None] = mapped_column(sa.String(200))

    verification_status: Mapped[str] = mapped_column(
        str_enum(VERIFICATION_STATUSES, "verification_status"),
        default="pending_verification", server_default="pending_verification",
    )
    publication_status: Mapped[str] = mapped_column(
        str_enum(PUBLICATION_STATUSES, "publication_status"), default="draft", server_default="draft"
    )
    data_origin: Mapped[str] = mapped_column(
        str_enum(DATA_ORIGINS, "data_origin"), default="official", server_default="official"
    )
    last_verified_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))
    verified_by_id: Mapped[int | None] = mapped_column(sa.ForeignKey("users.id", ondelete="SET NULL"))

    is_featured: Mapped[bool] = mapped_column(default=False, server_default=sa.false(), index=True)
    featured_rank: Mapped[int | None]
    archived_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))
    created_by_id: Mapped[int | None] = mapped_column(sa.ForeignKey("users.id", ondelete="SET NULL"))
    updated_by_id: Mapped[int | None] = mapped_column(sa.ForeignKey("users.id", ondelete="SET NULL"))

    category: Mapped[Category] = relationship()
    organization: Mapped[Organization] = relationship()
    criteria: Mapped[list[EligibilityCriterion]] = relationship(
        back_populates="opportunity", cascade="all, delete-orphan", order_by="EligibilityCriterion.sort_order"
    )
    required_documents: Mapped[list[RequiredDocument]] = relationship(
        back_populates="opportunity", cascade="all, delete-orphan"
    )
    dates: Mapped[list[OpportunityDate]] = relationship(
        back_populates="opportunity", cascade="all, delete-orphan", order_by="OpportunityDate.event_date"
    )
    states: Mapped[list["State"]] = relationship(secondary=opportunity_states)  # noqa: F821

    @property
    def is_open(self) -> bool:
        """Active = published, not expired/archived, and deadline not passed."""
        if self.publication_status != "published":
            return False
        if self.verification_status in ("expired", "archived"):
            return False
        return self.deadline is None or self.deadline >= date.today()


class EligibilityCriterion(TimestampMixin, db.Model):
    """One machine-checkable rule, transcribed by an admin from the official source.

    `value` shape depends on `criterion_type`, e.g.
      age_max              -> {"years": 30}
      education_level      -> {"any_of": ["undergraduate", "postgraduate"]}
      income_max           -> {"amount": 250000}
      state_domicile       -> {"any_of": ["maharashtra"]}
      marks_min_percentage -> {"value": 60}
      custom               -> {}   (always 'needs review'; shown verbatim to the user)
    """

    __tablename__ = "eligibility_criteria"

    id: Mapped[int] = mapped_column(primary_key=True)
    opportunity_id: Mapped[int] = mapped_column(sa.ForeignKey("opportunities.id", ondelete="CASCADE"), index=True)
    criterion_type: Mapped[str] = mapped_column(str_enum(CRITERION_TYPES, "criterion_type"))
    value: Mapped[dict] = mapped_column(JSONType, default=dict)
    description: Mapped[str] = mapped_column(sa.String(500))  # plain-language rule
    source_excerpt: Mapped[str | None] = mapped_column(sa.Text)  # quoted from the official document
    is_mandatory: Mapped[bool] = mapped_column(default=True, server_default=sa.true())
    sort_order: Mapped[int] = mapped_column(default=0, server_default="0")

    opportunity: Mapped[Opportunity] = relationship(back_populates="criteria")


class RequiredDocument(db.Model):
    __tablename__ = "required_documents"
    __table_args__ = (sa.UniqueConstraint("opportunity_id", "document_type_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    opportunity_id: Mapped[int] = mapped_column(sa.ForeignKey("opportunities.id", ondelete="CASCADE"), index=True)
    document_type_id: Mapped[int] = mapped_column(sa.ForeignKey("document_types.id", ondelete="RESTRICT"))
    is_mandatory: Mapped[bool] = mapped_column(default=True, server_default=sa.true())
    notes: Mapped[str | None] = mapped_column(sa.String(300))  # e.g. "issued after 1 April of current year"

    opportunity: Mapped[Opportunity] = relationship(back_populates="required_documents")
    document_type: Mapped[DocumentType] = relationship()


class OpportunityDate(db.Model):
    """Important dates beyond the deadline: exam date, result date, verification window..."""

    __tablename__ = "opportunity_dates"

    id: Mapped[int] = mapped_column(primary_key=True)
    opportunity_id: Mapped[int] = mapped_column(sa.ForeignKey("opportunities.id", ondelete="CASCADE"), index=True)
    label: Mapped[str] = mapped_column(sa.String(120))
    event_date: Mapped[date]
    note: Mapped[str | None] = mapped_column(sa.String(200))

    opportunity: Mapped[Opportunity] = relationship(back_populates="dates")
