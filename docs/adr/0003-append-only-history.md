# ADR 0003: History and audit tables are append-only

**Status:** Accepted

## Context
Compliance must show who did what and when. A record that can be edited cannot be trusted
as evidence, even if nobody edits it today.

## Decision
Any table that records history or audit facts is append-only.

- Repositories for these tables expose `add` and read methods only. There is no update or delete.
- The database enforces it: `BEFORE UPDATE` and `BEFORE DELETE` triggers abort (see `incident_updates` in `001_initial.sql`).
- A correction is a new row that refers to the one it corrects. It never overwrites.
- Current state (for example a claim's status) may live in a mutable column, but every change to it also writes a history row in the same transaction.

## Consequences
- Tampering fails at the database, not just by convention.
- Writing the history row and changing the state must share one transaction, or they can disagree.
