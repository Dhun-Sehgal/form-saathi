"""Application tracker, notes, reminders, calendar, notifications, dashboard."""
from datetime import date, datetime, time, timedelta, timezone

import sqlalchemy as sa
from flask import Blueprint, jsonify, request
from marshmallow import Schema, fields, validate

from ..extensions import db
from ..models import (
    Announcement, Application, ApplicationNote, ApplicationStatusHistory, ChatMessage, ChatSession,
    Notification, Opportunity, OpportunityDate, Reminder, RequiredDocument, SavedOpportunity, UploadedDocument,
)
from ..models.base import APPLICATION_STATUSES, REMINDER_CHANNELS
from ..serializers import (
    application_dict, document_type_dict, notification_dict, opportunity_card, profile_completion, reminder_dict,
)
from ..services import catalog, mailer, notify
from ..utils.auth import current_user, login_required
from ..utils.errors import APIError, not_found
from ..utils.helpers import aware, body, int_arg, iso, utcnow
from .documents import build_checklist

bp = Blueprint("tracker", __name__, url_prefix="/api/v1")


class CreateAppSchema(Schema):
    opportunity_id = fields.Integer(required=True)
    status = fields.String(load_default="interested", validate=validate.OneOf(APPLICATION_STATUSES))


class UpdateAppSchema(Schema):
    status = fields.String(validate=validate.OneOf(APPLICATION_STATUSES))
    applied_on = fields.Date(allow_none=True)
    reference_number = fields.String(allow_none=True, validate=validate.Length(max=80))
    note = fields.String(allow_none=True, validate=validate.Length(max=300))


class NoteSchema(Schema):
    body = fields.String(required=True, validate=validate.Length(min=1, max=4000))


class ReminderSchema(Schema):
    title = fields.String(required=True, validate=validate.Length(min=1, max=160))
    remind_at = fields.AwareDateTime(required=True, default_timezone=timezone.utc)
    channel = fields.String(load_default="in_app", validate=validate.OneOf(REMINDER_CHANNELS))
    application_id = fields.Integer(load_default=None, allow_none=True)
    opportunity_id = fields.Integer(load_default=None, allow_none=True)
    is_done = fields.Boolean()


class PrefsSchema(Schema):
    email_enabled = fields.Boolean()
    deadline_reminders = fields.Boolean()
    deadline_days_before = fields.Integer(validate=validate.Range(1, 60))
    document_reminders = fields.Boolean()
    status_reminders = fields.Boolean()
    opportunity_updates = fields.Boolean()
    weekly_digest = fields.Boolean()


def _own_app(app_id) -> Application:
    a = db.session.get(Application, app_id)
    if a is None or a.user_id != current_user().id:
        raise not_found("Application")
    return a


# ------------------------------------------------------------------ applications
@bp.get("/applications")
@login_required
def list_applications():
    rows = db.session.scalars(sa.select(Application).where(Application.user_id == current_user().id)
                              .order_by(Application.updated_at.desc())).all()
    items = []
    for a in rows:
        d = application_dict(a)
        d["checklist"] = {k: v for k, v in build_checklist(a.user_id, a.opportunity).items() if k != "items"}
        items.append(d)
    return jsonify(items=items)


@bp.post("/applications")
@login_required
def create_application():
    data = body(CreateAppSchema())
    user = current_user()
    o = db.session.scalars(catalog.public_query().where(Opportunity.id == data["opportunity_id"])).first()
    if o is None:
        raise not_found("Opportunity")
    a = db.session.scalar(sa.select(Application).where(Application.user_id == user.id, Application.opportunity_id == o.id))
    if a is not None:
        return jsonify(application=application_dict(a, full=True), created=False)
    a = Application(user_id=user.id, opportunity_id=o.id, status=data["status"])
    a.history.append(ApplicationStatusHistory(to_status=data["status"], note="Added to tracker"))
    db.session.add(a)
    db.session.commit()
    return jsonify(application=application_dict(a, full=True), created=True), 201


@bp.get("/applications/<int:app_id>")
@login_required
def get_application(app_id):
    a = _own_app(app_id)
    d = application_dict(a, full=True)
    d["checklist"] = build_checklist(a.user_id, a.opportunity)
    d["reminders"] = [reminder_dict(r) for r in db.session.scalars(
        sa.select(Reminder).where(Reminder.application_id == a.id).order_by(Reminder.remind_at))]
    return jsonify(application=d)


@bp.patch("/applications/<int:app_id>")
@login_required
def update_application(app_id):
    a = _own_app(app_id)
    data = body(UpdateAppSchema(), partial=True)
    note = data.pop("note", None)
    if "status" in data and data["status"] != a.status:
        a.history.append(ApplicationStatusHistory(from_status=a.status, to_status=data["status"], source="user", note=note))
        a.status, a.status_source = data["status"], "user"
    for k in ("applied_on", "reference_number"):
        if k in data:
            setattr(a, k, data[k])
    if a.applied_on and a.applied_on > date.today():
        raise APIError("Application date can't be in the future.", 422, "validation_error", {"applied_on": "Future date."})
    a.updated_at = utcnow()
    db.session.commit()
    return jsonify(application=application_dict(a, full=True))


@bp.delete("/applications/<int:app_id>")
@login_required
def delete_application(app_id):
    db.session.delete(_own_app(app_id))
    db.session.commit()
    return jsonify(ok=True)


@bp.post("/applications/<int:app_id>/notes")
@login_required
def add_note(app_id):
    a = _own_app(app_id)
    n = ApplicationNote(application_id=a.id, body=body(NoteSchema())["body"].strip())
    db.session.add(n)
    db.session.commit()
    return jsonify(note={"id": n.id, "body": n.body, "created_at": iso(n.created_at)}), 201


@bp.delete("/applications/<int:app_id>/notes/<int:note_id>")
@login_required
def delete_note(app_id, note_id):
    a = _own_app(app_id)
    n = db.session.get(ApplicationNote, note_id)
    if n is None or n.application_id != a.id:
        raise not_found("Note")
    db.session.delete(n)
    db.session.commit()
    return jsonify(ok=True)


# ------------------------------------------------------------------ reminders
def _validate_links(data):
    user = current_user()
    if data.get("application_id"):
        _own_app(data["application_id"])
    if data.get("opportunity_id") and db.session.get(Opportunity, data["opportunity_id"]) is None:
        raise not_found("Opportunity")
    return user


@bp.get("/reminders")
@login_required
def list_reminders():
    rows = db.session.scalars(sa.select(Reminder).where(Reminder.user_id == current_user().id)
                              .order_by(Reminder.is_done, Reminder.remind_at)).all()
    return jsonify(items=[reminder_dict(r) for r in rows])


@bp.post("/reminders")
@login_required
def create_reminder():
    data = body(ReminderSchema())
    user = _validate_links(data)
    data.pop("is_done", None)
    r = Reminder(user_id=user.id, **data)
    db.session.add(r)
    db.session.commit()
    return jsonify(reminder=reminder_dict(r), email_configured=mailer.is_configured()), 201


@bp.patch("/reminders/<int:rid>")
@login_required
def update_reminder(rid):
    r = db.session.get(Reminder, rid)
    if r is None or r.user_id != current_user().id:
        raise not_found("Reminder")
    data = body(ReminderSchema(), partial=True)
    _validate_links(data)
    for k, v in data.items():
        setattr(r, k, v)
    if "remind_at" in data:
        r.sent_at = None
    db.session.commit()
    return jsonify(reminder=reminder_dict(r))


@bp.delete("/reminders/<int:rid>")
@login_required
def delete_reminder(rid):
    r = db.session.get(Reminder, rid)
    if r is None or r.user_id != current_user().id:
        raise not_found("Reminder")
    db.session.delete(r)
    db.session.commit()
    return jsonify(ok=True)


# ------------------------------------------------------------------ calendar
@bp.get("/calendar")
@login_required
def calendar():
    user = current_user()
    try:
        start = date.fromisoformat(request.args.get("start", ""))
        end = date.fromisoformat(request.args.get("end", ""))
    except ValueError:
        start = date.today().replace(day=1)
        end = start + timedelta(days=42)
    if (end - start).days > 100:
        raise APIError("Date range too large.", 400)
    saved_ids = set(db.session.scalars(sa.select(SavedOpportunity.opportunity_id).where(SavedOpportunity.user_id == user.id)))
    apps = {a.opportunity_id: a for a in db.session.scalars(sa.select(Application).where(Application.user_id == user.id))}
    ids = saved_ids | set(apps)
    events = []
    if ids:
        for o in db.session.scalars(sa.select(Opportunity).where(
                Opportunity.id.in_(ids), Opportunity.deadline.between(start, end))):
            events.append({"type": "deadline", "date": iso(o.deadline), "title": f"Deadline: {o.title}",
                           "link": f"/app/opportunities/{o.slug}", "tracked": o.id in apps})
        for d in db.session.scalars(sa.select(OpportunityDate).where(
                OpportunityDate.opportunity_id.in_(ids), OpportunityDate.event_date.between(start, end))):
            events.append({"type": "date", "date": iso(d.event_date), "title": f"{d.label}: {d.opportunity.title}",
                           "link": f"/app/opportunities/{d.opportunity.slug}"})
    for a in apps.values():
        if a.applied_on and start <= a.applied_on <= end:
            events.append({"type": "applied", "date": iso(a.applied_on), "title": f"Applied: {a.opportunity.title}",
                           "link": f"/app/tracker/{a.id}"})
    lo = datetime.combine(start, time.min, tzinfo=timezone.utc)
    hi = datetime.combine(end, time.max, tzinfo=timezone.utc)
    for r in db.session.scalars(sa.select(Reminder).where(Reminder.user_id == user.id, Reminder.remind_at.between(lo, hi))):
        events.append({"type": "reminder", "date": aware(r.remind_at).date().isoformat(), "title": r.title,
                       "link": f"/app/tracker/{r.application_id}" if r.application_id else None, "id": r.id,
                       "is_done": r.is_done, "remind_at": iso(r.remind_at)})
    events.sort(key=lambda e: e["date"])
    return jsonify(start=iso(start), end=iso(end), events=events)


# ------------------------------------------------------------------ notifications
@bp.get("/notifications")
@login_required
def list_notifications():
    user = current_user()
    notify.sync_user(user)
    q = sa.select(Notification).where(Notification.user_id == user.id)
    if request.args.get("unread") == "1":
        q = q.where(Notification.is_read.is_(False))
    rows = db.session.scalars(q.order_by(Notification.created_at.desc(), Notification.id.desc())
                              .limit(int_arg("limit", 50, 1, 100))).all()
    unread = db.session.scalar(sa.select(sa.func.count(Notification.id)).where(
        Notification.user_id == user.id, Notification.is_read.is_(False)))
    return jsonify(items=[notification_dict(n) for n in rows], unread=unread)


@bp.post("/notifications/<int:nid>/read")
@login_required
def read_notification(nid):
    n = db.session.get(Notification, nid)
    if n is None or n.user_id != current_user().id:
        raise not_found("Notification")
    n.is_read, n.read_at = True, utcnow()
    db.session.commit()
    return jsonify(ok=True)


@bp.post("/notifications/read-all")
@login_required
def read_all():
    db.session.execute(sa.update(Notification).where(
        Notification.user_id == current_user().id, Notification.is_read.is_(False)).values(is_read=True, read_at=utcnow()))
    db.session.commit()
    return jsonify(ok=True)


@bp.get("/notifications/preferences")
@login_required
def get_prefs():
    p = notify.prefs_for(current_user())
    db.session.commit()
    return jsonify(preferences={k: getattr(p, k) for k in PrefsSchema().fields}, email_configured=mailer.is_configured())


@bp.put("/notifications/preferences")
@login_required
def put_prefs():
    p = notify.prefs_for(current_user())
    for k, v in body(PrefsSchema(), partial=True).items():
        setattr(p, k, v)
    db.session.commit()
    return jsonify(preferences={k: getattr(p, k) for k in PrefsSchema().fields}, email_configured=mailer.is_configured())


# ------------------------------------------------------------------ dashboard
@bp.get("/dashboard")
@login_required
def dashboard():
    user = current_user()
    notify.sync_user(user)
    saved, app_map = catalog.user_context(user)
    today = date.today()

    apps = db.session.scalars(sa.select(Application).where(Application.user_id == user.id)).all()
    by_status = {s: 0 for s in APPLICATION_STATUSES}
    for a in apps:
        by_status[a.status] += 1

    watch_ids = saved | set(app_map)
    upcoming = []
    if watch_ids:
        upcoming = db.session.scalars(catalog.public_query().where(
            Opportunity.id.in_(watch_ids), Opportunity.deadline >= today,
            Opportunity.verification_status.notin_(("expired", "archived"))
        ).order_by(Opportunity.deadline).limit(5)).unique().all()

    pending_docs = []
    for a in apps:
        if a.status in notify.PRE_APPLY:
            for item in build_checklist(user.id, a.opportunity)["items"]:
                if item["is_mandatory"] and item["status"] in ("missing", "expired"):
                    pending_docs.append({"application_id": a.id, "opportunity_title": a.opportunity.title,
                                         "document_type": item["document_type"], "status": item["status"]})

    saved_rows = db.session.scalars(sa.select(SavedOpportunity).where(SavedOpportunity.user_id == user.id)
                                    .order_by(SavedOpportunity.created_at.desc()).limit(4)).all()
    recent = db.session.scalars(catalog.public_query().where(catalog.open_clause())
                                .order_by(Opportunity.created_at.desc(), Opportunity.id.desc()).limit(4)).unique().all()
    recommended = []
    for o, verdict, reasons in catalog.recommend(user, 4):
        card = opportunity_card(o, saved, app_map)
        card["match"] = {"verdict": verdict, "reasons": reasons}
        recommended.append(card)

    # Weekly activity: actions per day over the last 7 days.
    since = datetime.combine(today - timedelta(days=6), time.min, tzinfo=timezone.utc)
    stamps = []
    stamps += db.session.scalars(sa.select(SavedOpportunity.created_at).where(
        SavedOpportunity.user_id == user.id, SavedOpportunity.created_at >= since)).all()
    stamps += db.session.scalars(sa.select(ApplicationStatusHistory.created_at).join(Application).where(
        Application.user_id == user.id, ApplicationStatusHistory.created_at >= since)).all()
    stamps += db.session.scalars(sa.select(UploadedDocument.created_at).where(
        UploadedDocument.user_id == user.id, UploadedDocument.created_at >= since)).all()
    stamps += db.session.scalars(sa.select(ChatMessage.created_at).join(ChatSession).where(
        ChatSession.user_id == user.id, ChatMessage.role == "user", ChatMessage.created_at >= since)).all()
    days = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
    counts = {d: 0 for d in days}
    for s in stamps:
        d = aware(s).date()
        if d in counts:
            counts[d] += 1

    notifications = db.session.scalars(sa.select(Notification).where(
        Notification.user_id == user.id, Notification.is_read.is_(False))
        .order_by(Notification.created_at.desc()).limit(5)).all()
    docs_uploaded = db.session.scalar(sa.select(sa.func.count(UploadedDocument.id)).where(
        UploadedDocument.user_id == user.id, UploadedDocument.deleted_at.is_(None)))
    announcements = db.session.scalars(sa.select(Announcement).where(
        Announcement.is_active.is_(True), Announcement.audience.in_(("all", "users")),
        sa.or_(Announcement.ends_at.is_(None), Announcement.ends_at >= utcnow()),
    ).order_by(Announcement.created_at.desc()).limit(2)).all()

    return jsonify(
        name=(user.profile.full_name or "").split(" ")[0] if user.profile else "",
        profile_completion=profile_completion(user.profile),
        stats={
            "saved": len(saved), "tracked": len(apps),
            "applied": sum(by_status[s] for s in ("applied", "under_review", "approved", "rejected")),
            "deadlines_this_week": sum(1 for o in upcoming if (o.deadline - today).days <= 7),
            "documents": docs_uploaded, "documents_missing": len(pending_docs),
        },
        recommended=recommended,
        recent=[opportunity_card(o, saved, app_map) for o in recent],
        saved=[opportunity_card(s.opportunity, saved, app_map) for s in saved_rows],
        upcoming_deadlines=[opportunity_card(o, saved, app_map) for o in upcoming],
        applications_by_status=by_status,
        pending_documents=pending_docs[:8],
        notifications=[notification_dict(n) for n in notifications],
        weekly_activity=[{"date": d.isoformat(), "count": counts[d]} for d in days],
        announcements=[{"id": a.id, "title": a.title, "body": a.body, "level": a.level} for a in announcements],
    )
