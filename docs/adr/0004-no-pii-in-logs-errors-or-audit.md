# ADR 0004: Passport numbers never leave the claim record

**Status:** Accepted

## Context
Passport numbers are sensitive personal data. Logs, error messages, and audit exports are
copied into tools with much wider access than the claims database.

## Decision
A passport number is stored once, on the claim, and appears nowhere else.

- Not in log lines. A redacting filter is a safety net, not permission to log it.
- Not in error messages or validation errors. Validation errors list field names and messages only; they never echo the submitted input.
- Not in audit or history rows. Refer to a claim by id.
- Not in API responses. Responses expose `passport_last4` only.
- The `Claim` dataclass hides it from `repr()`.

## Consequences
- Anything that needs to identify a claim uses its id.
- New code that handles claim data must be checked against this list.
