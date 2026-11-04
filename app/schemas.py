"""Pydantic request/response models. The only place HTTP shapes are defined.

Responses never include the full passport number, only `passport_last4` (ADR 0004).
"""
from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, StrictInt

from app.domain import Claim, ClaimStatus, Incident, IncidentKind, IncidentUpdate


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class IncidentCreate(_Strict):
    flight_number: str = Field(min_length=3, max_length=8)
    flight_date: date
    kind: IncidentKind


class IncidentOut(BaseModel):
    id: int
    flight_number: str
    flight_date: date
    kind: IncidentKind
    created_at: datetime

    @classmethod
    def from_domain(cls, incident: Incident) -> "IncidentOut":
        return cls(
            id=incident.id,
            flight_number=incident.flight_number,
            flight_date=incident.flight_date,
            kind=incident.kind,
            created_at=incident.created_at,
        )


class IncidentUpdateCreate(_Strict):
    note: str = Field(min_length=1, max_length=500)


class IncidentUpdateOut(BaseModel):
    id: int
    incident_id: int
    note: str
    author_id: int
    created_at: datetime

    @classmethod
    def from_domain(cls, update: IncidentUpdate) -> "IncidentUpdateOut":
        return cls(
            id=update.id,
            incident_id=update.incident_id,
            note=update.note,
            author_id=update.author_id,
            created_at=update.created_at,
        )


class ClaimCreate(_Strict):
    incident_id: int
    passenger_name: str = Field(min_length=1, max_length=120)
    passport_number: str = Field(min_length=5, max_length=20)
    amount_cents: StrictInt = Field(gt=0, le=5_000_000)
    reason: str = Field(min_length=1, max_length=500)


class ClaimOut(BaseModel):
    id: int
    incident_id: int
    passenger_name: str
    passport_last4: str
    amount_cents: int
    reason: str
    status: ClaimStatus
    filed_by: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, claim: Claim) -> "ClaimOut":
        return cls(
            id=claim.id,
            incident_id=claim.incident_id,
            passenger_name=claim.passenger_name,
            passport_last4=claim.passport_last4,
            amount_cents=claim.amount_cents,
            reason=claim.reason,
            status=claim.status,
            filed_by=claim.filed_by,
            created_at=claim.created_at,
            updated_at=claim.updated_at,
        )


class ClaimList(BaseModel):
    items: list[ClaimOut]
    total: int
    limit: int
    offset: int
