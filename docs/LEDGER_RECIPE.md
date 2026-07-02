# Ledger Recipe — Conversational Flow for Claude Sessions

How a Claude session (Cowork or claude.ai with the IBKR connector) produces
an Active BSL P&L report. The Python never calls MCP itself (D-014); the
Claude runtime fetches live data, writes the snapshot files, runs
`bsl-ledger`, and relays the result. **Informational only — the ledger
warns, it never blocks or enforces anything (D-003).**

## Prerequisites

- This repo at `~/Documents/Claude/Projects/bsl-coach` (or installed via
  `pip install -e .` so `bsl-ledger` is on PATH).
- IBKR MCP connector available in the Claude session.
- At least one registered trade — a trade is Active BSL **iff** it is in
  the registry (D-018). Register at sizing time (`bsl-size ... --register`)
  or manually (`bsl-ledger tag SYMBOL --date YYYY-MM-DD`).

## The flow

### 1. Fetch live data (Claude, via MCP)

- `get_account_trades` (period `DAYS_30` covers a full month bucket) → raw
  fills.
- `get_account_summary` → **NetLiquidation** (caps derive from NLV, never
  buying power, D-019) and, if available, **AvailableFunds** for the
  informational margin line.
- `get_account_positions` → market values (open-position info lines).

### 2. Write the snapshot files (Claude writes them)

`data/trades_snapshot.json` — the raw fills exactly as the connector
returned them (unknown fields are fine; they are ignored):

```json
{ "schema": "bsl-trades-1", "as_of": "2026-07-02T01:30:00Z",
  "period": "DAYS_30", "trades": [ /* raw fill objects */ ] }
```

`data/account_snapshot.json` — same file the sizing flow uses, plus the
optional `available_funds`:

```json
{ "schema": "bsl-snapshot-1", "as_of": "2026-07-02T01:30:00Z",
  "nlv": 3819828.43, "positions": {"NOW": 106040.00},
  "available_funds": 2100000 }
```

Rules:

- `as_of` = current UTC time, ISO8601 with `Z`. Snapshots ≥ 60 minutes old
  warn loudly (`--snapshot-max-age-minutes` to change).
- Fill `trade_time` values are UTC; the ledger converts to
  America/New_York at ingest (D-021) — a fill at `2026-07-02T01:30Z`
  belongs to ET trading day 2026-07-01.
- Overlapping pulls are safe: duplicate `trade_id`s dedupe.
- Never commit real data — both files (and `data/bsl_registry.json`) are
  git-ignored.

### 3. Run the report

```bash
cd ~/Documents/Claude/Projects/bsl-coach
PYTHONPATH=src python3 -m bsl_coach.cli_ledger report
```

(or just `bsl-ledger` if installed). Add `--json` for machine-readable
output. `--nlv` overrides the account snapshot; `--today YYYY-MM-DD`
overrides the report's ET day (default: the ET date of the trades
snapshot's `as_of`).

### 4. Relay the result

Report to Dave: TODAY / WTD / MTD realized P&L vs caps with usage %,
every closed episode line, open registered positions (unrealized is info
only — it never counts toward caps), the review list (anything that did
not match a registered setup), and **every warning verbatim** — especially
WARNING ≥ 75% and STAND DOWN ≥ 100% with the prescribed action
(daily → stop for the day; weekly → halve next week's sizing;
monthly → stop a week and journal). Never soften a stand-down message.

## Registry maintenance

```bash
bsl-ledger list                              # show the registry
bsl-ledger tag NOW --date 2026-07-01         # manual tag (ET date)
bsl-ledger untag 2026-07-01-NOW-1            # remove an entry
bsl-size NOW --direction long --entry 105.57 \
  --stop 104.59 --tier base --register       # register at sizing time
```

Matching rule (FR-4): STK fills in a registered symbol whose ET date is on
or after the registration ET date. OPT fills and pre-registration fills go
to the review list — tag or ignore them explicitly, never auto-classified.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Report OK (including warnings) |
| 4 | Snapshot/registry missing or malformed, or invalid NLV |
| 5 | A loss cap is at ≥ 100% — stand-down state (report still prints) |
