# Domain Context

Operating context for BSL Coach. Any future session should be able to reason about the system from this file without re-deriving the strategy.

---

## Client

Hudson Mac Cayman Holding Company. Sole user and decision-maker: Dave Holmes — trader, analyst, and executor for all positions. Adam Raposa (humbledtrader.com) appears in the data flow as an external source, not a user.

## Business Goal

Daily pre-market automation pipeline that turns Adam Raposa's Pre-Market Planning PDF into TradingView-ready Pine Scripts, risk-adjusted position sizes, and cleanly separated Active BSL vs Legacy Portfolio P&L, for a solo high-net-worth trader executing BSL setups.

## Key Terms

- **BSL** — the trading methodology taught by Adam Raposa (Humbled Trader). Intake records the expansion as "Buy-Support / Sell-Resistance"; see Q-008 on naming consistency. Discretionary setups at published Key Levels; never algorithmic signal generation.
- **PM Planning** — **Pre-Market** Planning. Adam's single daily brief (live call 8:30 AM ET, PDF ~8:45 AM ET). "PM" never means afternoon in this project.
- **KL (Key Level)** — a price level published in the PM Planning PDF: Entry KL, Target 1 (T1), Target 2 (T2). Adam publishes no stop losses; Dave sets stops himself.
- **Conviction tiers** — Dave's per-setup grade mapping to per-trade risk: Base 0.10% / Medium 0.15% / High 0.20% / Max 0.25% of NLV. "Pass" = no trade. Adam's "size up" flag maps to +1 tier only when Dave's own read agrees (two-vote rule — always human judgment, never automated).
- **NLV** — Net Liquidation Value of the live IBKR account (~$3.9M now; $10M+ expected after Dec 9 2026 SPCX lockup expiration).
- **Legacy Portfolio** — the 47 pre-existing positions (incl. multi-leg options structures). Tracked as MTM baseline only; not managed by this project's tools; not governed by the risk caps.
- **Active BSL** — trades opened on/after 2026-07-01 (D-001). The risk framework governs these only.
- **Staged order** — a bracket created via `create_order_instruction`, landing in IBKR Desktop's Review Instructions tab. Dave manually transmits every order (D-003).

## Business Rules — Risk Framework (established 2026-07-01)

Anchors: $5-10K/day P&L target; 10% max peak-to-trough drawdown.

- Per-trade risk by conviction: 0.10% / 0.15% / 0.20% / 0.25% of NLV.
- Hard cap: no single trade risks more than **$50,000**, regardless of tier or NLV.
- Concentration: no single position exceeds **5% of NLV** (counting any existing position in the same symbol).
- Loss caps (Active BSL ledger only — deferred to the ledger sprint, D-012): daily 1.0% → stop for the day; weekly 3.0% → halve next week's sizing; monthly 5.0% → stop a week and journal; 10% drawdown → full stop and reassess.
- At $4M: base $4K / med $6K / high $8K / max $10K risk per trade. At $10M: $10K / $15K / $20K / $25K.
- Not financial advice; a starter framework Dave iterates as live data accumulates.

## Current Workflow (pain)

8:30 call → ~8:45 PDF → 30-50 min of manual TradingView markup → manual stop selection → hand-calculated sizing under time pressure → manual bracket construction in IBKR Desktop → no Legacy/Active P&L separation, so loss caps can't fire on the right signal. Discord and Dave's own multi-day setups have no unified intake.

## Target Workflow (v1)

PDF → parser extracts tickers/KLs/conditional setups → Dave supplies conviction tier + stop per ticker → dated Pine Script (`bsl_pm_watchlist_YYYY-MM-DD.pine`) via `pbcopy` → sizing calculator returns exact share counts with cap checks → Dave stages brackets in IBKR Desktop and transmits manually → TUI dashboard (later sprint) shows positions, two-ledger P&L, risk budget usage. Non-PDF setups enter via structured paste.

## Execution stack

TradingView = chart/analysis layer (Pine indicator; no info tables duplicating dashboard data — see memory `dashboard-chart-no-overlap.md`). IBKR Desktop = execution layer (live account; staged brackets; Quick Trade buttons for scale-outs). IBKR MCP connector = account-data and staging path (Claude runtime only, D-014). IB Gateway installed as fallback. Multi-monitor: TV main screen, IBKR Desktop secondary, future TUI tertiary.

## Constraints

- Live account. Never auto-fire orders (D-003). Never propose trades or give buy/sell advice.
- Dave is an experienced trader running a hedged book — no beginner framing.
- No web framework, no database in v1 (SQLite optional in v2).
- MCP tools callable only from Claude sessions; standalone Python takes account data as inputs (D-014).
- Existing working code (`pm_pdf_to_pine.py` + dated Pine scripts, in daily use since 2026-06-16) lives outside this folder until its migration sprint.
