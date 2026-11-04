# ADR 0005: Domain errors and one error response shape

**Status:** Accepted

## Context
Clients need predictable failures. Services that raise HTTP exceptions cannot be reused outside HTTP.

## Decision
- Services and repositories raise subclasses of `DomainError` (`app/errors.py`), each with a stable `code`.
- `app/api/error_handlers.py` maps each `code` to an HTTP status (404, 403, 409, 422).
- Every error body is `{"error": {"code": "...", "message": "..."}}`.
- New failure modes get a new `DomainError` subclass and one entry in the status map.

## Consequences
- No `HTTPException` outside the API layer.
- Clients can switch on `code` rather than parsing messages.
