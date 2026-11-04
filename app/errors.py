"""Domain errors.

Services and repositories raise these. They know nothing about HTTP; the API
layer maps each `code` to a status in `app/api/error_handlers.py`.
"""
from __future__ import annotations


class DomainError(Exception):
    code = "domain_error"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(DomainError):
    code = "not_found"


class InvalidInputError(DomainError):
    code = "invalid_input"


class PermissionDeniedError(DomainError):
    code = "forbidden"


class DuplicateClaimError(DomainError):
    code = "duplicate_claim"


class InvalidStateError(DomainError):
    code = "invalid_state"
