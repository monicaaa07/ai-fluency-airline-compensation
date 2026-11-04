from __future__ import annotations

import sqlite3
from datetime import datetime

from app.domain import ACTIVE_STATUSES, Claim, ClaimStatus
from app.errors import DuplicateClaimError

_COLUMNS = (
    "id, incident_id, passenger_name, passport_number, amount_cents, reason, "
    "status, filed_by, created_at, updated_at"
)


def _to_claim(row: sqlite3.Row) -> Claim:
    return Claim(
        id=row["id"],
        incident_id=row["incident_id"],
        passenger_name=row["passenger_name"],
        passport_number=row["passport_number"],
        amount_cents=row["amount_cents"],
        reason=row["reason"],
        status=ClaimStatus(row["status"]),
        filed_by=row["filed_by"],
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


class ClaimRepository:
    """Repositories translate database errors into domain errors (ADR 0001)."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def add(
        self,
        *,
        incident_id: int,
        passenger_name: str,
        passport_number: str,
        amount_cents: int,
        reason: str,
        filed_by: int,
        now: datetime,
    ) -> Claim:
        try:
            cur = self._conn.execute(
                "INSERT INTO claims (incident_id, passenger_name, passport_number, amount_cents, "
                "reason, status, filed_by, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    incident_id,
                    passenger_name,
                    passport_number,
                    amount_cents,
                    reason,
                    ClaimStatus.FILED.value,
                    filed_by,
                    now.isoformat(),
                    now.isoformat(),
                ),
            )
        except sqlite3.IntegrityError as exc:
            if "UNIQUE constraint failed" in str(exc):
                raise DuplicateClaimError(
                    "An active compensation claim already exists for this passenger on this incident"
                ) from exc
            raise
        return self.get(cur.lastrowid)  # type: ignore[return-value]

    def get(self, claim_id: int) -> Claim | None:
        row = self._conn.execute(f"SELECT {_COLUMNS} FROM claims WHERE id = ?", (claim_id,)).fetchone()
        return None if row is None else _to_claim(row)

    def find_active(self, incident_id: int, passport_number: str) -> Claim | None:
        placeholders = ", ".join("?" for _ in ACTIVE_STATUSES)
        row = self._conn.execute(
            f"SELECT {_COLUMNS} FROM claims WHERE incident_id = ? AND passport_number = ? "
            f"AND status IN ({placeholders})",
            (incident_id, passport_number, *[s.value for s in ACTIVE_STATUSES]),
        ).fetchone()
        return None if row is None else _to_claim(row)

    def list(self, status: ClaimStatus | None, limit: int, offset: int) -> tuple[list[Claim], int]:
        where, params = ("WHERE status = ?", [status.value]) if status else ("", [])
        total = self._conn.execute(f"SELECT COUNT(*) AS n FROM claims {where}", params).fetchone()["n"]
        rows = self._conn.execute(
            f"SELECT {_COLUMNS} FROM claims {where} ORDER BY id DESC LIMIT ? OFFSET ?",
            [*params, limit, offset],
        ).fetchall()
        return [_to_claim(r) for r in rows], total

    def set_status(self, claim_id: int, status: ClaimStatus, now: datetime) -> Claim:
        self._conn.execute(
            "UPDATE claims SET status = ?, updated_at = ? WHERE id = ?",
            (status.value, now.isoformat(), claim_id),
        )
        return self.get(claim_id)  # type: ignore[return-value]
