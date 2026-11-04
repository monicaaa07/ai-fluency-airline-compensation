# ADR 0006: Schema changes are numbered SQL migrations

**Status:** Accepted

## Context
Editing the schema in place makes environments drift, and you cannot tell which version a database is on.

## Decision
- Schema lives in `app/migrations/NNN_description.sql`, applied in order at startup and recorded in `schema_migrations`.
- An applied migration is never edited. Change the schema with a new migration.
- SQLite cannot alter a CHECK constraint or drop a partial index in place. When needed, the migration drops and recreates the index, or rebuilds the table.
- Enum-like columns (such as claim `status`) are validated in the domain layer rather than with CHECK constraints, so adding a value needs no table rebuild.

## Consequences
- Every database can be brought to the current schema by running the app.
- A change to what counts as an "active" claim must update both `ACTIVE_STATUSES` in code and the partial unique index in a new migration.
