# Airline Compensation Service

FastAPI service that tracks flight disruptions ("incidents") and the compensation
claims staff file for affected passengers. Python 3.12, SQLite, pytest.

## Commands

- Install: `pip install -r requirements.txt`
- Test: `pytest`
- Run: `uvicorn app.main:create_app --factory --reload`
- Demo staff are seeded: 1 = Alice (agent), 2 = Ben (agent), 3 = Sam (supervisor), 4 = Maya (manager).
  Callers identify with an `X-Staff-Id` header.

## Layers (ADR 0001)

`routers -> services -> repositories -> SQLite`, with `domain.py` and `errors.py` shared by all.

- Routers (`app/api/routers/`) are thin: parse input, call ONE service method, shape output. No SQL, no business rules.
- Services (`app/services/`) hold business rules and own transactions (`with transaction(conn)`). They never import fastapi or pydantic.
- Repositories (`app/repositories/`) hold SQL only and never commit. They translate database errors into domain errors.
- Wiring happens in `app/container.py` and nowhere else.

## House rules (non-negotiable)

1. **Money is integer cents.** Never float or Decimal. Name fields `*_cents`. (ADR 0002)
2. **History is append-only.** Audit and history tables get no UPDATE or DELETE: not in code, and the database blocks it with triggers. Corrections are new rows. (ADR 0003)
3. **Passport numbers are PII.** They never appear in logs, error bodies, validation errors, audit rows, or API responses (use `passport_last4`). (ADR 0004)
4. **Errors are domain errors.** Raise subclasses of `DomainError` from `app/errors.py`; the API layer maps them. Error bodies always look like `{"error": {"code", "message"}}`. (ADR 0005)
5. **Schema changes are new numbered migrations** in `app/migrations/`. Never edit an applied migration. (ADR 0006)
6. **Time comes from the injected `Clock`.** Never call `datetime.now()` in a service. Timestamps are UTC. (ADR 0007)
7. **List endpoints paginate** with `limit` (default 50, max 200) and `offset`, and return `{items, total, limit, offset}`.

## Business rules

Who may approve what, claim limits, and what counts as a duplicate live in
`docs/COMPENSATION_POLICY.md`. Read it before touching the claim lifecycle.
Architecture detail and a "how to add a feature" checklist are in `docs/ARCHITECTURE.md`.

## Definition of done

- Tests added for every new rule, at the service layer first, then the API.
- `pytest` passes.
- No new rule is enforced only in a router.
- Any rule you were unsure about is called out in your summary, not guessed silently.
