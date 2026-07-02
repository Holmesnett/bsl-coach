# Sprint 003 Acceptance — Active BSL Ledger & Budget Checks

- **A-001** — `pytest` green; every blueprint edge case has ≥ 1 test; Sprint 002's 81 tests still pass untouched.
- **A-002** — Ground truth: the NOW fixture yields exactly one closed episode, realized +$458.61 (±$0.01), bucketed to ET 2026-07-01. If irreproducible, sprint stops per blueprint (no improvised P&L definition).
- **A-003** — Registry round trip: `bsl-size ... --register` (exit 0) appends an entry; `bsl-ledger list` shows it; `tag`/`untag` add and remove manual entries; sizing without `--register` never writes.
- **A-004** — ET bucketing: the 2026-07-02T01:30Z→ET-2026-07-01 rollover case and both DST boundary dates pass.
- **A-005** — Budget math at NLV $3,819,828.43 matches the blueprint's worked figures; warning fires at ≥ 75%, stand-down + exit 5 at ≥ 100%, profitable bucket = 0% usage; caps derive from snapshot NLV (test with two different NLVs).
- **A-006** — Review list: OPT fills in registered symbols, pre-registration fills, and unmatched activity appear for review and never enter episode P&L.
- **A-007** — Dedupe: overlapping snapshots (same fills pulled twice) produce identical ledger output.
- **A-008** — Guardrails extended: grep-clean for `create_order_instruction` / `ib_insync` / `mcp__` across all of `src/`; no blocking/enforcement code paths.
- **A-009** — `--json` report is valid JSON and semantically matches human output, warnings included.
- **A-010** — `docs/LEDGER_RECIPE.md` + README updates: the Claude-session flow (fetch trades → write snapshot → run `bsl-ledger`) documented end to end; a cold reader can run a report in 5 minutes.
- **A-011** — Live check (Dave drives): one real `bsl-ledger` run against a fresh trades snapshot; NOW trade appears correctly; totals sanity-checked against IBKR Desktop's own records. Sign-off recorded in CLOSEOUT and STATE.md.
