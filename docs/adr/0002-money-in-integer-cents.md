# ADR 0002: Money is stored and handled as integer cents

**Status:** Accepted

## Context
Floating-point arithmetic cannot represent values like 19.99 exactly. Small rounding
errors in compensation amounts become audit findings.

## Decision
All monetary amounts are integers counting cents, in code, API, and database.

- Fields and columns end in `_cents` (`amount_cents`).
- Floats and bools are rejected as amounts; the API schema uses a strict integer.
- Convert to dollars only for display, at the edge.

## Consequences
- `$19.99` is `1999` everywhere. There is no rounding to reason about.
- Policy thresholds are written in cents in code (`$200.00` is `20_000`).
