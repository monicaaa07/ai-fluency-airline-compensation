"""HTTP-level tests. Requires fastapi and httpx (see requirements.txt)."""
import unittest

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app

ALICE = {"X-Staff-Id": "1"}
BEN = {"X-Staff-Id": "2"}


def make_client() -> TestClient:
    app = create_app(Settings(db_path=":memory:", seed_demo_data=True, log_level="WARNING"))
    return TestClient(app)


def make_incident(client: TestClient) -> int:
    resp = client.post(
        "/incidents",
        json={"flight_number": "BA123", "flight_date": "2026-01-10", "kind": "cancellation"},
        headers=ALICE,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def claim_body(incident_id: int, **overrides) -> dict:
    body = {
        "incident_id": incident_id,
        "passenger_name": "Jo Passenger",
        "passport_number": "X1234567",
        "amount_cents": 15000,
        "reason": "Flight cancelled with under 24h notice",
    }
    body.update(overrides)
    return body


class ClaimApiTests(unittest.TestCase):
    def setUp(self):
        self.client = make_client()
        self.incident_id = make_incident(self.client)

    def test_health(self):
        self.assertEqual(self.client.get("/health").json(), {"status": "ok"})

    def test_file_claim_returns_masked_passport(self):
        resp = self.client.post("/claims", json=claim_body(self.incident_id), headers=ALICE)
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertEqual(data["passport_last4"], "4567")
        self.assertNotIn("X1234567", resp.text)
        self.assertEqual(data["status"], "filed")

    def test_missing_staff_header_is_a_validation_error(self):
        resp = self.client.post("/claims", json=claim_body(self.incident_id))
        self.assertEqual(resp.status_code, 422)
        self.assertEqual(resp.json()["error"]["code"], "invalid_input")

    def test_unknown_staff_is_forbidden(self):
        resp = self.client.post("/claims", json=claim_body(self.incident_id), headers={"X-Staff-Id": "99"})
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(resp.json()["error"]["code"], "forbidden")

    def test_validation_errors_do_not_echo_input(self):
        resp = self.client.post(
            "/claims", json=claim_body(self.incident_id, passport_number="X1", amount_cents=5), headers=ALICE
        )
        self.assertEqual(resp.status_code, 422)
        fields = resp.json()["error"]["fields"]
        self.assertTrue(all(set(f) == {"field", "message"} for f in fields))
        self.assertNotIn('"input"', resp.text)

    def test_float_amount_is_rejected(self):
        resp = self.client.post("/claims", json=claim_body(self.incident_id, amount_cents=19.99), headers=ALICE)
        self.assertEqual(resp.status_code, 422)

    def test_duplicate_claim_conflicts(self):
        self.client.post("/claims", json=claim_body(self.incident_id), headers=ALICE)
        resp = self.client.post("/claims", json=claim_body(self.incident_id), headers=BEN)
        self.assertEqual(resp.status_code, 409)
        self.assertEqual(resp.json()["error"]["code"], "duplicate_claim")

    def test_list_and_get_and_cancel(self):
        created = self.client.post("/claims", json=claim_body(self.incident_id), headers=ALICE).json()
        listing = self.client.get("/claims?limit=10", headers=ALICE).json()
        self.assertEqual(listing["total"], 1)
        self.assertEqual(self.client.get(f"/claims/{created['id']}", headers=ALICE).status_code, 200)
        forbidden = self.client.post(f"/claims/{created['id']}/cancel", headers=BEN)
        self.assertEqual(forbidden.status_code, 403)
        cancelled = self.client.post(f"/claims/{created['id']}/cancel", headers=ALICE)
        self.assertEqual(cancelled.json()["status"], "cancelled")

    def test_unknown_claim_is_404(self):
        resp = self.client.get("/claims/999", headers=ALICE)
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json()["error"]["code"], "not_found")


class IncidentApiTests(unittest.TestCase):
    def setUp(self):
        self.client = make_client()

    def test_create_get_and_updates(self):
        incident_id = make_incident(self.client)
        self.assertEqual(self.client.get(f"/incidents/{incident_id}", headers=ALICE).status_code, 200)
        posted = self.client.post(f"/incidents/{incident_id}/updates", json={"note": "Crew delayed"}, headers=ALICE)
        self.assertEqual(posted.status_code, 201)
        notes = self.client.get(f"/incidents/{incident_id}/updates", headers=ALICE).json()
        self.assertEqual([n["note"] for n in notes], ["Crew delayed"])

    def test_bad_flight_number_is_422(self):
        resp = self.client.post(
            "/incidents",
            json={"flight_number": "BA12345", "flight_date": "2026-01-10", "kind": "delay"},
            headers=ALICE,
        )
        self.assertEqual(resp.status_code, 422)


if __name__ == "__main__":
    unittest.main()
