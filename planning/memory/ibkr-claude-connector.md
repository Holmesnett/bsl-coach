---
name: ibkr-claude-connector
description: IBKR Claude connector status and how the MCP tools are used in this project
metadata:
  type: reference
  source: mirrored from Cowork local memory 2026-07-02 for cross-device handoff, with 2026-07-01 status update
---

## IMPORTANT — status update as of 2026-07-01

The IBKR MCP connector **IS available in Cowork** as of 2026-07-01 — confirmed live and used successfully in the outgoing Architect session. Older versions of this memory (dated 2026-06-17) said it was NOT available in Cowork; that was true at the time but is now superseded.

Tools discoverable via `ToolSearch` with server prefix `mcp__e6eff5f8-fb46-4232-8801-605c334177f8__`:

- `get_account_summary` — NLV, buying power, available funds, margin
- `get_account_positions` — all open positions with cost basis, market value, unrealized P&L
- `get_account_orders` — live/pending orders including bracket structures
- `get_account_trades` — trade history with fills (for tag-based Active BSL vs Legacy P&L split)
- `get_price_snapshot` — real-time bid/ask/last/volume/change/high/low/prior_close per contract
- `get_price_history` — historical OHLCV bars
- `search_contracts` — resolve ticker → contract_id (required by most price/option tools)
- `create_order_instruction` — stage a bracket order for Dave to review and manually transmit in IBKR Desktop's Review Instructions tab (never auto-fired)
- `delete_order_instruction`, `get_order_instructions` — manage the staged-order queue
- `get_option_data`, `get_option_parameters`, `search_futures`, `get_company_themes`, `get_pa_performance_all_periods`, etc.

## How it fits the project architecture

- The IBKR MCP connector supersedes the original Phase 3 plan of using `ib_insync` over IB Gateway. Gateway remains installed as a fallback path if the connector ever goes down, but is not the primary integration point in v1.
- The connector is **read-write** but the write side (`create_order_instruction`) is human-in-the-loop by design — orders land in IBKR Desktop's "Review Instructions" tab, and Dave manually clicks to transmit each one. Nothing is auto-fired.
- The connector is authorized against Dave's **live** IBKR account, not the paper account (DU9889832) mentioned in older documentation. Treat every query and instruction accordingly.

## How to apply

- When Dave asks "what am I holding" / "check my orders" / "pull today's P&L" — use `get_account_positions`, `get_account_orders`, `get_account_summary`. These are read-only, no confirmation needed.
- When Dave asks to stage an order — use `create_order_instruction` and confirm the exact bracket parameters (entry price, stop, target, share count) with Dave before firing. Do not autonomously propose orders — wait for Dave to specify.
- Never propose trades autonomously on this live account. If asked for analysis, provide observations and math, but don't recommend "take this trade" or "cut this position."

Related: `execution-stack.md`, `risk-framework.md`
