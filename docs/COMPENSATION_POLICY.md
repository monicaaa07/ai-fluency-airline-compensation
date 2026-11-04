# Compensation Policy

Business rules owned by Customer Operations. The code must follow these; if code and
policy disagree, the policy wins and the discrepancy gets raised.

## Approval tiers

A claim must be decided by someone whose role covers the claim amount:

| Claim amount | Who may decide it |
|---|---|
| Up to and including $200.00 (20,000 cents) | Agent, Supervisor, or Manager |
| Over $200.00, up to and including $1,000.00 (100,000 cents) | Supervisor or Manager |
| Over $1,000.00 | Manager only |

A higher role can always decide a lower-tier claim.

## Separation of duties

- **Nobody decides a claim they filed themselves**, whatever their role.

## Decisions

- Every claim starts as **filed** and waits for a decision.
- A decision is **approved** or **rejected**.
- **A rejection must include a written reason** (at least 10 characters). An approval may include a note.
- Decisions are **final** in this release. Reversal is out of scope; mistakes are handled by a manager filing a new claim.
- Only **filed** claims can be cancelled (by the filer or a supervisor). Decided claims cannot be cancelled.

## One claim per passenger per incident

A passenger can be compensated once per incident.

- **Filed** and **approved** claims use up the passenger's claim.
- **Rejected** and **cancelled** claims do not; the passenger may be claimed for again.

## Audit requirements

Compliance must be able to answer "who decided what, when, and on what basis" for any claim, for 7 years.

For every decision (and every status change) the record must show:

- the claim, who acted (staff id and role at that time), and when (UTC)
- the status before and after
- the claim amount at that moment, in cents
- the reason or note given

Rules for the audit record:

- It is **append-only**; nothing is edited or deleted, and corrections are new entries (ADR 0003).
- It never contains passport numbers or other passenger PII (ADR 0004).
- Supervisors and managers may read a claim's audit history; agents may not.
