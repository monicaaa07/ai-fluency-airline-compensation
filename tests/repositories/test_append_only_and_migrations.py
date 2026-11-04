import sqlite3
import unittest

from app.db import apply_migrations, connect
from app.repositories.incident_updates import IncidentUpdateRepository
from tests.helpers import ALICE, make_container, make_incident


class AppendOnlyTests(unittest.TestCase):
    def setUp(self):
        self.c = make_container()
        self.addCleanup(self.c.conn.close)
        incident = make_incident(self.c)
        self.c.incident_service.add_update(incident.id, "Original note", ALICE)

    def test_repository_has_no_update_or_delete_methods(self):
        repo = IncidentUpdateRepository(self.c.conn)
        for name in ("update", "delete", "remove", "set_note"):
            self.assertFalse(hasattr(repo, name), name)

    def test_database_rejects_update(self):
        with self.assertRaises(sqlite3.DatabaseError):
            self.c.conn.execute("UPDATE incident_updates SET note = 'tampered'")

    def test_database_rejects_delete(self):
        with self.assertRaises(sqlite3.DatabaseError):
            self.c.conn.execute("DELETE FROM incident_updates")


class MigrationTests(unittest.TestCase):
    def test_migrations_apply_once_and_are_idempotent(self):
        conn = connect(":memory:")
        self.addCleanup(conn.close)
        first = apply_migrations(conn)
        second = apply_migrations(conn)
        self.assertIn("001_initial", first)
        self.assertEqual(second, [])


class DuplicateIndexTests(unittest.TestCase):
    def test_database_enforces_one_active_claim_per_passenger_per_incident(self):
        c = make_container()
        self.addCleanup(c.conn.close)
        incident = make_incident(c)
        insert = (
            "INSERT INTO claims (incident_id, passenger_name, passport_number, amount_cents, reason, "
            "status, filed_by, created_at, updated_at) VALUES (?, 'Jo', 'X1234567', 100, 'r', 'filed', 1, 't', 't')"
        )
        c.conn.execute(insert, (incident.id,))
        with self.assertRaises(sqlite3.IntegrityError):
            c.conn.execute(insert, (incident.id,))


if __name__ == "__main__":
    unittest.main()
