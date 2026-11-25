"""Notification generation.

Runs idempotently (dedupe keys), so it is safe to call on dashboard load AND from the
scheduled worker. Every notification respects the user's preferences.
"""
from __future__ import annotations

import logging
from datetime import date, timedelta

import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models import (
    Application, Notification, NotificationPreference, Opportunity, Reminder, RequiredDocument,
    SavedOpportunity, SourceVerificationLog, UploadedDocument, User,
)
from ..utils.helpers import aware, utcnow
from . import mailer

log = logging.getLogger("formsaathi.notify")
PRE_APPLY = ("interested", "saved", "preparing_documents", "ready_to_apply")


def prefs_for(user: User) -> NotificationPreference:
    prefs = db.session.get(NotificationPreference, user.id)
    if prefs is None:
        prefs = NotificationPreference(user_id=user.id)
        db.session.add(prefs)
        db.session.flush()
    return prefs


def push(user: User, type_: str, title: str, body: str | None = None, link: str | None = None,
         dedupe_key: str | None = None, email: bool = False) -> Notification | None:
    """Create a notification unless one with the same dedupe_key exists."""
    if dedupe_key and db.session.scalar(
        sa.select(Notification.id).where(Notification.user_id == user.id, Notification.dedupe_key == dedupe_key)
    ):
        return None
    n = Notification(user_id=user.id, type=type_, title=title, body=body, link=link, dedupe_key=dedupe_key)
    try:
        with db.session.begin_nested():
            db.session.add(n)
    except IntegrityError:
        return None
    if email and prefs_for(user).email_enabled and mailer.is_configured():
        if mailer.send(user.email, title, body or title):
            n.emailed_at = utcnow()
    return n


def missing_documents(user_id: int, opportunity_id: int) -> list[str]:
    required = db.session.execute(
        sa.select(RequiredDocument.document_type_id).where(
            RequiredDocument.opportunity_id == opportunity_id, RequiredDocument.is_mandatory.is_(True))
    ).scalars().all()
    have = set(db.session.scalars(sa.select(UploadedDocument.document_type_id).where(
        UploadedDocument.user_id == user_id, UploadedDocument.deleted_at.is_(None),
        sa.or_(UploadedDocument.expires_on.is_(None), UploadedDocument.expires_on >= date.today()),
    )))
    return [t for t in required if t not in have]


def sync_user(user: User) -> int:
    """Generate any due notifications for one user. Returns how many were created."""
    prefs = prefs_for(user)
    today = date.today()
    created = 0

    # 1) Deadlines for saved + tracked opportunities.
    if prefs.deadline_reminders:
        ids = set(db.session.scalars(sa.select(SavedOpportunity.opportunity_id).where(SavedOpportunity.user_id == user.id)))
        ids |= set(db.session.scalars(sa.select(Application.opportunity_id).where(
            Application.user_id == user.id, Application.status.in_(PRE_APPLY))))
        if ids:
            soon = db.session.scalars(sa.select(Opportunity).where(
                Opportunity.id.in_(ids), Opportunity.deadline.is_not(None),
                Opportunity.deadline >= today, Opportunity.deadline <= today + timedelta(days=prefs.deadline_days_before),
                Opportunity.verification_status.notin_(("expired", "archived")),
            )).all()
            for o in soon:
                days = (o.deadline - today).days
                bucket = "1d" if days <= 1 else "3d" if days <= 3 else "window"
                when = "today" if days == 0 else "tomorrow" if days == 1 else f"in {days} days"
                if push(user, "deadline", f"{o.title} closes {when}",
                        f"Deadline: {o.deadline.strftime('%d %b %Y')}. Finish your documents and apply on the official site.",
                        f"/app/opportunities/{o.slug}", f"deadline:{o.id}:{bucket}", email=True):
                    created += 1

    # 2) Missing mandatory documents for tracked applications.
    if prefs.document_reminders:
        week = today.isocalendar()
        apps = db.session.scalars(sa.select(Application).where(
            Application.user_id == user.id, Application.status.in_(PRE_APPLY))).all()
        for a in apps:
            missing = missing_documents(user.id, a.opportunity_id)
            if missing and push(user, "document_missing", f"{len(missing)} document(s) missing for {a.opportunity.title}",
                                "Upload them to your document vault so you're ready to apply.",
                                f"/app/tracker/{a.id}", f"docs:{a.id}:{week[0]}-{week[1]}"):
                created += 1

    # 3) Nudge to update status for applications sitting in "applied" for 30+ days.
    if prefs.status_reminders:
        cutoff = utcnow() - timedelta(days=30)
        stale = db.session.scalars(sa.select(Application).where(
            Application.user_id == user.id, Application.status.in_(("applied", "under_review")))).all()
        for a in stale:
            if aware(a.updated_at) < cutoff and push(
                user, "status_reminder", f"Any update on {a.opportunity.title}?",
                "If you heard back, update the status in your tracker.", f"/app/tracker/{a.id}",
                f"status:{a.id}:{today.year}-{today.month}"):
                created += 1

    # 4) Uploaded certificates expiring within 30 days.
    if prefs.document_reminders:
        expiring = db.session.scalars(sa.select(UploadedDocument).where(
            UploadedDocument.user_id == user.id, UploadedDocument.deleted_at.is_(None),
            UploadedDocument.expires_on.is_not(None), UploadedDocument.expires_on <= today + timedelta(days=30),
        )).all()
        for d in expiring:
            if push(user, "document_missing", f"{d.document_type.name} expires on {d.expires_on.strftime('%d %b %Y')}",
                    "Many applications need a currently valid certificate. Consider renewing it.",
                    "/app/documents", f"docexp:{d.id}:{d.expires_on.isoformat()}"):
                created += 1

    # 5) Personal reminders that are due.
    due = db.session.scalars(sa.select(Reminder).where(
        Reminder.user_id == user.id, Reminder.sent_at.is_(None), Reminder.is_done.is_(False),
        Reminder.remind_at <= utcnow())).all()
    for r in due:
        link = f"/app/tracker/{r.application_id}" if r.application_id else "/app/calendar"
        if push(user, "reminder", r.title, "Your personal reminder.", link, f"reminder:{r.id}",
                email=r.channel in ("email", "both")):
            created += 1
        r.sent_at = utcnow()

    db.session.commit()
    return created


def expire_past_deadlines() -> int:
    """Mark opportunities whose deadline has passed as expired, with an audit log row."""
    rows = db.session.scalars(sa.select(Opportunity).where(
        Opportunity.deadline < date.today(), Opportunity.is_rolling.is_(False),
        Opportunity.verification_status.in_(("verified", "pending_verification")),
    )).all()
    for o in rows:
        db.session.add(SourceVerificationLog(opportunity_id=o.id, action="marked_expired",
                                             from_status=o.verification_status, to_status="expired",
                                             notes="Automatic: deadline passed."))
        o.verification_status = "expired"
    db.session.commit()
    return len(rows)


def run_all() -> dict:
    expired = expire_past_deadlines()
    total = 0
    for user in db.session.scalars(sa.select(User).where(User.is_active.is_(True))).all():
        try:
            total += sync_user(user)
        except Exception:  # one user's failure must not stop the job
            db.session.rollback()
            log.exception("Notification sync failed for user %s", user.id)
    return {"expired": expired, "notifications": total}
