from __future__ import annotations

import logging
import re
import sqlite3

from app.clock import Clock
from app.db import transaction
from app.domain import Claim, ClaimStatus, Role
from app.errors import (
    DuplicateClaimError,
    InvalidInputError,
    InvalidStateError,
    NotFoundError,
    PermissionDeniedError,
)
from app.repositories.claims import ClaimRepository
from app.repositories.incidents import IncidentRepository
from app.repositories.staff import StaffRepository

logger = logging.getLogger(__name__)

MAX_AMOUNT_CENTS = 5_000_000  # $50,000.00
MAX_PAGE_SIZE = 200
_PASSPORT = re.compile(r"^[A-Z0-9]{5,20}$")


class ClaimService:
    def __init__(
        self,
        conn: sqlite3.Connection,
        claims: ClaimRepository,
        incidents: IncidentRepository,
        staff: StaffRepository,
        clock: Clock,
    ) -> None:
        self._conn = conn
        self._claims = claims
        self._incidents = incidents
        self._staff = staff
        self._clock = clock

    def file_claim(
        self,
        *,
        incident_id: int,
        passenger_name: str,
        passport_number: str,
        amount_cents: int,
        reason: str,
        filed_by: int,
    ) -> Claim:
        if isinstance(amount_cents, bool) or not isinstance(amount_cents, int):
            raise InvalidInputError("Amount must be a whole number of cents")
        if not 0 < amount_cents <= MAX_AMOUNT_CENTS:
            raise InvalidInputError(f"Amount must be between 1 and {MAX_AMOUNT_CENTS} cents")
        name = passenger_name.strip()
        if not name:
            raise InvalidInputError("Passenger name must not be empty")
        passport = passport_number.strip().upper()
        if not _PASSPORT.match(passport):
            raise InvalidInputError("Passport number must be 5-20 letters or digits")
        text = reason.strip()
        if not text:
            raise InvalidInputError("Reason must not be empty")
        if self._staff.get(filed_by) is None:
            raise NotFoundError("Staff member not found")
        if self._incidents.get(incident_id) is None:
            raise NotFoundError("Incident not found")

        with transaction(self._conn):
            if self._claims.find_active(incident_id, passport) is not None:
                raise DuplicateClaimError(
                    "An active compensation claim already exists for this passenger on this incident"
                )
            claim = self._claims.add(
                incident_id=incident_id,
                passenger_name=name,
                passport_number=passport,
                amount_cents=amount_cents,
                reason=text,
                filed_by=filed_by,
                now=self._clock.now(),
            )
        logger.info(
            "claim_filed",
            extra={
                "claim_id": claim.id,
                "incident_id": incident_id,
                "amount_cents": amount_cents,
                "filed_by": filed_by,
            },
        )
        return claim

    def get_claim(self, claim_id: int) -> Claim:
        claim = self._claims.get(claim_id)
        if claim is None:
            raise NotFoundError("Claim not found")
        return claim

    def list_claims(
        self, status: ClaimStatus | None = None, limit: int = 50, offset: int = 0
    ) -> tuple[list[Claim], int]:
        if not 1 <= limit <= MAX_PAGE_SIZE:
            raise InvalidInputError(f"limit must be between 1 and {MAX_PAGE_SIZE}")
        if offset < 0:
            raise InvalidInputError("offset must not be negative")
        return self._claims.list(status, limit, offset)

    def cancel_claim(self, claim_id: int, actor_id: int) -> Claim:
        actor = self._staff.get(actor_id)
        if actor is None:
            raise NotFoundError("Staff member not found")
        with transaction(self._conn):
            claim = self._claims.get(claim_id)
            if claim is None:
                raise NotFoundError("Claim not found")
            if claim.status is not ClaimStatus.FILED:
                raise InvalidStateError(
                    f"Only filed claims can be cancelled (current status: {claim.status.value})"
                )
            if actor.id != claim.filed_by and actor.role is Role.AGENT:
                raise PermissionDeniedError("Only the filer or a supervisor can cancel a claim")
            updated = self._claims.set_status(claim_id, ClaimStatus.CANCELLED, self._clock.now())
        logger.info("claim_cancelled", extra={"claim_id": claim_id, "actor_id": actor_id})
        return updated
