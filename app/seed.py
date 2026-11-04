"""Demo staff. IDs are deterministic: 1=Alice, 2=Ben, 3=Sam, 4=Maya."""
from __future__ import annotations

import sqlite3

from app.domain import Role
from app.repositories.staff import StaffRepository

DEMO_STAFF = [
    ("Alice Agent", Role.AGENT),
    ("Ben Agent", Role.AGENT),
    ("Sam Supervisor", Role.SUPERVISOR),
    ("Maya Manager", Role.MANAGER),
]


def seed_staff(conn: sqlite3.Connection) -> None:
    repo = StaffRepository(conn)
    if repo.count() > 0:
        return
    for name, role in DEMO_STAFF:
        repo.add(name, role)
