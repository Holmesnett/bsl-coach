# Sprint 002 Builder Handoff — Position Sizing Calculator

You are the Builder for BSL Coach Sprint 002. Read, in order: `AGENTS.md`, `planning/STATE.md`, `planning/DECISIONS.md`, `planning/DOMAIN.md`, then all four files in `planning/sprints/002-position-sizing-calculator/`. Implement from the sprint files only.

Build the position sizing calculator exactly as specified: pure `risk_math` core (Decimal money math), `bsl-size` CLI, optional snapshot-file input, pytest matrix per the blueprint's edge-case list.

Hard rules:

- This code informs live-money decisions on a ~$3.9M account. The blueprint's test matrix is mandatory (D-009). Do not ship untested money math.
- NO MCP calls, NO `ib_insync`, NO network I/O in `src/`. Account data arrives via CLI flags or the snapshot file (D-014).
- NO order staging or order construction of any kind (D-013).
- NO loss-budget / ledger logic (D-012 — next sprint).
- Never auto-derive the conviction tier; it is always an input.
- Prefer boring, local, file-based Python. No new dependencies beyond stdlib + pytest unless you document why.
- Do not touch `planning/memory/`, `references/`, or the parser living outside this folder.

Definition of done: acceptance A-001 through A-010 verified by you with commands documented; A-011 (live smoke test) is Dave's, flagged as awaiting sign-off. Then update `planning/STATE.md`, `planning/FILE_INVENTORY.md`, and record any new decisions in `planning/DECISIONS.md` with the next D-number, plus `docs/ARCHITECTURE.md` if the shape changed.
