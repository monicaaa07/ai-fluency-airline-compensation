from __future__ import annotations

import sqlite3
from datetime import date, datetime

from app.domain import Incident, IncidentKind

_COLUMNS = "id, flight_number, flight_date, kind, created_at"


def _to_incident(row: sqlite3.Row) -> Incident:
    return Incident(
        id=row["id"],
        flight_number=row["flight_number"],
        flight_date=date.fromisoformat(row["flight_date"]),
        kind=IncidentKind(row["kind"]),
        created_at=datetime.fromisoformat(row["created_at"]),
    )


class IncidentRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def add(self, flight_number: str, flight_date: date, kind: IncidentKind, created_at: datetime) -> Incident:
        cur = self._conn.execute(
            "INSERT INTO incidents (flight_number, flight_date, kind, created_at) VALUES (?, ?, ?, ?)",
            (flight_number, flight_date.isoformat(), kind.value, created_at.isoformat()),
        )
        return self.get(cur.lastrowid)  # type: ignore[return-value]

    def get(self, incident_id: int) -> Incident | None:
        row = self._conn.execute(
            f"SELECT {_COLUMNS} FROM incidents WHERE id = ?", (incident_id,)
        ).fetchone()
        return None if row is None else _to_incident(row)
