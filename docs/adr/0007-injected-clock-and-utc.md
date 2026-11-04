# ADR 0007: Time comes from an injected clock, in UTC

**Status:** Accepted

## Context
Code that calls `datetime.now()` directly cannot be tested deterministically, and mixed
time zones corrupt audit timelines.

## Decision
- Services receive a `Clock` and call `clock.now()`. They never call `datetime.now()`.
- All timestamps are timezone-aware UTC, stored as ISO-8601 strings.
- Tests use `FixedClock` and advance it explicitly.
- One service call reads the clock once and uses that value for everything it writes, so related rows share a timestamp.

## Consequences
- Tests can assert exact timestamps.
- An audit entry and the state change it records carry the same moment.
