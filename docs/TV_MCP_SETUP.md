# TradingView MCP Bridge — Setup Runbook (D-024)

Connects Cowork sessions to the locally running TradingView Desktop via
Chrome DevTools Protocol. Gives the Architect live chart reads (levels,
indicator values, quotes) and direct Pine injection — replaces the
pbcopy+paste transfer (D-005 stays as fallback). **Chart interaction only;
no order path exists through this tool (D-003 boundary unchanged —
execution lives in IBKR Desktop).**

- Repo: `https://github.com/tradesdontlie/tradingview-mcp` (MIT, 4.1k stars)
- **Pinned commit: `c34dfd5b76ff4ad8de2884d1567931cc90dd2428`** (reviewed 2026-07-06)
- Security review (2026-07-06, Architect): 2 runtime deps only
  (`@modelcontextprotocol/sdk`, `chrome-remote-interface`); CDP bound to
  127.0.0.1:9222; `child_process` confined to `tv_launch` (local TV
  start/stop); sole external endpoint `pine-facade.tradingview.com`
  (TradingView's own saved-scripts API, called in-page); proper input
  sanitization (`safeString` JSON-escapes all interpolated strings); no
  telemetry. Verdict: clean at pinned commit.
- TV trading panel is **not** broker-connected (confirmed 2026-07-06) —
  keep it that way while CDP is enabled (R-012).

## Install (per machine — MacBook Pro AND Mac Studio, like D-023 grants)

Run in Terminal:

```bash
node -v   # need 18+; if missing: brew install node
mkdir -p ~/tools && cd ~/tools
git clone https://github.com/tradesdontlie/tradingview-mcp.git
cd tradingview-mcp
git checkout c34dfd5b76ff4ad8de2884d1567931cc90dd2428
npm install
```

Deliberately OUTSIDE `~/Documents/Claude/Projects/bsl-coach` — node_modules
does not belong in an iCloud-synced git folder.

## Register with the Claude desktop app

Claude → Settings → Developer → Edit Config → add inside `mcpServers`:

```json
"tradingview": {
  "command": "node",
  "args": ["/Users/daveholmes/tools/tradingview-mcp/src/server.js"]
}
```

Save, then fully quit and restart the Claude app (this ends the running
Cowork session — update STATE.md first).

## Launch TradingView with CDP

```bash
~/tools/tradingview-mcp/scripts/launch_tv_debug_mac.sh
```

Note: the script **kills any running TradingView first** (~30s chart
outage). Verify: `curl -s http://localhost:9222/json/version` returns JSON.

A plain TradingView launch (Dock/Spotlight, no flag) runs with the debug
port CLOSED — that is the rollback and the default posture on days the
bridge isn't wanted.

## Verify (new Cowork session, BSL Coach project)

1. `tv_health_check` → connected.
2. With the day's layout open: `data_get_pine_lines` with
   `study_filter: "BSL PM Watchlist"` on the AAPL pane → must return
   exactly the sheet's levels (7/6: 308.26 / 313.40 / 317.40 / 307).
3. `chart_set_symbol` round-trip (switch away and back).
4. `pine_set_source` + `pine_smart_compile` of the daily watchlist script
   → replaces the manual paste-over.

All four pass = bridge is live-verified; record in STATE.md.

## Rollback

1. Relaunch TradingView without the flag (port closes).
2. Remove the `tradingview` block from the Claude config; restart Claude.
3. `rm -rf ~/tools/tradingview-mcp` if abandoning entirely.
4. Pine transfer reverts to pbcopy+paste (D-005).

## Standing rules

- Never enable CDP with a broker-connected TV panel (R-012).
- Updates to the repo are re-reviewed before `git pull` — stay pinned.
- If a TradingView Desktop update breaks the bridge (R-013), fall back to
  D-005 and re-pin TV's version; do not chase fixes mid-market.
