"""Maps domain errors to HTTP. Every error body has the same shape (ADR 0005):

    {"error": {"code": "...", "message": "..."}}

Validation errors list field names and messages only. They must never echo the
submitted input, because that input can contain a passport number (ADR 0004).
"""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.errors import DomainError

STATUS_BY_CODE = {
    "not_found": 404,
    "invalid_input": 422,
    "forbidden": 403,
    "duplicate_claim": 409,
    "invalid_state": 409,
}


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def handle_domain_error(request: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=STATUS_BY_CODE.get(exc.code, 400),
            content={"error": {"code": exc.code, "message": exc.message}},
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        fields = [
            {"field": ".".join(str(part) for part in err["loc"]), "message": err["msg"]}
            for err in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content={"error": {"code": "invalid_input", "message": "Request validation failed", "fields": fields}},
        )
