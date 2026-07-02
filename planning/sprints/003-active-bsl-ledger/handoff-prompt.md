# Sprint 003 Builder Handoff — Active BSL Ledger & Budget Checks

You are the Builder for BSL Coach Sprint 003. Read, in order: `AGENTS.md`,
`planning/STATE.md`, `planning/DECISIONS.md` (D-018..D-021 govern this sprint),
`planning/DOMAIN.md`, then all four files in
`planning/sprints/003-active-bsl-ledger/`. Implement from the sprint files only.

Build the BSL trade registry, trades-snapshot ingest, episode ledger with ET
bucketing, budget checks, and the `bsl-ledger` CLI exactly as specified.

Hard rules:

- Money-touching code (P&L aggregation, budget math) — the D-009 test matrix in
  the blueprint is mandatory. `Decimal` throughout; fills may have fractional sizes.
- The NOW ground-truth fixture gates everything: if you cannot reproduce
  +$458.61 from the real fills using IBKR's `realized_pnl`, STOP, document the
  discrepancy in CLOSEOUT.md and a decision row — do not invent a P&L definition.
- NO MCP calls, NO network, NO order code, NO blocking/enforcement behavior,
  NO auto-tagging heuristics, NO unrealized P&L in cap math.
- All day/week/month logic in America/New_York via `zoneinfo`; fills arrive UTC.
- Do not modify Sprint 002 behavior except adding `--register`; its 81 tests must
  still pass.
- Do not touch `planning/memory/`, `references/`, or the external parser.

Definition of done: A-001..A-010 verified by you with commands documented in a
CLOSEOUT.md; A-011 flagged as awaiting Dave. Then update `planning/STATE.md`,
`planning/FILE_INVENTORY.md`, `docs/ARCHITECTURE.md`, `docs/VALIDATION.md`,
record new decisions with the next D-number (D-022 onward), commit and push.
