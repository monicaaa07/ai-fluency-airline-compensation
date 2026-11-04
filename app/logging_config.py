"""Structured JSON logging with passport redaction (ADR 0004)."""
from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone

SENSITIVE_KEYS = ("passport_number", "passport")
_PATTERN = re.compile(r"(passport(?:_number)?\s*[=:]\s*)\S+", re.IGNORECASE)
_RESERVED = set(logging.LogRecord("x", 0, "x", 0, "x", (), None).__dict__) | {"message", "asctime"}


def redact(text: str) -> str:
    return _PATTERN.sub(r"\1[REDACTED]", text)


class RedactingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        for key in SENSITIVE_KEYS:
            if hasattr(record, key):
                setattr(record, key, "[REDACTED]")
        record.msg = redact(record.getMessage())
        record.args = ()
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.fromtimestamp(record.created, timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key, value in record.__dict__.items():
            if key not in _RESERVED and not key.startswith("_"):
                payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    handler.addFilter(RedactingFilter())
    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(level)
