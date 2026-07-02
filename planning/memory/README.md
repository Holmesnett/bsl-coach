# Memory files (mirrored from Cowork local memory)

These files are point-in-time context notes that were built up in the outgoing Architect's local Cowork memory system on Dave's MacBook Pro. They are mirrored here into the project folder so that:

1. A fresh Architect session on any device (Mac Studio, Fable 5 primary, whatever) can read them at session start rather than starting from a blank slate.
2. They survive a Cowork session switch that would otherwise leave them stranded on one machine.

**They are reference, not doctrine.** If a claim here conflicts with something in `ARCHITECT_BRIEFING.md` or with the planning files, the planning files win.

## Contents

- `execution-stack.md` — Dave's trading stack: TradingView for charts, IBKR Desktop (live account) for orders, IB Gateway available. Includes IBKR Desktop menu paths.
- `risk-framework.md` — Per-trade sizing tiers (0.10-0.25%), daily/weekly/monthly loss caps, concentration limits, two-ledger split logic.
- `ibkr-claude-connector.md` — Current status of the IBKR MCP connector in Cowork (available as of 2026-07-01), which tools it exposes, and how the project uses them.
- `dashboard-chart-no-overlap.md` — Dave's preference not to duplicate tabular data on chart layer if it's already in the dashboard layer.

## Source

These were saved by Claude Opus 4.7 in Cowork across sessions spanning 2026-05-25 through 2026-07-01, during the intake and framework-building phase of the BSL Coach project. Some memory files carry a "point-in-time" caveat — verify anything specific against current tool behavior before treating as fact.
