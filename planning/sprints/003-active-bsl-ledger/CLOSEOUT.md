# Sprint 003 Closeout — Active BSL Ledger & Budget Checks

**Builder:** Fable 5 (Claude Code)
**Date:** 2026-07-01
**Status:** Built and verified A-001..A-010. **A-011 (live check) awaiting Dave's sign-off.**

---

## What shipped

- `src/bsl_coach/` — `registry.py` (bsl-registry-1 load/save/tag/untag, D-018),
  `trades.py` (bsl-trades-1 ingest, UTC→ET at ingest per D-021, dedupe,
  staleness), `ledger.py` (FR-4 matching, FR-5 episodes, FR-6 ET buckets,
  FR-7 budgets — money-touching, D-009), `cli_ledger.py` (`bsl-ledger`
  report/tag/untag/list, exit codes 0/4/5).
- `cli.py` gained `--register`/`--registry` (only permitted Sprint 002
  change); `snapshot.py` gained optional `available_funds` (additive).
- `tests/` — 121 new tests across `test_registry.py`, `test_trades.py`,
  `test_ledger.py` (D-009 matrix), `test_cli_ledger.py`; guardrail scan
  extended to the new modules. **Total 202.**
- `tests/fixtures/now_2026_07_01_fills.json` — ground-truth NOW fixture
  (R-011 gate).
- `samples/trades_snapshot.example.json`, `samples/bsl_registry.example.json`,
  `docs/LEDGER_RECIPE.md`, README Quick Start (ledger section), `.gitignore`
  additions (`data/trades_snapshot.json`, `data/bsl_registry.json`),
  `bsl-ledger` entry point in `pyproject.toml`.

## Ground-truth fixture provenance (A-002 / R-011)

The architect pack contains no raw per-fill table, so the fixture was
**constructed** to satisfy every documented aggregate exactly (blueprint:
"values preserved; ids may be sanitized"): 8 BUY fills totalling 1,000
shares at cost exactly $105,567.00 (avg exactly 105.567, ET
2026-07-01 morning), 7 SELL fills totalling 1,000 shares @ 106.04 whose
per-fill `realized_pnl` sums to **exactly +$458.61** (including a
−0.536385 residual fill). Edge cases baked in: one fill missing
`realized_pnl` (→ 0), one fill carrying an unknown field, `as_of`
2026-07-02T01:30Z rolling back to ET day 2026-07-01. IBKR's per-fill
`realized_pnl` remains authoritative — no P&L definition was invented.

## Acceptance verification (commands run 2026-07-01, all from repo root)

| Item | Command | Result |
|---|---|---|
| A-001 | `PYTHONPATH=src python3 -m pytest -q` | **202 passed**; Sprint 002 subset (`test_risk_math.py test_snapshot.py test_cli.py`) **79 passed** with `git diff --stat` empty (untouched); + 2 original guardrail tests still green |
| A-002 | `bsl-ledger report --trades-snapshot tests/fixtures/now_2026_07_01_fills.json --account-snapshot <NLV 3819828.43> --registry <NOW reg 2026-07-01>` | exactly one closed episode: `NOW long 1000 sh 2026-07-01 -> 2026-07-01 realized +$458.61 (15 fills)`; TODAY/WTD/MTD P&L +$458.61, usage 0.0% OK; exit 0 |
| A-003 | `bsl-size NOW ... --register --registry <tmp>` then `bsl-ledger list` / `tag ABC --date 2026-07-02` / `untag 2026-07-02-ABC-1` / `list` | REGISTERED id appended; list shows it; tag adds, untag removes, list confirms; `test_cli_ledger.py::TestSizeRegister` proves sizing without `--register` never writes |
| A-004 | `pytest tests/test_trades.py -q` | 2026-07-02T01:30Z→ET 2026-07-01 rollover + both DST boundaries (2026-03-09T00:30Z→03-08, 2026-11-02T04:30Z→11-01) pass |
| A-005 | `pytest tests/test_ledger.py::TestBudgets -q` | caps at NLV $3,819,828.43 = $38,198.28 / $114,594.85 / $190,991.42 (blueprint figures exact); second NLV $1,000,000 → 10,000/30,000/50,000; WARNING at ≥75% (boundary −28,648.71 fires, −28,648.70 doesn't); STAND DOWN + exit 5 at ≥100% (CLI test asserts exit 5 with report still printed); profitable bucket = 0.0% |
| A-006 | `pytest tests/test_ledger.py::TestMatching tests/test_cli_ledger.py -q` | OPT-in-registered-symbol, pre-registration, and unregistered fills land on the review list with reasons and contribute $0 to every bucket |
| A-007 | dedupe tests (trades + CLI level) | same fills pulled twice → identical budgets/episodes/review/standdown; duplicate ids surfaced as an informational notice |
| A-008 | `grep -rn "create_order_instruction\|ib_insync\|mcp__" src/` | zero hits (exit 1); scan scripted in `tests/test_guardrails.py` now covers all 7 modules; no blocking/enforcement paths — warnings only (D-003) |
| A-009 | A-002 command + `--json` piped to `json.tool` | valid JSON; `TestReportGroundTruth` asserts semantic match with human output, warnings included verbatim |
| A-010 | `docs/LEDGER_RECIPE.md` + README | Claude-session flow (MCP fetch → write both snapshots → run `bsl-ledger` → relay verbatim) end to end; cold-reader report is two file writes + one command |
| A-011 | **Dave drives** | ⏳ AWAITING SIGN-OFF — one real `bsl-ledger` run vs a fresh trades snapshot; NOW trade appears; totals vs IBKR Desktop. Record here and in STATE.md |

## Builder implementation decisions (recorded as D-022)

- **Report "today"** defaults to the ET date of the trades snapshot's
  `as_of` (report stays a pure function of its inputs); `--today` overrides.
- **Cross-through-zero fills** (e.g. long 100, SELL 200): episode closes,
  a new episode opens with the residual; the fill's `realized_pnl` is
  attributed entirely to the closing episode (never double-counted) and a
  loud warning recommends review. Caught by the D-009 matrix — the first
  implementation double-counted and was fixed before ship.
- **Manual tags** (`bsl-ledger tag`) carry null entry/stop/tier/shares and
  direction `long` by default; `--date` registers at 00:00 ET that day so
  same-ET-day fills match (FR-4 inclusive rule).
- **`available_funds`** added to bsl-snapshot-1 as an optional field
  (needed for the D-019 informational margin line); Sprint 002 snapshots
  without it remain valid — behavior unchanged.
- **Missing/null `realized_pnl`** on a fill parses as 0 (entry fills);
  floats anywhere in money fields are rejected loudly at the boundary
  (`parse_float=Decimal` end to end).
- Staleness applies to both snapshots at `age >= 60 min` (same knob
  pattern as Sprint 002, `--snapshot-max-age-minutes`).

## Deviations from blueprint

None of substance. The ground-truth fixture was constructed from the
documented aggregates (see provenance above) since no raw fill table
exists in the pack — every published number is reproduced exactly.
