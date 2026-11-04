# Run B: the same feature, using the 4Ds

**Goal:** show that the difference is not a magic prompt. It is four habits you can use with any AI tool.

## Setup
Run `demo/prepare_runs.sh <folder>` and open `<folder>/run-b-4d` in Claude Code. This copy has the
code plus `CLAUDE.md` and `docs/` (architecture, policy, decision records).

Walk the audience through the stages in order. Each stage names the D it practices.

---

## Stage 1: Delegation (before you type anything)

Decide who does what. Fill this in **with the audience** on a whiteboard first.

| Task | Claude | Human | Why |
|---|---|---|---|
| Understand the existing codebase and its rules | Yes | Skim | Fast, tireless reading |
| Propose the design and a build plan | Yes | **Reviews** | Claude drafts; you judge |
| Decide approval limits and who may approve | | **Yes** | A business decision. Already written in `COMPENSATION_POLICY.md` |
| Decide whether decisions can be reversed | | **Yes** | Business call. Claude must ask, not guess |
| Write migration, service, API, tests | Yes | Reviews | Mechanical once the design is right |
| Check it against the real-world scenarios | Helps | **Yes** | You own "is this right?" |
| Merge and tell people AI was involved | | **Yes** | Accountability |

*Say out loud:* "Problem awareness: we know what done looks like. Platform awareness: Claude Code can read the repo, edit files and run tests, but it cannot know our policies unless we give them to it."

---

## Stage 2: Description (Product, Process, Performance)

Paste this. Replace the bracketed part with the contents of `demo/FEATURE_REQUEST.md`.

```
I want to add an approval workflow with an audit trail to this service.

PRODUCT: what I want
[paste the contents of demo/FEATURE_REQUEST.md]

PROCESS: how I want you to work
1. First read CLAUDE.md, docs/ARCHITECTURE.md, every file in docs/adr/, and docs/COMPENSATION_POLICY.md.
2. Do not write code yet. Give me a plan: files to add or change, by layer; the migration; how each decision record and policy rule will be honored; and which existing patterns you will reuse.
3. List anything you are unsure about, and anywhere my request and the documents seem to conflict.
4. After I approve the plan, build in small steps (migration, domain, repository, service, API, tests) and run the tests after each step.

PERFORMANCE: how I want you to behave
- Be concise. Explain in plain language, as if to a smart non-expert.
- If something is ambiguous or conflicts with a documented rule, stop and ask me instead of guessing.
- Push back if I ask for something that would break a decision record.
- At the end, tell me what you assumed and what you did not verify.
```

*Say out loud:* "Product is what. Process is how. Performance is how Claude should behave with me: ask, push back, be honest about limits."

---

## Stage 3: Discernment on the plan (before any code)

Read Claude's plan **as a reviewer**. Do not accept it yet. Use these questions, spoken or typed:

- "Which policy rules does this plan not cover?"
- "How will a claim's status and its history stay consistent if something fails halfway?"
- "A passenger's claim is approved. Can staff then file another claim for the same passenger and incident? Show me where that is blocked."
- "What is the riskiest assumption in this plan?"
- "Where would passport numbers or other private data appear in this design?"

Facilitator note: these probe the common traps (see `SCORECARD.md`) without revealing them. If Claude's plan already handles one, say so. If it misses one, let the audience spot it, then ask Claude to revise the plan. **This loop (Discernment feeding back into Description) is the lesson.**

Approve the plan only when you would be comfortable defending it.

---

## Stage 4: Build in small steps, with Discernment on the product

Tell Claude: "Approved. Go." Then, after it finishes, ask it to **prove** the result in plain terms:

```
Show me, with a test for each, how the system handles these situations, and list the test names:
1. An agent approves a $150 claim filed by another agent.
2. An agent tries to approve a $600 claim.
3. A supervisor tries to approve a $1,500 claim.
4. Someone approves a claim they filed themselves.
5. A rejection with no reason.
6. After a claim is approved, someone files another claim for the same passenger and incident.
7. Someone tries to edit or delete a history entry.
```

Then check for yourself, because Claude's own summary is not proof:

- Run `pytest`.
- Search the new code for the passport field name. It should not appear in logs, history rows, or errors.
- Ask: "Does any new code UPDATE or DELETE the history table? Show me."
- Ask: "Did you edit an existing migration?"

---

## Stage 5: Diligence

- **Verify:** all tests green, and you personally read the history table's migration and the approval service method.
- **Privacy:** confirm no passport numbers in logs, history, or error bodies (ADR 0004).
- **Transparency:** ask Claude to draft the pull-request description, then add this line yourself:

  > *AI assistance: designed and implemented with Claude Code under the 4D process (plan reviewed and approved by a human; scenarios verified by a human). Reviewer: <name>.*

- **Accountability:** the human merges. If it breaks an audit rule in production, "the AI wrote it" is not an answer.

*Say out loud:* "Diligence is not paperwork. It is deciding in advance that you will own the result."

---

## After the run
Save the folder untouched and score both runs with `SCORECARD.md`.
