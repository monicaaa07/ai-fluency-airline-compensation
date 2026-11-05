# ai-fluency-airline-compensation

WITCON 2026 AI fluency demo with real world use case.

A small, enterprise-shaped FastAPI service for **airline passenger compensation claims**, built to
show one thing: the same AI coding task goes very differently when you apply the **AI Fluency 4Ds**
(Delegation, Description, Discernment, Diligence) than when you type a one-line prompt.

**The feature we ask Claude Code to build:** an *approval workflow with an audit trail*.

| | Run A | Run B |
|---|---|---|
| Prompt | One line | The 4D process: plan first, then build |
| Project context | Code only | Code + `CLAUDE.md` + architecture doc + policy + decision records |
| Human role | Accept whatever comes back | Delegate, describe, review the plan, verify, own the result |

Then the same four habits are applied to a task with no code at all, to show they travel to any AI tool.

## The service

Staff file compensation claims for passengers affected by a disrupted flight. Today claims can be
filed, listed, and cancelled; nothing decides them yet.

```
app/
  api/            routers (thin), dependencies, error handlers
  services/       business rules and transactions
  repositories/   SQL only
  migrations/     numbered .sql files
  domain.py       types and enums
  errors.py       domain errors
tests/            mirrors app/ (services, repositories, api)
CLAUDE.md         house rules for Claude Code
docs/             ARCHITECTURE.md, COMPENSATION_POLICY.md, adr/0001-0007
demo/             facilitator guide, run scripts, scorecard, non-coding closer
```

## Quick start

```bash
pip install -r requirements.txt
pytest
uvicorn app.main:create_app --factory --reload
```

Demo staff (send as the `X-Staff-Id` header): 1 Alice (agent), 2 Ben (agent), 3 Sam (supervisor), 4 Maya (manager).

## Running the demo

1. Read `demo/FACILITATOR_GUIDE.md`.
2. `demo/prepare_runs.sh ~/demo-runs` creates two clean folders, `run-a-one-line` and `run-b-4d`.
3. Follow `demo/RUN_A_one_line_prompt.md`, then `demo/RUN_B_4D_playbook.md`.
4. Score both. Either watch them side by side in the live console (`demo/visual/`, set-up steps in the facilitator guide) or fill in `demo/SCORECARD.md`.
5. Finish with `demo/CLOSER_non_coding_4D.md`.

> The `demo/` folder reveals the hidden rules the demo tests for. It is deliberately **not** copied into the run folders.
