# Run A: the one-line prompt

**Goal:** show what you get when you treat Claude Code like a search box.

## Setup
Run `demo/prepare_runs.sh <folder>` and open `<folder>/run-a-one-line` in Claude Code. This copy
deliberately has **no** `CLAUDE.md`, no `docs/`, and no demo files. Only the code.

## The prompt (paste exactly, nothing else)

```
Add an approval workflow with an audit trail to the compensation claims service.
```

## Rules for the facilitator
- Do not add context, answer follow-up questions with extra detail, or steer. If Claude asks something, reply "use your best judgment".
- Accept the result. Do not iterate. The point is the first answer.
- Let it finish, run `pytest`, then **stop**. Save the folder untouched for scoring.

## While you wait, narrate (briefly)
- "Notice what I did not say: who can approve, what the limits are, how history must be stored."
- "Claude will fill those gaps with reasonable guesses. Reasonable is not the same as correct for *our* business."

## What often happens (not guaranteed)
Runs vary. Typical gaps are listed in `SCORECARD.md`. If Run A does surprisingly well, say so,
then ask the audience: *"How would you know? What would you check?"* That is Discernment.
