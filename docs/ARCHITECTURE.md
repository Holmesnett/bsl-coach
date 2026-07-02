# Architecture — BSL Coach v1

## Shape

Local, file-based Python on macOS. No web framework, no database, no daemon. Three layers:

1. **Claude runtime (Cowork / Claude sessions)** — the only place MCP tools exist. Fetches live account data via the IBKR MCP connector and refreshes the snapshot files; invokes CLIs; relays results. Later sprints: stages orders via `create_order_instruction` (human-transmitted always, D-003).
2. **Pure Python (`src/bsl_coach/`)** — testable logic with zero network access (D-014). Sprint 002: `risk_math`, `snapshot`, `cli` (`bsl-size`). Sprint 003: `registry`, `trades`, `ledger`, `cli_ledger` (`bsl-ledger`). Later: parser (migrated `pm_pdf_to_pine.py`), TUI dashboard.
3. **External surfaces** — TradingView (Pine via `pbcopy`), IBKR Desktop (manual execution; Review Instructions tab for future staged orders), iCloud (folder sync), GitHub (version control).

## Snapshot-file interface (D-014 / D-020)

MCP-callable code and pure Python never mix. Claude sessions write:

- `data/account_snapshot.json` (`bsl-snapshot-1`) — NLV + per-symbol market values (from `get_account_summary` / `get_account_positions`), plus optional `available_funds` for the informational D-019 margin line.
- `data/trades_snapshot.json` (`bsl-trades-1`) — raw fills (from `get_account_trades`); UTC fill times convert to ET at ingest (D-021).

Both are git-ignored, versioned-schema, staleness-checked. Explicit CLI flags always override. The BSL registry (`data/bsl_registry.json`, `bsl-registry-1`, D-018) is likewise git-ignored and written only by `bsl-size --register` / `bsl-ledger tag|untag`.

## Data flow

PM PDF → (external parser, pre-migration) → Pine script → TradingView. Sizing: Claude refreshes account snapshot → `bsl-size` → share count + cap checks (+ optional `--register` tags the trade as BSL, D-018). Ledger: Claude refreshes trades snapshot → `bsl-ledger` → episode P&L split Active-BSL vs everything-else, ET-bucketed (D-021), budget usage vs 1%/3%/5% caps — warnings only, never enforcement.

## Key boundaries

- A trade is Active BSL iff it's in the registry (D-018). Date-based tagging was falsified by real post-cutoff non-BSL activity on day one.
- Risk is anchored to NLV, never buying power; Portfolio Margin headroom appears as informational feasibility only (D-019).
- Execution is always human (D-003). Nothing in this codebase transmits, blocks, or enforces.
- The risk framework's constants live in one module, documented against `planning/DOMAIN.md`.

## Future (per roadmap, not yet authorized)

Parser migration with the 87-PDF fixture corpus; observability TUI (framework per Q-002); order-staging integration (write side of the connector, human-transmitted).
