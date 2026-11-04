"""Append-only by design (ADR 0003): there is deliberately no update or delete here."""
from __future__ import annotations

import sqlite3
from datetime import datetime

from app.domain import IncidentUpdate

_COLUMNS = "id, incident_id, note, author_id, created_at"


def _to_update(row: sqlite3.Row) -> IncidentUpdate:
    return IncidentUpdate(
        id=row["id"],
        incident_id=row["incident_id"],
        note=row["note"],
        author_id=row["author_id"],
        created_at=datetime.fromisoformat(row["created_at"]),
    )


class IncidentUpdateRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def add(self, incident_id: int, note: str, author_id: int, created_at: datetime) -> IncidentUpdate:
        cur = self._conn.execute(
            "INSERT INTO incident_updates (incident_id, note, author_id, created_at) VALUES (?, ?, ?, ?)",
            (incident_id, note, author_id, created_at.isoformat()),
        )
        row = self._conn.execute(
            f"SELECT {_COLUMNS} FROM incident_updates WHERE id = ?", (cur.lastrowid,)
        ).fetchone()
        return _to_update(row)

    def list_for_incident(self, incident_id: int) -> list[IncidentUpdate]:
        rows = self._conn.execute(
            f"SELECT {_COLUMNS} FROM incident_updates WHERE incident_id = ? ORDER BY id",
            (incident_id,),
        ).fetchall()
        return [_to_update(r) for r in rows]
