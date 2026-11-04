import unittest
from datetime import date

from app.domain import IncidentKind
from app.errors import InvalidInputError, NotFoundError
from tests.helpers import ALICE, make_container, make_incident


class IncidentServiceTests(unittest.TestCase):
    def setUp(self):
        self.c = make_container()
        self.addCleanup(self.c.conn.close)

    def test_creates_incident_and_normalises_flight_number(self):
        incident = self.c.incident_service.create_incident(" ba123 ", date(2026, 1, 10), IncidentKind.DELAY)
        self.assertEqual(incident.flight_number, "BA123")

    def test_rejects_bad_flight_number(self):
        for bad in ("123", "BA", "BA12345", "B-123"):
            with self.subTest(flight=bad), self.assertRaises(InvalidInputError):
                self.c.incident_service.create_incident(bad, date(2026, 1, 10), IncidentKind.DELAY)

    def test_unknown_incident(self):
        with self.assertRaises(NotFoundError):
            self.c.incident_service.get_incident(42)

    def test_updates_are_listed_in_order(self):
        incident = make_incident(self.c)
        self.c.incident_service.add_update(incident.id, "Crew delayed", ALICE)
        self.c.incident_service.add_update(incident.id, "Aircraft swapped", ALICE)
        notes = [u.note for u in self.c.incident_service.list_updates(incident.id)]
        self.assertEqual(notes, ["Crew delayed", "Aircraft swapped"])

    def test_empty_update_rejected(self):
        incident = make_incident(self.c)
        with self.assertRaises(InvalidInputError):
            self.c.incident_service.add_update(incident.id, "   ", ALICE)


if __name__ == "__main__":
    unittest.main()
