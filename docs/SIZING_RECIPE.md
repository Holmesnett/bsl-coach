# Sizing Recipe — Conversational Flow for Claude Sessions

How a Claude session (Cowork or claude.ai with the IBKR connector) sizes a
trade at ~9:25am. The Python never calls MCP itself (D-014); the Claude
runtime fetches live data, writes the snapshot file, runs the CLI, and
relays the result. Numbers only — the calculator never stages or transmits
orders (D-003, D-013).

## Prerequisites

- This repo at `~/Documents/Claude/Projects/bsl-coach` (or installed via
  `pip install -e .` so `bsl-size` is on PATH).
- IBKR MCP connector available in the Claude session.

## The flow

### 1. Fetch live account data (Claude, via MCP)

- `get_account_summary` → read **NetLiquidation** (NLV).
- `get_account_positions` → market value per symbol (only symbols relevant
  to today's setups matter; include any symbol you might size).

### 2. Refresh the snapshot file (Claude writes it)

Write `data/account_snapshot.json` in the repo root:

```json
{
  "schema": "bsl-snapshot-1",
  "as_of": "2026-07-01T13:25:00Z",
  "nlv": 3890000,
  "positions": {
    "NOW": 105570.00
  }
}
```

Rules:

- `as_of` must be the current UTC time in ISO8601 with `Z`. The CLI warns
  loudly when the snapshot is ≥ 60 minutes old (`--snapshot-max-age-minutes`
  to change).
- `nlv` and market values are plain JSON numbers (parsed as `Decimal`,
  never float).
- Never commit a real snapshot — `data/account_snapshot.json` is
  git-ignored.

### 3. Run the CLI

Dave supplies the setup (symbol, direction, entry, stop) and the conviction
tier — the tier is always Dave's call, never derived (two-vote rule is
human).

```bash
cd ~/Documents/Claude/Projects/bsl-coach
PYTHONPATH=src python3 -m bsl_coach.cli NOW \
  --direction long --entry 105.57 --stop 104.59 --tier base
```

With a fresh snapshot, `--nlv` and `--existing-value` come from the file.
Add `--json` for machine-readable output.

### 4. Relay the result

Report to Dave: shares, position value, dollar risk / % of NLV,
concentration %, and — critically — any `capped` check, the binding
constraint, and every warning verbatim (especially STALE SNAPSHOT and
NO VIABLE SIZE). Never round up the share count; never soften a warning.

## Offline / fallback path (no connector)

If the MCP connector is down (R-006), skip the snapshot and pass everything
by flags:

```bash
PYTHONPATH=src python3 -m bsl_coach.cli NOW \
  --direction long --entry 105.57 --stop 104.59 --tier base \
  --nlv 3890000 --existing-value 0
```

Dave reads NLV and any existing position value straight from IBKR Desktop.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Sized OK (including capped results) |
| 2 | Invalid input — no numbers produced |
| 3 | No viable size — do not trade this setup at this size |
| 4 | Snapshot missing/malformed when the snapshot was the selected source |
