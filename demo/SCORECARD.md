# Scorecard

Score both runs on the same ten situations. The left side is written for everyone; **Where to look**
is for people who want to read code.

**Scoring per row:** 0 = missing or wrong, 1 = partly handled, 2 = handled correctly.
Maximum 20 per run. Outputs vary from run to run, so treat the scores as a conversation starter, not a benchmark.

| # | Situation (plain English) | Why it matters | Where to look | Run A | Run B |
|---|---|---|---|---|---|
| 1 | An agent approves a **$150** claim filed by someone else | Normal case must work | Approval service method; its tests | | |
| 2 | An agent tries to approve a **$600** claim | Agents have a limit; bigger claims escalate | Tier check in the service (`COMPENSATION_POLICY.md`) | | |
| 3 | A supervisor tries to approve **$1,500** | Only managers approve above $1,000 | Same tier check | | |
| 4 | Someone approves **a claim they filed themselves** | Separation of duties applies to everyone, even managers | Service compares actor to `filed_by` | | |
| 5 | A rejection with **no reason** | Auditors need to know why | Validation for the reject path | | |
| 6 | After approval, someone **files another claim** for the same passenger and incident | One compensation per passenger per incident; *approved* claims count | `ACTIVE_STATUSES` in `domain.py` **and** the unique index (needs a new migration) | | |
| 7 | An auditor asks: **who decided what, when, from what to what, for what amount?** | The audit record must be complete | History table columns and the API that reads it | | |
| 8 | Someone tries to **edit or delete** a history entry | Evidence must not be alterable | No update/delete in the repository; database triggers (ADR 0003) | | |
| 9 | Look for **passport numbers** in logs, history rows, and error messages (including validation errors) | PII must not leak (ADR 0004) | Log calls, history columns, error handlers | | |
| 10 | Does it **look like the rest of the system**? Layers respected, domain errors, new migration (not an edited one), injected clock, money in cents, tests added | Maintainability and trust | Compare with `docs/ARCHITECTURE.md` checklist | | |

**Totals:** Run A ____ / 20  Run B ____ / 20

## Quick checks for graders

- **Row 6:** grep for `ACTIVE_STATUSES`. Did it change? Did a new migration drop and recreate `ux_claims_one_active_per_passenger_incident`?
- **Row 8:** does the new history table have `BEFORE UPDATE` / `BEFORE DELETE` triggers, and does its repository avoid update/delete methods?
- **Row 9:** grep new code and tests for `passport`. Check that history rows reference the claim by id only. Post an invalid claim and read the error body.
- **Row 10:** `git diff --stat` against the baseline commit, and read whether `app/migrations/001_initial.sql` was touched.

## Common traps (facilitator only; do not show before Run A)

1. Policy limits invented or ignored (Run A cannot know them).
2. History stored by overwriting columns on the claim instead of an append-only table.
3. Approved claims no longer blocking duplicates (index and `ACTIVE_STATUSES` not updated).
4. Self-approval allowed for senior roles.
5. Rejection reasons optional.
6. Passport number copied into history rows, logs, or echoed in validation errors.
7. Editing `001_initial.sql` instead of adding `002_...`.
8. Business logic placed in the router.

## Debrief questions

- Where did Run B's advantage come from: a better prompt, or better information and better review?
- Which of the 4Ds mattered most for each of the ten rows?
- If Run A had scored well, would you have known? How?
