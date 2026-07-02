---
name: dashboard-chart-no-overlap
description: "Dave prefers non-redundant info displays — if data is in the Terminal dashboard, don't also render it on TradingView charts as info tables"
metadata:
  type: feedback
  source: mirrored from Cowork local memory 2026-07-02 for cross-device handoff
---

When the BSL workflow includes both a Terminal/HTML dashboard (Python/rich/textual) and TradingView indicators, don't duplicate the same watchlist/KL data in both places. The chart should carry only visual context that benefits from price-axis anchoring (lines, zones, VWAP, session shading). Tabular/structured data — direction, R:R, notes, conditional triggers, percent moves — belongs in the dashboard layer only.

**Why:** Dave called this out after the smoke-test of the BSL PM Watchlist Pine Script on QQQ. The on-chart info table replicated dashboard data and read as visual noise. He flagged it as soon as he saw the table render.

**How to apply:** When building Pine Script indicators, HTML overlays, or other chart-level visualizations going forward, default any info-table or data-panel features to OFF (or omit them entirely). If a feature is purely informational and could live in the dashboard, default it off. Reserve chart real estate for visuals that require price-axis context.
