"""Core domain types shared by every layer. No I/O, no framework imports."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum


class Role(str, Enum):
    AGENT = "agent"
    SUPERVISOR = "supervisor"
    MANAGER = "manager"


class IncidentKind(str, Enum):
    CANCELLATION = "cancellation"
    DELAY = "delay"
    DENIED_BOARDING = "denied_boarding"


class ClaimStatus(str, Enum):
    FILED = "filed"
    CANCELLED = "cancelled"


# Statuses that use up a passenger's single claim for an incident.
ACTIVE_STATUSES = (ClaimStatus.FILED,)


@dataclass(frozen=True)
class Staff:
    id: int
    name: str
    role: Role


@dataclass(frozen=True)
class Incident:
    id: int
    flight_number: str
    flight_date: date
    kind: IncidentKind
    created_at: datetime


@dataclass(frozen=True)
class IncidentUpdate:
    id: int
    incident_id: int
    note: str
    author_id: int
    created_at: datetime


@dataclass(frozen=True)
class Claim:
    id: int
    incident_id: int
    passenger_name: str
    # repr=False keeps the passport number out of accidental log lines (ADR 0004).
    passport_number: str = field(repr=False)
    amount_cents: int
    reason: str
    status: ClaimStatus
    filed_by: int
    created_at: datetime
    updated_at: datetime

    @property
    def passport_last4(self) -> str:
        return self.passport_number[-4:]
