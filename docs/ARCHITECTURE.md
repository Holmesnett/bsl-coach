# Architecture — BSL Coach v1

## Shape

Local, file-based Python on macOS. No web framework, no database, no daemon. Three layers:

1. **Claude runtime (Cowork / Claude sessions)** — the only place MCP tools exist. Fetches live account data via the IBKR MCP connector, refreshes `data/account_snapshot.json`, invokes CLIs, relays results. Later sprints: stages orders via `create_order_instruction` (human-transmitted always, D-003).
2. **Pure Python (`src/bsl_coach/`)** — testable logic with zero network access (D-014). Sprint 002: `risk_math`, `snapshot`, `cli`. Later sprints add: parser (migrated `pm_pdf_to_pine.py`), ledger/tagging tracker, TUI dashboard.
3. **External surfaces** — TradingView (Pine scripts via `pbcopy`), IBKR Desktop (manual execution; Review Instructions tab for staged orders), iCloud (folder sync), GitHub (version control).

## Data flow (Sprint 002 slice)

PM PDF → (existing external parser) → Pine script → TradingView charts. In parallel: Claude fetches NLV + positions → snapshot file → `bsl-size` → share count + cap checks → Dave builds the bracket in IBKR Desktop manually.

## Key boundaries

- MCP-callable code and pure Python never mix (D-014). The snapshot file is the interface between them.
- The risk framework's constants live in one module, documented against `planning/DOMAIN.md`.
- Execution is always human (D-003). Nothing in this codebase transmits an order.

## Future (per roadmap, not yet authorized)

Sprint 003 (likely): Active-vs-Legacy ledger tracker off `get_account_trades` + D-001 cutoff → enables daily/weekly/monthly loss-budget checks. Then: parser migration with fixture tests; observability TUI (framework per Q-002); order staging integration.
