"""Shared test setup. Tests are unittest-style classes, run with pytest."""
from __future__ import annotations

from datetime import date, datetime, timezone

from app.clock import FixedClock
from app.container import Container, build_container
from app.db import apply_migrations, connect
from app.domain import Incident, IncidentKind
from app.seed import seed_staff

ALICE, BEN, SAM, MAYA = 1, 2, 3, 4  # seeded staff ids: two agents, a supervisor, a manager

START = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)


def make_container() -> Container:
    conn = connect(":memory:")
    apply_migrations(conn)
    seed_staff(conn)
    return build_container(conn, FixedClock(START))


def make_incident(container: Container, flight_number: str = "BA123") -> Incident:
    return container.incident_service.create_incident(
        flight_number, date(2026, 1, 10), IncidentKind.CANCELLATION
    )


def file_claim(container: Container, incident_id: int, *, passport: str = "X1234567", amount_cents: int = 15000,
               filed_by: int = ALICE):
    return container.claim_service.file_claim(
        incident_id=incident_id,
        passenger_name="Jo Passenger",
        passport_number=passport,
        amount_cents=amount_cents,
        reason="Flight cancelled with under 24h notice",
        filed_by=filed_by,
    )
