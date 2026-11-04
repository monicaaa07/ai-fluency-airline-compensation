"""Wires repositories and services together. The only place that knows all of them."""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from app.clock import Clock
from app.repositories.claims import ClaimRepository
from app.repositories.incident_updates import IncidentUpdateRepository
from app.repositories.incidents import IncidentRepository
from app.repositories.staff import StaffRepository
from app.services.claims import ClaimService
from app.services.incidents import IncidentService


@dataclass(frozen=True)
class Container:
    conn: sqlite3.Connection
    clock: Clock
    staff: StaffRepository
    incident_service: IncidentService
    claim_service: ClaimService


def build_container(conn: sqlite3.Connection, clock: Clock) -> Container:
    staff = StaffRepository(conn)
    incidents = IncidentRepository(conn)
    updates = IncidentUpdateRepository(conn)
    claims = ClaimRepository(conn)
    return Container(
        conn=conn,
        clock=clock,
        staff=staff,
        incident_service=IncidentService(conn, incidents, updates, staff, clock),
        claim_service=ClaimService(conn, claims, incidents, staff, clock),
    )
