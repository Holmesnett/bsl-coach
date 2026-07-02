---
name: risk-framework
description: "Dave's active-trading risk rules — anchored to $5-10K/day P&L target and 10% max drawdown; separate ledgers for legacy portfolio vs active BSL trades"
metadata:
  type: reference
  source: mirrored from Cowork local memory 2026-07-02 for cross-device handoff
---

Dave's active-trading risk framework, established 2026-07-01. Anchored to:
- Target daily P&L: **$5,000 - $10,000**
- Max acceptable peak-to-trough drawdown: **10%** of account capital
- Current account: ~$4M NLV. Post Dec 9 2026 SPCX lockup: expected $10M+ NLV.

**Per-trade risk (as % of account capital):**
- Base conviction: 0.10%
- Medium conviction: 0.15%
- High conviction: 0.20%
- Max (Adam-flagged + Dave's own conviction agrees): 0.25%
- Hard cap: no single trade risks more than $50K regardless of tier, even at $10M+.

**Loss caps that trigger action:**
- Daily 1.0% → stop trading for the day (no revenge trades)
- Weekly 3.0% → reduce next week's sizing to 50% until equity curve re-establishes
- Monthly 5.0% → stop for a week, journal, articulate process changes before re-entering
- 10% drawdown → complete stop, reassess everything

**At $4M:** trade 4K base / 6K med / 8K high / 10K max. Daily cap 40K, weekly 120K, monthly 200K.
**At $10M:** trade 10K base / 15K med / 20K high / 25K max. Daily cap 100K, weekly 300K, monthly 500K.

**Concentration limits:**
- No single position >5% of capital
- No single-day sector concentration >2x base risk
- Never risk more than $50K on a single trade (hard cap)

**Adam's upsize guidance:** when Adam flags "size up more," that maps to jumping one conviction tier. Only jump when both Adam AND Dave's own read agree (two-vote requirement).

**Two-ledger separation (Alternative 1 chosen 2026-07-01):**
- Everything stays in one IBKR account (preserves combined Portfolio Margin)
- Legacy Portfolio P&L: mark-to-market of the 47 pre-existing positions
- Active BSL P&L: only from trades initiated on or after a cutoff date (proposed 2026-07-01, day of first tagged BSL trade $NOW)
- Daily/weekly/monthly caps apply to Active BSL only, not portfolio drift
- Tracker to be built off the IBKR MCP connector's `get_account_trades` — tag trades by open date; before cutoff = Legacy, on/after = Active BSL.

**How to apply:**
- Before placing any BSL bracket, verify shares × (entry - stop) is within the appropriate conviction tier for current account size.
- Before start of trading day, verify no unrealized loss on active book is already approaching daily cap.
- Not financial advice — this is a starter framework based on standard risk-of-ruin math (per-trade risk ≈ max_drawdown / 20-30). Iterate as real trade data accumulates.

Related: `execution-stack.md`
