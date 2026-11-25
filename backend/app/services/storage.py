"""Private file storage for the document vault.

Files are written under UPLOAD_DIR/<user_id>/<random>.ext — never inside a public folder —
and are only served through an authenticated, ownership-checked endpoint.
"""
import hashlib
import os
import uuid
from pathlib import Path

from flask import current_app
from werkzeug.datastructures import FileStorage

from ..utils.errors import APIError

# Detect the real type from the file's first bytes; never trust the extension or browser MIME.
SIGNATURES = [
    (b"%PDF-", "application/pdf", ".pdf"),
    (b"\x89PNG\r\n\x1a\n", "image/png", ".png"),
    (b"\xff\xd8\xff", "image/jpeg", ".jpg"),
]
ALLOWED_EXT = {".pdf", ".png", ".jpg", ".jpeg", ".webp"}


def sniff(head: bytes) -> tuple[str, str] | None:
    for sig, mime, ext in SIGNATURES:
        if head.startswith(sig):
            return mime, ext
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return "image/webp", ".webp"
    return None


def _root() -> Path:
    root = Path(current_app.config["UPLOAD_DIR"]).resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


def save(user_id: int, file: FileStorage) -> dict:
    if not file or not file.filename:
        raise APIError("Choose a file to upload.", 422, "validation_error", {"file": "Required."})
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXT:
        raise APIError("Only PDF, JPG, PNG or WebP files are allowed.", 422, "unsupported_file")

    data = file.read()
    max_bytes = current_app.config["MAX_UPLOAD_MB"] * 1024 * 1024
    if not data:
        raise APIError("The file is empty.", 422, "unsupported_file")
    if len(data) > max_bytes:
        raise APIError(f"File is too large. Maximum size is {current_app.config['MAX_UPLOAD_MB']} MB.", 413, "file_too_large")
    detected = sniff(data[:16])
    if detected is None:
        raise APIError("This file doesn't look like a valid PDF or image.", 422, "unsupported_file")
    mime, real_ext = detected

    folder = _root() / str(user_id)
    folder.mkdir(exist_ok=True)
    stored = uuid.uuid4().hex + real_ext
    (folder / stored).write_bytes(data)
    return {
        "stored_filename": stored,
        "mime_type": mime,
        "size_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "original_filename": os.path.basename(file.filename)[:255],
    }


def path_for(user_id: int, stored_filename: str) -> Path:
    path = (_root() / str(user_id) / stored_filename).resolve()
    if _root() not in path.parents:  # defence in depth against path tricks
        raise APIError("Invalid file path.", 400)
    return path


def delete(user_id: int, stored_filename: str) -> None:
    try:
        path_for(user_id, stored_filename).unlink(missing_ok=True)
    except APIError:
        pass


def delete_all(user_id: int) -> None:
    folder = _root() / str(user_id)
    if folder.exists():
        for f in folder.iterdir():
            f.unlink(missing_ok=True)
        folder.rmdir()
