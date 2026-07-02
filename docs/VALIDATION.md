# Validation — BSL Coach

## Rigor model (D-009)

Micro-app rigor everywhere except money-touching code. Money-touching = anything computing position sizes, stop distances, risk dollars, cap checks, budget consumption, or NLV math. That code gets a mandatory test matrix: happy paths AND edge cases (zero/negative stop distance, entry crossing stop, share-count floor boundaries, hard-cap and concentration boundaries, absent/stale account data). Non-money code (CLI plumbing, file handling, docs) gets happy-path plus the failure modes that would lose data.

## Sprint 002 validation

- `python3 -m pytest` — full suite green is the gate.
- Money math in `Decimal`; tests include float-wobble boundary cases.
- Out-of-scope guard: grep `src/` for `create_order_instruction`, `ib_insync`, `mcp__` — zero hits.
- A-011 live smoke test: Dave runs one real-morning sizing and checks it against hand math before the calculator is trusted in the daily workflow.

## Standing rules

- A failing or missing test on money math blocks sprint completion — no exceptions.
- Every acceptance item maps to a command or a documented manual check.
- Validation behavior changes get recorded here at each sprint boundary.
