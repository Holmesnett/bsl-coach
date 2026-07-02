---
name: execution-stack
description: "Dave's BSL trading execution stack — TradingView for chart analysis, IBKR Desktop (live account) for order placement"
metadata:
  type: reference
  source: mirrored from Cowork local memory 2026-07-02 for cross-device handoff
---

Dave's split-layer trading workflow:

- **Chart layer:** TradingView. The BSL Coach Pine Script (`bsl_pm_watchlist.pine`) renders the day's Key Levels, conditional setups, VWAP, prior-day LOCH, and prime / avoid window shading per ticker. This is where setups are analyzed and where alerts fire.
- **Execution layer:** Interactive Brokers Desktop (the newer cross-platform IBKR client). **LIVE account with real capital**, not paper. Confirmed 2026-07-01. NLV was ~$3.89M with 47 positions including multi-leg options structures at time of confirmation — Dave runs a sophisticated, actively hedged book; do NOT assume beginner status or paper-money framing in advice. He is familiar with both TWS and IBKR Desktop but chose IBKR Desktop for daily execution because the cleaner UI reduces visual noise. He has TWS available as a fallback for any advanced order types IBKR Desktop doesn't expose. Earlier notes about "paper mode / reps phase" (DU9889832) are outdated — the paper account existed as a separate context but the AI connector was authorized against the LIVE account.
- **Why IBKR Desktop over TradingView orders:** familiarity + lower visual noise. Dave already knows the IBKR interface family; cleaner Desktop UI helps with rep quality.
- **Execution pattern:** Pre-built bracket orders (Entry + SL + T1/T2 OCO), staged via the "Save" button in the order ticket, then submitted manually after a setup confirms at the KL. Price alerts set at each Entry KL and conditional trigger to direct attention.
- **Multi-monitor setup:** TradingView on the main screen for chart analysis, IBKR Desktop on the secondary monitor for order management. Persistent Terminal UI dashboard (planned for a future sprint) will run on a tertiary window.
- **TV → IBKR API connection** exists but is currently unused for order routing.
- **IB Gateway:** already installed locally and Dave is very familiar with it. This is the historical path for any IBKR API automation via `ib_insync`. Ports: 4001 live, 4002 paper. HOWEVER — see updated `ibkr-claude-connector.md`; the IBKR MCP connector is now available in Cowork and may obviate the ib_insync path entirely.

**IBKR Desktop menu paths (confirmed from sitemap):**
- **Settings → Trading Presets** — bracket-order template config (default profit-target offset, default stop offset, default TIF).
- **Trade → Market Alerts** — centralized alert manager. Price alerts created via the MCP connector will appear here.
- **Preferences → Quick Trade** — one-click order buttons + quantity selector chips. Dave has already customized these (Shares: 10/25/50/100/200/500/1000/2000; Cash: 1k/2.5k/5k/7.5k/10k/15k/20k/25k). Useful for scale-outs and partial exits, NOT for bracket orders.
- **Order Ticket → Advanced dropdown** — exposes Profit Taker and Stop Loss fields for building bracket OCO orders manually.
- **Portfolio → AI Instructions** — where Claude-proposed orders land for Dave's review before he transmits them.

**How to apply:**
- When discussing trade execution, automation, or order workflow, assume Dave is placing orders in IBKR Desktop, not in TradingView. Do not suggest TradingView-based order placement features unless he asks.
- The TV ↔ IBKR API connection exists but is currently unused for order routing.
- Related context on dashboard/chart visual separation: see `dashboard-chart-no-overlap.md`.
- Related risk framework: see `risk-framework.md`.
