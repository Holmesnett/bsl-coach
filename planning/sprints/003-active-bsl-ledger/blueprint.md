# Sprint 003 Blueprint — Active BSL Ledger & Budget Checks

## Layout

```
src/bsl_coach/
  registry.py         # bsl_registry.json read/write, entry model, tag/untag
  trades.py           # trades_snapshot.json ingest, fill model, dedupe, UTC->ET
  ledger.py           # episode builder, P&L attribution, ET buckets, budget math
  cli_ledger.py       # `bsl-ledger` entrypoint (report / tag / untag / list)
  cli.py              # + `--register` flag on bsl-size (writes via registry.py)
tests/
  test_registry.py
  test_trades.py      # ingest, dedupe, UTC->ET conversion incl. 20:00 ET rollover
  test_ledger.py      # episodes, buckets, budgets — the D-009 matrix
  test_cli_ledger.py
  fixtures/
    now_2026_07_01_fills.json   # sanitized real NOW fills (ground truth +$458.61)
samples/
  trades_snapshot.example.json
  bsl_registry.example.json
docs/LEDGER_RECIPE.md # Claude-session flow: fetch trades -> snapshot -> bsl-ledger
```

## Schemas

`data/bsl_registry.json`:
```json
{ "schema": "bsl-registry-1",
  "entries": [ { "id": "2026-07-01-NOW-1", "symbol": "NOW", "direction": "long",
    "registered_at": "2026-07-01T14:55:00Z", "entry": 105.57, "stop": 104.59,
    "tier": "base", "shares_sized": 1602, "status": "active", "note": "" } ] }
```

`data/trades_snapshot.json`:
```json
{ "schema": "bsl-trades-1", "as_of": "<UTC ISO Z>", "period": "DAYS_30",
  "trades": [ /* raw fill objects exactly as get_account_trades returns them */ ] }
```

Observed fill fields (probed live 2026-07-01 — build the parser against these):
`trade_id`, `symbol`, `sec_type` (STK/OPT), `side` (BUY/SELL), `size` (may be
fractional — Decimal), `price`, `trade_time` (UTC ISO Z), `commission`,
`net_amount`, `realized_pnl`, `order_id`. Unknown extra fields must be ignored,
not fatal.

## Ground truth fixture (mandatory)

The NOW 2026-07-01 trade, from real fills: 8 BUY fills totaling 1000 shares
(~$105.567 avg, 14:59:38Z) and 7 SELL fills totaling 1000 shares @ 106.04
(18:55Z), per-fill `realized_pnl` summing to **+$458.61** (one small negative
fill −0.536385 included). `tests/fixtures/now_2026_07_01_fills.json` encodes
these fills (values preserved; ids may be sanitized). The ledger must produce:
one episode, closed, realized +$458.61 (±$0.01), bucketed to ET 2026-07-01.
**If IBKR's `realized_pnl` semantics make this unreproducible, stop and record
the discrepancy in CLOSEOUT + a decision — do not improvise an alternative
P&L definition.**

## Budget math (encode as tests)

At NLV $3,819,828.43: daily cap $38,198.28, weekly $114,594.85, monthly
$190,991.42. Bucket P&L −$30,000 → daily usage 78.5% (warning ≥ 75%);
−$38,198.28 → 100% → stand-down message + exit 5. Bucket P&L +$458.61 →
usage 0%. Caps recompute from snapshot NLV every run — never hardcode dollars.

## Edge cases the test matrix must cover (D-009)

UTC→ET: fill at 2026-07-02T01:30:00Z belongs to ET 2026-07-01 (the exact
rollover observed tonight); DST boundary dates (Mar/Nov). Episodes: multi-fill
entries and exits (the NOW shape); partial exit spanning two ET days (P&L
splits by closing-fill date); re-entry same day = second episode; fills in a
registered symbol before its registration date → review list, not episode;
short episodes (SELL first). Data: duplicate `trade_id` dedupe; fractional
sizes; missing/zero `realized_pnl` on entry fills; unknown fields ignored;
malformed snapshot exit 4; stale snapshot warning at threshold. Budgets: usage
exactly at 75% and 100%; profitable bucket = 0%; week (Mon ET) and month
boundaries; zero/absent NLV guard (exit 4, never divide-by-zero).

## Report sketch (human output)

Header: as-of, NLV + source/age, margin info line (available funds, informational
only per D-019). Sections: TODAY / WTD / MTD — realized P&L, cap, usage %, status
(OK / WARNING ≥75% / STAND DOWN ≥100% with the framework's prescribed action
text from DOMAIN.md). Then: open registered positions (unrealized as info),
closed episodes (per-trade lines), review list (unmatched fills in registered
symbols, OPT fills, fills before registration). Every warning verbatim in
`--json` too.

## What the Builder must NOT do

No MCP calls, no network, no order code (extend `tests/test_guardrails.py` to
cover the new modules). No auto-tagging heuristics. No blocking behavior. No
unrealized P&L in cap math. No new runtime dependencies beyond stdlib without
documented justification (`zoneinfo` is stdlib — use it).
