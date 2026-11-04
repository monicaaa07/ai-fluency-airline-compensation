# Architecture

## Shape

```
HTTP request
   |
   v
app/api/routers/*        parse + validate input (pydantic), call one service method
   |
   v
app/services/*           business rules, permissions, transactions, logging
   |
   v
app/repositories/*       SQL only; translate DB errors to domain errors
   |
   v
SQLite (app/migrations)  schema owned by numbered .sql files
```

`app/domain.py` (types, enums) and `app/errors.py` (domain errors) are shared by every layer and import nothing from the layers.

**Dependency rule:** arrows point down only. A service never imports a router or a schema. A repository never imports a service. See ADR 0001.

## Request flow: filing a claim

1. `POST /claims` hits `routers/claims.py`; `ClaimCreate` validates the body.
2. The `CurrentStaff` dependency reads `X-Staff-Id` and loads the staff member.
3. The router calls `ClaimService.file_claim(...)`.
4. The service validates, opens `transaction(conn)`, checks for an active duplicate, and calls `ClaimRepository.add`.
5. The router converts the returned `Claim` to `ClaimOut` (which exposes `passport_last4` only).
6. Any `DomainError` raised on the way is turned into a JSON error by `api/error_handlers.py`.

## Conventions

| Topic | Convention |
|---|---|
| Errors | Raise `DomainError` subclasses; never `HTTPException` in services. Body: `{"error": {"code", "message"}}` |
| Validation errors | List `field` and `message` only. Never echo submitted input (it may hold a passport number) |
| Transactions | Services use `with transaction(conn)`; repositories never commit |
| Time | `Clock.now()` injected into services; stored as ISO-8601 UTC strings |
| Money | Integer cents, fields named `*_cents` |
| Pagination | `limit` (1-200, default 50), `offset`; response `{items, total, limit, offset}` |
| IDs in responses | Integers; staff are referenced by id, never by name or email |
| Logging | `logging.getLogger(__name__)`, event names like `claim_filed`, context in `extra={...}`; no PII |
| Schema | Numbered migrations in `app/migrations/`; append-only tables protected by triggers |
| Tests | Mirror the source tree (`tests/services`, `tests/repositories`, `tests/api`); service-level tests first |
| Concurrency | Routes are `async def` and the single SQLite connection is used on the event-loop thread. Fine at demo scale; revisit before real load |

## Adding a feature: checklist

1. Read `docs/COMPENSATION_POLICY.md` and the ADRs that touch your change.
2. Write the migration (`app/migrations/00N_*.sql`). Do not edit earlier ones.
3. Extend `domain.py` (enums, dataclasses) and, if a status is added, review `ACTIVE_STATUSES`.
4. Add repository methods (SQL only).
5. Put the rules in a service method; raise domain errors; log events without PII.
6. Add schemas and a thin router. Map any new error codes in `error_handlers.py`.
7. Wire new classes in `container.py`.
8. Tests: service rules first, then DB-level guarantees, then API behavior.
9. Update this document if you introduced a new convention.
