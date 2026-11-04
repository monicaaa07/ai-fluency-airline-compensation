from __future__ import annotations

import sqlite3

from app.domain import Role, Staff


class StaffRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def add(self, name: str, role: Role) -> Staff:
        cur = self._conn.execute("INSERT INTO staff (name, role) VALUES (?, ?)", (name, role.value))
        return Staff(id=cur.lastrowid, name=name, role=role)

    def get(self, staff_id: int) -> Staff | None:
        row = self._conn.execute("SELECT id, name, role FROM staff WHERE id = ?", (staff_id,)).fetchone()
        if row is None:
            return None
        return Staff(id=row["id"], name=row["name"], role=Role(row["role"]))

    def count(self) -> int:
        return self._conn.execute("SELECT COUNT(*) AS n FROM staff").fetchone()["n"]
