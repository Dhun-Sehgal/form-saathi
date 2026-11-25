"""Private document vault + per-opportunity checklists."""
import io
from datetime import date

import sqlalchemy as sa
from flask import Blueprint, jsonify, request, send_file
from marshmallow import Schema, ValidationError, fields, validate

from ..extensions import db, limiter
from ..models import DocumentType, Opportunity, RequiredDocument, UploadedDocument
from ..serializers import document_dict, document_type_dict
from ..services import catalog, storage
from ..utils.auth import current_user, login_required
from ..utils.errors import APIError, not_found
from ..utils.helpers import body, utcnow

bp = Blueprint("documents", __name__, url_prefix="/api/v1/documents")
MAX_DOCUMENTS = 60


class UpdateSchema(Schema):
    label = fields.String(allow_none=True, validate=validate.Length(max=120))
    document_type_id = fields.Integer()
    issued_on = fields.Date(allow_none=True)
    expires_on = fields.Date(allow_none=True)


def _own(doc_id) -> UploadedDocument:
    d = db.session.get(UploadedDocument, doc_id)
    if d is None or d.user_id != current_user().id or d.deleted_at is not None:
        raise not_found("Document")
    return d


def _active_docs(user_id):
    return db.session.scalars(sa.select(UploadedDocument).where(
        UploadedDocument.user_id == user_id, UploadedDocument.deleted_at.is_(None)
    ).order_by(UploadedDocument.created_at.desc())).all()


@bp.get("")
@login_required
def list_documents():
    return jsonify(items=[document_dict(d) for d in _active_docs(current_user().id)])


@bp.post("")
@login_required
@limiter.limit("30 per hour")
def upload():
    user = current_user()
    if len(_active_docs(user.id)) >= MAX_DOCUMENTS:
        raise APIError(f"You can store up to {MAX_DOCUMENTS} documents. Delete old ones first.", 409, "limit_reached")
    try:
        doc_type_id = int(request.form.get("document_type_id", ""))
    except ValueError:
        raise APIError("Choose a document type.", 422, "validation_error", {"document_type_id": "Required."})
    if db.session.get(DocumentType, doc_type_id) is None:
        raise APIError("Unknown document type.", 422, "validation_error", {"document_type_id": "Invalid."})
    try:
        extra = UpdateSchema().load({k: v for k, v in request.form.items()
                                     if k in ("label", "issued_on", "expires_on") and v})
    except ValidationError as e:
        raise APIError("Please check the dates.", 422, "validation_error",
                       {k: v[0] for k, v in e.messages.items()})
    info = storage.save(user.id, request.files.get("file"))
    d = UploadedDocument(user_id=user.id, document_type_id=doc_type_id, **info, **extra)
    db.session.add(d)
    db.session.commit()
    return jsonify(document=document_dict(d)), 201


@bp.get("/<int:doc_id>/file")
@login_required
def download(doc_id):
    d = _own(doc_id)
    path = storage.path_for(d.user_id, d.stored_filename)
    if not path.exists():
        raise APIError("The file is missing from storage. Please upload it again.", 410, "file_missing")
    inline = request.args.get("download") != "1"
    # Files are small (<= MAX_UPLOAD_MB); reading into memory releases the file handle immediately.
    resp = send_file(io.BytesIO(path.read_bytes()), mimetype=d.mime_type, as_attachment=not inline, download_name=d.original_filename,
                     max_age=0)
    resp.headers["Cache-Control"] = "private, no-store"
    resp.headers["Content-Security-Policy"] = "default-src 'none'; img-src 'self'; style-src 'unsafe-inline'; sandbox"
    return resp


@bp.patch("/<int:doc_id>")
@login_required
def update(doc_id):
    d = _own(doc_id)
    data = body(UpdateSchema(), partial=True)
    if "document_type_id" in data and db.session.get(DocumentType, data["document_type_id"]) is None:
        raise APIError("Unknown document type.", 422, "validation_error")
    for k, v in data.items():
        setattr(d, k, v)
    db.session.commit()
    return jsonify(document=document_dict(d))


@bp.delete("/<int:doc_id>")
@login_required
def delete(doc_id):
    d = _own(doc_id)
    storage.delete(d.user_id, d.stored_filename)  # the file is removed immediately
    d.deleted_at = utcnow()
    d.original_filename = "deleted"
    db.session.commit()
    return jsonify(ok=True)


def build_checklist(user_id: int, opportunity: Opportunity) -> dict:
    docs = _active_docs(user_id)
    by_type: dict[int, UploadedDocument] = {}
    for d in docs:
        by_type.setdefault(d.document_type_id, d)
    items = []
    for r in opportunity.required_documents:
        have = by_type.get(r.document_type_id)
        if have is None:
            status = "missing"
        elif have.expires_on and have.expires_on < date.today():
            status = "expired"
        elif have.expires_on and opportunity.deadline and have.expires_on < opportunity.deadline:
            status = "expiring"
        else:
            status = "ready"
        items.append({"document_type": document_type_dict(r.document_type), "is_mandatory": r.is_mandatory,
                      "notes": r.notes, "status": status, "document": document_dict(have) if have else None})
    ready = sum(1 for i in items if i["status"] == "ready")
    return {"items": items, "ready": ready, "total": len(items),
            "missing_mandatory": sum(1 for i in items if i["is_mandatory"] and i["status"] in ("missing", "expired"))}


@bp.get("/checklist/<int:opportunity_id>")
@login_required
def checklist(opportunity_id):
    o = db.session.scalars(catalog.public_query().where(Opportunity.id == opportunity_id)).first()
    if o is None:
        raise not_found("Opportunity")
    data = build_checklist(current_user().id, o)
    data["opportunity"] = {"id": o.id, "slug": o.slug, "title": o.title, "deadline": o.deadline.isoformat() if o.deadline else None}
    return jsonify(data)
