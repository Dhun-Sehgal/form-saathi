"""One JSON error shape for the whole API:
    {"error": {"code": "...", "message": "...", "fields": {...}}}
"""
import logging

from flask import Flask, jsonify, request
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException

log = logging.getLogger("formsaathi.errors")


class APIError(Exception):
    def __init__(self, message: str, status: int = 400, code: str = "bad_request", fields: dict | None = None):
        super().__init__(message)
        self.message, self.status, self.code, self.fields = message, status, code, fields


def not_found(what: str = "Resource") -> APIError:
    return APIError(f"{what} not found.", 404, "not_found")


def _payload(code: str, message: str, fields: dict | None = None):
    body = {"code": code, "message": message}
    if fields:
        body["fields"] = fields
    return {"error": body}


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(APIError)
    def _api_error(e: APIError):
        return jsonify(_payload(e.code, e.message, e.fields)), e.status

    @app.errorhandler(ValidationError)
    def _validation(e: ValidationError):
        fields = {k: (v[0] if isinstance(v, list) else v) for k, v in e.messages.items()} if isinstance(e.messages, dict) else None
        return jsonify(_payload("validation_error", "Please check the highlighted fields.", fields)), 422

    @app.errorhandler(HTTPException)
    def _http(e: HTTPException):
        if not request.path.startswith("/api/"):
            return e
        codes = {404: "not_found", 405: "method_not_allowed", 413: "file_too_large", 429: "rate_limited"}
        messages = {
            413: f"File is too large. Maximum size is {app.config['MAX_UPLOAD_MB']} MB.",
            429: "Too many requests. Please wait a moment and try again.",
        }
        return jsonify(_payload(codes.get(e.code, "http_error"), messages.get(e.code, e.description))), e.code

    @app.errorhandler(Exception)
    def _unhandled(e: Exception):
        log.exception("Unhandled error on %s %s", request.method, request.path)
        return jsonify(_payload("server_error", "Something went wrong on our side. Please try again.")), 500
