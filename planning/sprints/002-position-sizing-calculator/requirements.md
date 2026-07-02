# Sprint 002 Requirements — Position Sizing Calculator

## Why (business goal)

Position sizing is currently hand math under time pressure minutes before the open, against a live ~$3.9M account. A wrong size is the single most expensive mistake this project can prevent. This sprint ships a tested calculator that turns (symbol, direction, entry, stop, conviction tier, NLV, existing exposure) into an exact share count with every cap checked.

## What

A Python package `bsl_coach` in `src/` providing:

1. **Pure risk math** (`risk_math` module): tier → risk dollars, risk dollars + stop distance → share count, cap checks. No I/O, no network, no MCP. All money math in `Decimal`.
2. **CLI** (`bsl-size`): computes and prints a sizing result. Example invocation (final flag names are Builder's choice, semantics are not):

   `bsl-size NOW --direction long --entry 105.57 --stop 104.59 --tier base --nlv 3890000 --existing-value 0`

3. **Account snapshot file** (optional input): `data/account_snapshot.json` holding `{nlv, positions: {symbol: market_value}, as_of}` — written by a Claude session (via IBKR MCP) or by hand. When present and fresh, `--nlv`/`--existing-value` may be omitted. Stale snapshot (default > 1h) triggers a prominent warning, not silent use.
4. **Conversational recipe** (`docs/`): a short documented flow for Claude sessions — fetch NLV + positions via the IBKR MCP connector, refresh the snapshot file, run the CLI, relay the result. The Python never calls MCP itself (D-014).

## Functional requirements

- FR-1: Tier mapping per DOMAIN.md: base 0.10% / medium 0.15% / high 0.20% / max 0.25% of NLV.
- FR-2: Risk dollars = min(tier% × NLV, $50,000 hard cap). Output states when the hard cap binds.
- FR-3: Share count = floor(risk dollars ÷ per-share stop distance). Whole shares only, always rounded down.
- FR-4: Long: stop must be strictly below entry. Short: stop strictly above entry. Anything else (including equality) is a hard input error — non-zero exit, no numbers output.
- FR-5: Concentration check: (shares × entry) + existing same-symbol position value must not exceed 5% of NLV. When exceeded, reduce shares to the largest count that passes, and report both the capped and uncapped figures with the binding constraint named.
- FR-6: Zero computed shares (stop too tight × price too high for the risk budget) is a loud, explicit "no viable size" result — never silently output 0 as if tradeable.
- FR-7: Output (human-readable and `--json`): shares, position value, dollar risk, risk as % of NLV, concentration %, NLV used and its source/age, every check with pass/capped/fail, and the binding constraint.
- FR-8: Works completely offline via flags — no account connectivity required (R-006 fallback path).

## Out of scope (hard boundaries)

- Daily/weekly/monthly loss-budget checks and the Active-vs-Legacy ledger (D-012 — next sprint).
- Order staging / any `create_order_instruction` or MCP integration in Python code (D-013, D-014).
- PDF parser migration, Pine Script changes, TUI, alerts.
- Any auto-derivation of conviction tier — the tier is always Dave's input (two-vote rule is human).

## Rigor

D-009 applies in full: this is money-touching code. The acceptance test matrix is mandatory, not aspirational.
