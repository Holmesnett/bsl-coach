# Sprint 002 Blueprint — Position Sizing Calculator

## Package layout

```
src/bsl_coach/
  __init__.py          # __version__
  risk_math.py         # pure functions + SizingResult dataclass (Decimal throughout)
  snapshot.py          # read/validate data/account_snapshot.json, staleness check
  cli.py               # argparse entrypoint `bsl-size`
tests/
  test_risk_math.py    # the D-009 matrix (bulk of the sprint's test weight)
  test_snapshot.py     # missing/stale/malformed snapshot handling
  test_cli.py          # flag parsing, exit codes, --json shape, offline path
samples/
  account_snapshot.example.json
pyproject.toml         # package metadata + bsl-size entry point
README.md              # extend scaffold README: install, usage, conversational recipe pointer
docs/SIZING_RECIPE.md  # conversational flow for Claude sessions (MCP fetch → snapshot → CLI)
```

## Design rules

- `risk_math.py` is pure: `(direction, entry, stop, tier, nlv, existing_value) → SizingResult`. Raises typed exceptions (`InvalidStopError`, `InvalidInputError`) on bad input. No prints, no file access.
- All prices/values parsed to `Decimal` at the boundary; floats never touch money math. Share count is `int`.
- `SizingResult` carries: `shares`, `position_value`, `risk_dollars`, `risk_pct_of_nlv`, `concentration_pct`, `checks` (per-check status: pass / capped / fail), `binding_constraint`, `warnings`.
- Tier table and caps (50_000 hard cap, 5% concentration, tier percentages) live as named constants in one place with a comment pointing at DOMAIN.md.
- Precedence when constraints collide: hard cap trims risk dollars first (FR-2), then concentration trims shares (FR-5). The tighter result always wins; `binding_constraint` names it.
- CLI exit codes: 0 = sized OK (including capped), 2 = invalid input, 3 = no viable size, 4 = snapshot problem when snapshot was the selected source.
- Snapshot schema: `{"schema": "bsl-snapshot-1", "as_of": "<UTC ISO8601 Z>", "nlv": <number>, "positions": {"SYM": <market_value>}}`. Versioned for future migration.
- Explicit flags always override snapshot values; the output must say which source supplied NLV.

## Worked reference examples (encode these as tests)

At NLV $4,000,000:

- Base tier → risk $4,000. NOW long, entry 105.57, stop 104.59 (distance 0.98) → floor(4000/0.98) = 4,081 shares; position value $430,832 ≈ 10.8% of NLV → concentration caps shares to floor(200,000/105.57) = 1,894 shares (binding constraint: concentration).
- Max tier at NLV $30,000,000 → tier risk $75,000 → hard cap trims to $50,000 (binding constraint: hard cap).
- Long with stop ≥ entry → `InvalidStopError`, exit 2.
- Risk $4,000, stop distance $0.005 on a $1,400 stock → shares floor fine; risk $4,000, entry $1,400, stop distance $800 → floor(4000/800) = 5 shares — verify no float wobble at boundaries (use cases like distance 0.98 vs 0.9800000001).
- Existing NOW position value $150,000 at 5% cap $200,000 → only $50,000 of new position value allowed.

## Edge cases the test matrix must cover (D-009)

Zero stop distance; negative distance (stop crosses entry, both directions); equality; zero/negative/absent NLV; zero computed shares (FR-6); floor boundaries (risk exactly divisible vs off-by-a-penny); hard cap exactly at tier boundary; concentration exactly at 5%; existing position alone already ≥ 5%; penny-priced symbol vs $1,400 symbol; `--json` output parses and matches human output; stale snapshot warning fires at threshold; malformed snapshot fails loudly.

## What the Builder must NOT do

No MCP calls, no `ib_insync`, no network I/O anywhere in `src/`. No order construction. No loss-budget math. No tier auto-suggestion. No TUI. Grep-able guard: the strings `create_order_instruction`, `ib_insync`, and `mcp__` must not appear in `src/`.
