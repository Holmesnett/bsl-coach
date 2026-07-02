============================================================
FILE: planning/STATE.md
============================================================

# Project State

**Project:** BSL Coach
**Client:** Hudson Mac Cayman Holding Company
**Last updated:** 2026-07-01 (Architect Pack 002 applied — Sprint 003 authorized)

---

## Current Phase

Build — Sprint 003 (Active BSL Ledger + Budget Checks) authorized and active.

Sprint 002 (Position Sizing Calculator) is code complete — 81 tests green, A-001..A-010 verified (see sprint 002 CLOSEOUT.md) — **awaiting Dave's A-011 live smoke test** on the next real trading morning. A-011 does not block Sprint 003.

---

## Current Status

- Canonical project folder: `~/Documents/Claude/Projects/bsl-coach` (iCloud-shared MacBook Pro ↔ Mac Studio; single Cowork project "BSL Coach").
- Git remote `https://github.com/Holmesnett/bsl-coach.git`; scaffold, Sprint 002, PDF corpus, and utility-script commits pushed.
- **Sprint 002 shipped:** `src/bsl_coach/` (risk_math / snapshot / cli), `bsl-size` CLI, 81 tests green. Dress-rehearsed against live account data 2026-07-01 evening (NLV $3,819,828.43; NOW sizing verified against hand math — concentration cap binding at 1,602 shares).
- **Sprint 003 authorized (this pack):** BSL trade registry, trades-snapshot ingest, episode/P&L ledger with ET bucketing, daily/weekly/monthly budget checks, `bsl-ledger` CLI report.
- PM Planning PDF fixture corpus: 87 PDFs in `references/client-docs/` spanning May 2025 – Jul 2026 (Q-010; D-017 filing script).
- Working parser (`pm_pdf_to_pine.py`) still outside this folder; migration remains a future sprint.

## Active Sprint

`planning/sprints/003-active-bsl-ledger/`

Sprint 003 — Active BSL Ledger & Budget Checks.

## Live-account context

- IBKR account is LIVE. NLV $3,819,828.43 as of 2026-07-01 ~21:30 ET. Never auto-fire orders. Never propose trades.
- Active BSL ledger cutoff: 2026-07-01. First tagged trade CLOSED same day: NOW long 1000 @ $105.57 avg (10:59 ET) → sold 1000 @ $106.04 limit (14:55 ET), realized +$458.61 net. Active BSL ledger: 1 trade, 1 win, +$458.61.
- Post-cutoff NON-BSL activity exists (MU/SNDK/SHAZ/SNDU adds, recurring PURR buys, options rolls) — this is why tagging is registry-based (D-018), not date-based.
- Post-Dec-9-2026 SPCX lockup, NLV scales to $10M+; %-based framework auto-scales (review then, Q-006).

## Next Actions

1. Builder executes Sprint 003 from `planning/sprints/003-active-bsl-ledger/`.
2. Dave: A-011 (Sprint 002) live smoke test next trading morning — record sign-off in sprint 002 CLOSEOUT.md and here.
3. On Sprint 003 completion + A-011: both sprints close; next Architect conversation picks parser migration vs observability TUI.

## Blockers

None.

## Watch Items

- Money-touching code carries the D-009 raised validation bar — Sprint 003's P&L and budget math is money-touching.
- IBKR `realized_pnl` field semantics must be verified against the NOW trade ground truth (+$458.61) before the ledger is trusted (R-011).
- Let iCloud sync settle before switching devices; push to GitHub at every sprint boundary.

============================================================
FILE: planning/STATUS.json
============================================================

{
  "schemaVersion": 1,
  "phase": "build",
  "sprint": "003-active-bsl-ledger",
  "updated": "2026-07-01"
}

============================================================
FILE: planning/sprints/003-active-bsl-ledger/requirements.md
============================================================

# Sprint 003 Requirements — Active BSL Ledger & Budget Checks

## Why (business goal)

The risk framework's loss caps (daily 1% / weekly 3% / monthly 5% of NLV) currently exist only in Dave's memory. They cannot fire on the right signal because the 47-position Legacy book's MTM noise swamps the Active BSL P&L — and because Dave also makes non-BSL trades after the 2026-07-01 cutoff (MU rolls, SNDU/SHAZ adds, recurring PURR buys), so date-based tagging misclassifies (proven against real fills on 2026-07-01). Tonight's NOW trade required manual archaeology through raw fills to answer "how did my one BSL trade do?" — that question must be one command.

## What

Extend `src/bsl_coach/` with:

1. **BSL trade registry** (`data/bsl_registry.json`) — the tagging system (D-018). A trade is a BSL trade if and only if it is registered. Registration happens at sizing (`bsl-size ... --register`) or manually (`bsl-ledger tag` / `untag` / `list`).
2. **Trades snapshot ingest** (`data/trades_snapshot.json`) — raw IBKR fills written by a Claude session from `get_account_trades` (D-020, same pattern as the account snapshot per D-014). Python never calls MCP.
3. **Ledger engine** — matches STK fills to registered setups, builds trade episodes (entry fills → flat), computes realized P&L per episode from IBKR's per-fill `realized_pnl`, buckets by ET day/week/month (D-021).
4. **Budget checks** — Active BSL realized P&L vs caps: daily 1.0%, weekly 3.0%, monthly 5.0% of NLV (NLV from the account snapshot). Warnings at 75% usage; stand-down messaging at 100% per the framework (daily → stop for the day; weekly → halve next week's sizing; monthly → stop a week and journal). **Warnings only — nothing is ever blocked; execution is manual anyway (D-003).**
5. **`bsl-ledger` CLI report** — today / WTD / MTD Active BSL realized P&L, per-episode lines, budget usage, open registered positions (unrealized shown as info, NOT counted toward caps), unmatched-fill review list, and an informational margin-feasibility line (available funds from the account snapshot) per D-019.

## Functional requirements

- FR-1: Registry entries carry: id, symbol, direction, registered_at (UTC ISO Z), entry, stop, tier, shares_sized, status (active/closed/abandoned), note. Versioned schema `bsl-registry-1`.
- FR-2: `bsl-size --register` appends a registry entry on a successful sizing (exit 0 only). No flag → no registration (sizing alone never tags).
- FR-3: `bsl-ledger tag SYMBOL [--date YYYY-MM-DD] [--note ...]` and `bsl-ledger untag <id>` provide the manual override; `bsl-ledger list` shows the registry.
- FR-4: Matching rule: STK fills only, fill symbol == registered symbol, fill ET date >= registration ET date (same-ET-day inclusive regardless of clock time — Dave may register moments after entry). OPT fills never match in v1; those in registered symbols appear on the review list.
- FR-5: Episode = consecutive matched fills from first entry until net shares return to zero. Re-entry after flat starts a new episode. Episode realized P&L = sum of matched fills' `realized_pnl`. Bucket attribution: P&L lands in the ET date of each closing fill.
- FR-6: All bucketing in America/New_York (D-021): day = ET calendar day; week = Mon–Fri ET containing the day; month = ET calendar month. Fill timestamps arrive UTC and convert at ingest.
- FR-7: Budget usage = losses only: usage = max(0, −bucket_P&L) / cap. Profitable buckets show 0% usage. Caps derive from snapshot NLV at report time.
- FR-8: Snapshot rules mirror Sprint 002: versioned schemas, staleness warnings (trades snapshot ≥ 60 min default), malformed = loud failure. Duplicate fills across overlapping snapshot pulls dedupe by `trade_id`.
- FR-9: Exit codes: 0 = report OK (including warnings), 4 = snapshot missing/malformed, 5 = any cap at ≥ 100% (report still prints; the code lets Claude sessions and scripts detect stand-down state).
- FR-10: `--json` output for the full report, semantically matching the human output.

## Out of scope (hard boundaries)

- Blocking or preventing anything — this sprint informs; it never enforces (execution is manual, D-003).
- Options-strategy BSL trades (v1 is STK episodes only; OPT fills go to the review list).
- Auto-tagging heuristics of any kind — registry and manual tags only (D-018).
- MCP calls, network I/O, order staging (D-013, D-014).
- TUI dashboard, parser migration, unrealized P&L counting toward caps.

## Rigor

D-009 applies in full — P&L aggregation and budget math are money-touching. The NOW trade ground truth (R-011) gates trust in IBKR's `realized_pnl` field.

============================================================
FILE: planning/sprints/003-active-bsl-ledger/blueprint.md
============================================================

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

============================================================
FILE: planning/sprints/003-active-bsl-ledger/acceptance.md
============================================================

# Sprint 003 Acceptance — Active BSL Ledger & Budget Checks

- **A-001** — `pytest` green; every blueprint edge case has ≥ 1 test; Sprint 002's 81 tests still pass untouched.
- **A-002** — Ground truth: the NOW fixture yields exactly one closed episode, realized +$458.61 (±$0.01), bucketed to ET 2026-07-01. If irreproducible, sprint stops per blueprint (no improvised P&L definition).
- **A-003** — Registry round trip: `bsl-size ... --register` (exit 0) appends an entry; `bsl-ledger list` shows it; `tag`/`untag` add and remove manual entries; sizing without `--register` never writes.
- **A-004** — ET bucketing: the 2026-07-02T01:30Z→ET-2026-07-01 rollover case and both DST boundary dates pass.
- **A-005** — Budget math at NLV $3,819,828.43 matches the blueprint's worked figures; warning fires at ≥ 75%, stand-down + exit 5 at ≥ 100%, profitable bucket = 0% usage; caps derive from snapshot NLV (test with two different NLVs).
- **A-006** — Review list: OPT fills in registered symbols, pre-registration fills, and unmatched activity appear for review and never enter episode P&L.
- **A-007** — Dedupe: overlapping snapshots (same fills pulled twice) produce identical ledger output.
- **A-008** — Guardrails extended: grep-clean for `create_order_instruction` / `ib_insync` / `mcp__` across all of `src/`; no blocking/enforcement code paths.
- **A-009** — `--json` report is valid JSON and semantically matches human output, warnings included.
- **A-010** — `docs/LEDGER_RECIPE.md` + README updates: the Claude-session flow (fetch trades → write snapshot → run `bsl-ledger`) documented end to end; a cold reader can run a report in 5 minutes.
- **A-011** — Live check (Dave drives): one real `bsl-ledger` run against a fresh trades snapshot; NOW trade appears correctly; totals sanity-checked against IBKR Desktop's own records. Sign-off recorded in CLOSEOUT and STATE.md.

============================================================
FILE: planning/sprints/003-active-bsl-ledger/handoff-prompt.md
============================================================

# Sprint 003 Builder Handoff — Active BSL Ledger & Budget Checks

You are the Builder for BSL Coach Sprint 003. Read, in order: `AGENTS.md`,
`planning/STATE.md`, `planning/DECISIONS.md` (D-018..D-021 govern this sprint),
`planning/DOMAIN.md`, then all four files in
`planning/sprints/003-active-bsl-ledger/`. Implement from the sprint files only.

Build the BSL trade registry, trades-snapshot ingest, episode ledger with ET
bucketing, budget checks, and the `bsl-ledger` CLI exactly as specified.

Hard rules:

- Money-touching code (P&L aggregation, budget math) — the D-009 test matrix in
  the blueprint is mandatory. `Decimal` throughout; fills may have fractional sizes.
- The NOW ground-truth fixture gates everything: if you cannot reproduce
  +$458.61 from the real fills using IBKR's `realized_pnl`, STOP, document the
  discrepancy in CLOSEOUT.md and a decision row — do not invent a P&L definition.
- NO MCP calls, NO network, NO order code, NO blocking/enforcement behavior,
  NO auto-tagging heuristics, NO unrealized P&L in cap math.
- All day/week/month logic in America/New_York via `zoneinfo`; fills arrive UTC.
- Do not modify Sprint 002 behavior except adding `--register`; its 81 tests must
  still pass.
- Do not touch `planning/memory/`, `references/`, or the external parser.

Definition of done: A-001..A-010 verified by you with commands documented in a
CLOSEOUT.md; A-011 flagged as awaiting Dave. Then update `planning/STATE.md`,
`planning/FILE_INVENTORY.md`, `docs/ARCHITECTURE.md`, `docs/VALIDATION.md`,
record new decisions with the next D-number (D-022 onward), commit and push.

============================================================
FILE: docs/ARCHITECTURE.md
============================================================

# Architecture — BSL Coach v1

## Shape

Local, file-based Python on macOS. No web framework, no database, no daemon. Three layers:

1. **Claude runtime (Cowork / Claude sessions)** — the only place MCP tools exist. Fetches live account data via the IBKR MCP connector and refreshes the snapshot files; invokes CLIs; relays results. Later sprints: stages orders via `create_order_instruction` (human-transmitted always, D-003).
2. **Pure Python (`src/bsl_coach/`)** — testable logic with zero network access (D-014). Sprint 002: `risk_math`, `snapshot`, `cli` (`bsl-size`). Sprint 003: `registry`, `trades`, `ledger`, `cli_ledger` (`bsl-ledger`). Later: parser (migrated `pm_pdf_to_pine.py`), TUI dashboard.
3. **External surfaces** — TradingView (Pine via `pbcopy`), IBKR Desktop (manual execution; Review Instructions tab for future staged orders), iCloud (folder sync), GitHub (version control).

## Snapshot-file interface (D-014 / D-020)

MCP-callable code and pure Python never mix. Claude sessions write:

- `data/account_snapshot.json` (`bsl-snapshot-1`) — NLV + per-symbol market values (from `get_account_summary` / `get_account_positions`).
- `data/trades_snapshot.json` (`bsl-trades-1`) — raw fills (from `get_account_trades`).

Both are git-ignored, versioned-schema, staleness-checked. Explicit CLI flags always override.

## Data flow

PM PDF → (external parser, pre-migration) → Pine script → TradingView. Sizing: Claude refreshes account snapshot → `bsl-size` → share count + cap checks (+ optional `--register` tags the trade as BSL, D-018). Ledger: Claude refreshes trades snapshot → `bsl-ledger` → episode P&L split Active-BSL vs everything-else, ET-bucketed (D-021), budget usage vs 1%/3%/5% caps — warnings only, never enforcement.

## Key boundaries

- A trade is Active BSL iff it's in the registry (D-018). Date-based tagging was falsified by real post-cutoff non-BSL activity on day one.
- Risk is anchored to NLV, never buying power; Portfolio Margin headroom appears as informational feasibility only (D-019).
- Execution is always human (D-003). Nothing in this codebase transmits, blocks, or enforces.
- The risk framework's constants live in one module, documented against `planning/DOMAIN.md`.

## Future (per roadmap, not yet authorized)

Parser migration with the 87-PDF fixture corpus; observability TUI (framework per Q-002); order-staging integration (write side of the connector, human-transmitted).

============================================================
FILE: docs/VALIDATION.md
============================================================

# Validation — BSL Coach

## Rigor model (D-009)

Micro-app rigor everywhere except money-touching code. Money-touching = anything computing position sizes, stop distances, risk dollars, cap checks, P&L aggregation, budget consumption, or NLV math. That code gets a mandatory test matrix: happy paths AND edge cases. Non-money code gets happy-path plus the failure modes that would lose data.

## Sprint 002 validation (shipped)

- 81 tests green (`PYTHONPATH=src python3 -m pytest -q`); D-009 matrix on `risk_math`; guardrail grep scripted in `tests/test_guardrails.py`.
- Independently re-verified by the Architect 2026-07-01: suite green, guard clean, blueprint reference example reproduced, live dress rehearsal vs hand math exact.
- A-011 (Dave's real-morning smoke test) pending.

## Sprint 003 validation (active)

- Gate 1 — ground truth: the NOW 2026-07-01 fixture (real fills) must reproduce +$458.61 realized through IBKR's `realized_pnl`; irreproducibility stops the sprint (R-011).
- Gate 2 — full matrix green: episodes, ET bucketing (incl. the 2026-07-02T01:30Z → ET 07-01 rollover and DST dates), budget thresholds (75%/100%), dedupe, review-list routing; Sprint 002's suite untouched and green.
- Gate 3 — guardrails extended to new modules; no enforcement/blocking code paths.
- Gate 4 — A-011 live check: one real report vs IBKR Desktop's records, Dave signs off.

## Standing rules

- A failing or missing test on money math blocks sprint completion — no exceptions.
- Every acceptance item maps to a command or a documented manual check.
- Validation behavior changes get recorded here at each sprint boundary.
