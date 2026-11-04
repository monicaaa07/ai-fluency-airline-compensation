# ADR 0001: Layered architecture with a one-way dependency rule

**Status:** Accepted

## Context
Several teams will extend this service. Without clear boundaries, business rules end up
scattered across routers and SQL, which makes them hard to test and easy to bypass.

## Decision
Four layers: routers -> services -> repositories -> database. Dependencies point down only.

- Routers parse input and call one service method. No SQL, no business rules.
- Services hold rules, permissions, and transaction boundaries. They do not import fastapi or pydantic.
- Repositories hold SQL, never commit, and translate database errors into domain errors.
- Wiring lives in `app/container.py`.

## Consequences
- Rules can be tested without HTTP.
- A rule enforced only in a router is a bug: other callers would skip it.
- A new feature touches every layer, which is expected.
