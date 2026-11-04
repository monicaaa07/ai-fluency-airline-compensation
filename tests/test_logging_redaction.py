import io
import json
import logging
import unittest

from app.logging_config import JsonFormatter, RedactingFilter
from tests.helpers import file_claim, make_container, make_incident


def _logger_with_buffer(name: str):
    buffer = io.StringIO()
    handler = logging.StreamHandler(buffer)
    handler.setFormatter(JsonFormatter())
    handler.addFilter(RedactingFilter())
    logger = logging.getLogger(name)
    logger.handlers[:] = [handler]
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger, buffer


class RedactionTests(unittest.TestCase):
    def test_extra_fields_named_passport_are_redacted(self):
        logger, buffer = _logger_with_buffer("test.redaction.extra")
        logger.info("claim_filed", extra={"passport_number": "SECRET9999", "claim_id": 7})
        line = json.loads(buffer.getvalue())
        self.assertEqual(line["passport_number"], "[REDACTED]")
        self.assertEqual(line["claim_id"], 7)
        self.assertNotIn("SECRET9999", buffer.getvalue())

    def test_passport_in_message_text_is_redacted(self):
        logger, buffer = _logger_with_buffer("test.redaction.message")
        logger.info("lookup failed for passport_number=SECRET9999")
        self.assertNotIn("SECRET9999", buffer.getvalue())

    def test_filing_a_claim_never_logs_the_passport(self):
        logger, buffer = _logger_with_buffer("app.services.claims")
        container = make_container()
        self.addCleanup(container.conn.close)
        file_claim(container, make_incident(container).id, passport="SECRET9999")
        self.assertIn("claim_filed", buffer.getvalue())
        self.assertNotIn("SECRET9999", buffer.getvalue())


if __name__ == "__main__":
    unittest.main()
