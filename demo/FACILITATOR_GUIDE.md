# Facilitator guide

**Audience:** non-technical stakeholders and new grads.
**Length:** about 60 minutes.
**The takeaway:** *Using the AI Fluency framework (Delegation, Description, Discernment, Diligence), you can work effectively with Claude Code, or any AI tool, on any task.*

## Before the session (do this the day before)

1. `pip install -r requirements.txt && pytest` in the main repo. Everything should pass.
   - Expect 43 tests to pass on Python 3.9 or newer (verified on macOS with Apple's Python 3.9.6). If your count differs, fix it now rather than live.
2. `demo/prepare_runs.sh ~/demo-runs` to create the two folders. Run `pytest` in each.
3. **Do a full dry run of both runs.** Outputs vary. Know roughly how long each takes (budget 10-20 minutes each) and keep the dry-run folders as a fallback.
4. Print or share `SCORECARD.md` (without the "Common traps" section) and the pocket card from `CLOSER_non_coding_4D.md`.

## Agenda

| Min | Segment | What happens |
|---|---|---|
| 0-5 | Frame | The problem: "AI as a smart stranger vs a teammate who knows your rules". Introduce the 4Ds in two sentences each. |
| 5-10 | The system | Tour the airline service (see below). One sentence per layer. Do not dive into code. |
| 10-25 | **Run A** | One-line prompt, `RUN_A_one_line_prompt.md`. Narrate what is *not* being said. Do not rescue it. |
| 25-45 | **Run B** | The 4D playbook, `RUN_B_4D_playbook.md`. Make the audience do the Delegation table and review the plan. |
| 45-52 | Score | Open the live side-by-side console (see below) and press **Run all situations**. Fall back to `SCORECARD.md` by show of hands if the servers will not start. |
| 52-60 | **Closer** | The non-coding policy-memo exercise from `CLOSER_non_coding_4D.md`, then the pocket card. |

## Live side-by-side console (the visual scorecard)

`demo/visual/` is a browser page that sends the same ten situations to the finished Run A and Run B apps and shows what each one actually did, as green and red cards with a running tally. It changes neither app and needs only Python's standard library.

It needs **both finished builds**, so set it up after both runs are done and their tests pass. Use four Terminal windows, one command each:

```bash
# 1. Run A's app
cd ~/Claude/demo-runs/run-a-one-line && source .venv/bin/activate && AIRLINE_DB_PATH=:memory: uvicorn app.main:create_app --factory --port 8001

# 2. Run B's app
cd ~/Claude/demo-runs/run-b-4d && source .venv/bin/activate && AIRLINE_DB_PATH=:memory: uvicorn app.main:create_app --factory --port 8002

# 3. The console (from the main repo folder, not a run folder)
cd ~/Claude/ai-fluency-airline-compensation && python3 demo/visual/console.py
```

Then open http://127.0.0.1:9000 and press **Run all situations**. `AIRLINE_DB_PATH=:memory:` gives each app a fresh database every time it starts, so reruns stay clean. If an app is not running, the page shows the command to start it.

Notes:
- The page reads each app's own published API description to find the approve, reject and history endpoints, so it adapts to what each run built. If a run named things unexpectedly, that card says "Not built" or "Could not set this up", and the small text says why.
- A card checks the **outcome** only. Two apps can both block a request for different reasons, so read the small text under each stamp.
- The page was tested against stand-in servers while this repo was built, not against your real Run A and Run B. Do a dry run first.
- Do not run the console from inside a run folder. Keep it in the main repo so the run folders stay free of demo files.

## The system in one minute

"An airline's flight is cancelled. Staff file compensation claims for passengers. Today there is no way to *decide* those claims. We want an approval process that an auditor will trust. The rules that matter (approval limits, no self-approval, no editing history, no private data in logs) are written down, but only for people, and AI tools, who read them."

## Talking points by D

- **Delegation:** "We decide what is ours before we open the chat. Business rules like approval limits are ours."
- **Description:** "Run B's prompt is longer, but not magic. It says what, how, and how to behave. And it points at information Run A did not have."
- **Discernment:** "In Run B we reviewed a *plan* before code existed. That is where mistakes are cheapest."
- **Diligence:** "We checked privacy, ran tests, disclosed AI use, and a person owns the merge."

## Facilitator tips

- **Do not oversell.** Run B usually does better, but not always, and not on every row. If Run A does well, congratulate it, then ask *"how would you have known?"* That is the lesson about Discernment.
- **Keep Run A honest.** No hints, no rescue. If it asks questions, say "use your best judgment".
- **Run A is not blind.** The code still carries a few inline comments about house rules (append-only tables, cents, passport handling), so a careful run can pick up on some of them. That is realistic. The approval limits, self-approval ban, rejection-reason rule, and what counts as a duplicate exist only in `docs/COMPENSATION_POLICY.md`, which Run A never sees.
- **Keep it plain.** For non-technical viewers, narrate in terms of the situations on the scorecard, not file names. For new grads, show the "Where to look" column afterwards.
- **If Claude Code stalls** in either run, switch to your dry-run folder and say so.
- **Keep the traps hidden** until after scoring. The "Common traps" list in the scorecard is for you.

## What the audience should say at the end

"The better result came from knowing what to delegate, describing it well, reviewing what came back, and owning the outcome. And I could do that with any tool."

## Files

| File | Use |
|---|---|
| `FEATURE_REQUEST.md` | The business request (Run B uses it) |
| `RUN_A_one_line_prompt.md` | Script for Run A |
| `RUN_B_4D_playbook.md` | Script and prompts for Run B |
| `SCORECARD.md` | Ten situations, scoring sheet, traps, debrief |
| `visual/` | Live side-by-side console: `console.py` and `index.html` |
| `CLOSER_non_coding_4D.md` | Non-coding exercise and pocket card |
| `prepare_runs.sh` | Creates clean `run-a-one-line` and `run-b-4d` folders |
