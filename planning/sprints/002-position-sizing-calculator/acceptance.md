# Sprint 002 Acceptance — Position Sizing Calculator

A sprint-complete claim requires every item below.

- **A-001** — `pytest` green with the full D-009 matrix implemented: every edge case listed in the blueprint has at least one test; the worked reference examples are encoded exactly.
- **A-002** — Worked example check: at NLV $4,000,000, base tier, NOW long 105.57/stop 104.59 returns 1,894 shares with concentration named as binding constraint (per blueprint math).
- **A-003** — Hard cap: max tier at NLV $30,000,000 sizes off $50,000 risk, hard cap named as binding.
- **A-004** — Direction safety: long with stop ≥ entry and short with stop ≤ entry both exit 2 with a clear message and no sizing output.
- **A-005** — No-viable-size path (FR-6) exits 3 with an explicit message; never prints 0 shares as a tradeable result.
- **A-006** — Offline path: a fully-flagged invocation with no snapshot file present succeeds with no network access.
- **A-007** — Snapshot path: fresh snapshot supplies NLV/existing-value; stale snapshot (> threshold) still computes but with a prominent warning naming the age; malformed snapshot exits 4.
- **A-008** — Out-of-scope guard: `create_order_instruction`, `ib_insync`, and `mcp__` appear nowhere in `src/` (grep check documented or scripted).
- **A-009** — `--json` output is valid JSON and semantically matches the human-readable output for the same inputs.
- **A-010** — README + `docs/SIZING_RECIPE.md`: Dave can install and run a first sizing in under 5 minutes; the conversational recipe documents the Claude-fetches-NLV flow end to end.
- **A-011** — Live smoke test (Dave drives): one real morning sizing against live NLV (via the conversational recipe or manual flags), result sanity-checked against hand math. Sign-off recorded in STATE.md.
