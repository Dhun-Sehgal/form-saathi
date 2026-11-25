"""Small shared helpers."""
from datetime import date, datetime, timezone

from flask import request
from marshmallow import Schema

from .errors import APIError


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def aware(dt: datetime | None) -> datetime | None:
    """SQLite returns naive datetimes; treat them as UTC."""
    if dt is None:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def iso(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return aware(value).isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return value


def body(schema: Schema, partial: bool = False) -> dict:
    data = request.get_json(silent=True)
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise APIError("Request body must be a JSON object.", 400)
    return schema.load(data, partial=partial)


def int_arg(name: str, default: int, lo: int = 1, hi: int = 100) -> int:
    try:
        value = int(request.args.get(name, default))
    except (TypeError, ValueError):
        value = default
    return max(lo, min(hi, value))


def paginate(query, page: int, per_page: int, db, serializer):
    total = db.session.scalar(query.with_only_columns(db.func.count()).order_by(None))
    rows = db.session.scalars(query.limit(per_page).offset((page - 1) * per_page)).unique().all()
    return {
        "items": [serializer(r) for r in rows],
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": max(1, -(-total // per_page)),
    }


def days_until(d: date | None) -> int | None:
    return None if d is None else (d - date.today()).days
