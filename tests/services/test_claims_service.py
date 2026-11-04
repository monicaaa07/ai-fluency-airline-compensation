import unittest

from app.domain import ClaimStatus
from app.errors import (
    DuplicateClaimError,
    InvalidInputError,
    InvalidStateError,
    NotFoundError,
    PermissionDeniedError,
)
from tests.helpers import ALICE, BEN, SAM, file_claim, make_container, make_incident


class FileClaimTests(unittest.TestCase):
    def setUp(self):
        self.c = make_container()
        self.addCleanup(self.c.conn.close)
        self.incident = make_incident(self.c)

    def test_files_claim_with_amount_in_cents(self):
        claim = file_claim(self.c, self.incident.id, amount_cents=1999)
        self.assertEqual(claim.amount_cents, 1999)
        self.assertIs(claim.status, ClaimStatus.FILED)
        self.assertEqual(claim.filed_by, ALICE)

    def test_normalises_passport_and_exposes_last4_only_helper(self):
        claim = file_claim(self.c, self.incident.id, passport=" ab12345678 ")
        self.assertEqual(claim.passport_last4, "5678")

    def test_passport_is_not_in_repr(self):
        claim = file_claim(self.c, self.incident.id, passport="SECRET9999")
        self.assertNotIn("SECRET9999", repr(claim))

    def test_rejects_float_amounts(self):
        with self.assertRaises(InvalidInputError):
            file_claim(self.c, self.incident.id, amount_cents=19.99)  # type: ignore[arg-type]

    def test_rejects_bool_amounts(self):
        with self.assertRaises(InvalidInputError):
            file_claim(self.c, self.incident.id, amount_cents=True)  # type: ignore[arg-type]

    def test_rejects_zero_and_oversized_amounts(self):
        for bad in (0, -5, 5_000_001):
            with self.subTest(amount=bad), self.assertRaises(InvalidInputError):
                file_claim(self.c, self.incident.id, amount_cents=bad)

    def test_rejects_bad_passport(self):
        with self.assertRaises(InvalidInputError):
            file_claim(self.c, self.incident.id, passport="12")

    def test_unknown_incident_and_staff(self):
        with self.assertRaises(NotFoundError):
            file_claim(self.c, 999)
        with self.assertRaises(NotFoundError):
            file_claim(self.c, self.incident.id, filed_by=999)

    def test_duplicate_active_claim_is_rejected(self):
        file_claim(self.c, self.incident.id)
        with self.assertRaises(DuplicateClaimError):
            file_claim(self.c, self.incident.id, filed_by=BEN)

    def test_same_passenger_can_claim_on_a_different_incident(self):
        other = make_incident(self.c, "LH456")
        file_claim(self.c, self.incident.id)
        file_claim(self.c, other.id)

    def test_can_refile_after_cancellation(self):
        first = file_claim(self.c, self.incident.id)
        self.c.claim_service.cancel_claim(first.id, ALICE)
        second = file_claim(self.c, self.incident.id)
        self.assertNotEqual(first.id, second.id)


class CancelClaimTests(unittest.TestCase):
    def setUp(self):
        self.c = make_container()
        self.addCleanup(self.c.conn.close)
        self.claim = file_claim(self.c, make_incident(self.c).id)

    def test_filer_can_cancel(self):
        cancelled = self.c.claim_service.cancel_claim(self.claim.id, ALICE)
        self.assertIs(cancelled.status, ClaimStatus.CANCELLED)

    def test_supervisor_can_cancel_someone_elses_claim(self):
        cancelled = self.c.claim_service.cancel_claim(self.claim.id, SAM)
        self.assertIs(cancelled.status, ClaimStatus.CANCELLED)

    def test_other_agent_cannot_cancel(self):
        with self.assertRaises(PermissionDeniedError):
            self.c.claim_service.cancel_claim(self.claim.id, BEN)

    def test_cannot_cancel_twice(self):
        self.c.claim_service.cancel_claim(self.claim.id, ALICE)
        with self.assertRaises(InvalidStateError):
            self.c.claim_service.cancel_claim(self.claim.id, ALICE)

    def test_unknown_claim(self):
        with self.assertRaises(NotFoundError):
            self.c.claim_service.cancel_claim(999, ALICE)


class ListClaimsTests(unittest.TestCase):
    def setUp(self):
        self.c = make_container()
        self.addCleanup(self.c.conn.close)
        incident = make_incident(self.c)
        for i in range(5):
            file_claim(self.c, incident.id, passport=f"P{i:07d}")

    def test_paginates_newest_first(self):
        items, total = self.c.claim_service.list_claims(limit=2, offset=0)
        self.assertEqual(total, 5)
        self.assertEqual([c.id for c in items], [5, 4])

    def test_filters_by_status(self):
        self.c.claim_service.cancel_claim(1, ALICE)
        items, total = self.c.claim_service.list_claims(status=ClaimStatus.CANCELLED)
        self.assertEqual((len(items), total), (1, 1))

    def test_rejects_bad_paging(self):
        for kwargs in ({"limit": 0}, {"limit": 201}, {"offset": -1}):
            with self.subTest(**kwargs), self.assertRaises(InvalidInputError):
                self.c.claim_service.list_claims(**kwargs)


if __name__ == "__main__":
    unittest.main()
