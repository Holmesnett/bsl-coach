# Architecture — BSL Coach v1

## Shape

Local, file-based Python on macOS. No web framework, no database, no daemon. Three layers:

1. **Claude runtime (Cowork / Claude sessions / scheduled tasks)** — the only place MCP tools exist. Fetches live account data via the IBKR MCP connector and refreshes the snapshot files; invokes CLIs; relays results; runs the premarket scan (7:45a ET) and EOD recap (4:15p ET) scheduled tasks that maintain journal files. Later sprints: stages orders via `create_order_instruction` (human-transmitted always, D-003).
2. **Pure Python (`src/bsl_coach/`)** — testable logic with zero network access (D-014). Sprint 002: `risk_math`, `snapshot`, `cli` (`bsl-size`). Sprint 003: `registry`, `trades`, `ledger`, `cli_ledger` (`bsl-ledger`). Sprint 004: `pm_parser`, `pine_gen`, `board_gen`, `cli_pm` (`bsl-pm`). Later: TUI dashboard (open question Q-002).
3. **External surfaces** — TradingView (generated Pine via `pbcopy` + paste over one saved indicator, D-005), IBKR Desktop (manual execution), iCloud (folder sync), GitHub (version control).

## Snapshot-file interface (D-014 / D-020)

Claude sessions write `data/account_snapshot.json` (`bsl-snapshot-1`) and
`data/trades_snapshot.json` (`bsl-trades-1`); git-ignored, versioned,
staleness-checked; CLI flags override.

## Data flow (morning)

PM PDF lands → `bsl-pm parse` (bsl-pmplan-1 JSON, PDF archived to
data/pdf_archive/) → `bsl-pm pine --copy` (dated Pine, pasted over the saved
"BSL PM Watchlist" TV indicator; alerts re-armed by hand) + `bsl-pm board`
(markdown into the day's journal). Sizing: Claude refreshes account snapshot →
`bsl-size` (+`--register` tags BSL trades, D-018). Ledger: Claude refreshes
trades snapshot → `bsl-ledger` (episodes, ET buckets D-021, budget usage —
warnings only). Journal/watchlist homework files in `journal/` are
human-curated; scheduled tasks update them from live data, `src/` never does.

## Key boundaries

- A trade is Active BSL iff registered (D-018). Risk anchors to NLV, never
  buying power (D-019). Execution always human (D-003); nothing transmits,
  blocks, or enforces.
- Parser tolerance: unknown watchlist bullet shapes surface in parse reports
  (`unparsed`), never silently dropped; corpus sweep tracks format drift.
- Chart layers carry no tabular/info panels (dashboard-chart-no-overlap).

## Future (not yet authorized)

Journaling automation (Q-011, Sprint 005 candidate); observability TUI
(Q-002); transcript parsing; premarket-BSL variant (paper-track first);
order-staging integration last (D-013).
