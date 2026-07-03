============================================================
FILE: planning/STATE.md
============================================================

# Project State

**Project:** BSL Coach
**Client:** Hudson Mac Cayman Holding Company
**Last updated:** 2026-07-02 evening (Architect Pack 003 applied — Sprint 004 authorized)

---

## Current Phase

Build — Sprint 004 (PM Planning Parser Migration) authorized and active.

Sprints 001 (Discovery) and 003 (Active BSL Ledger) are CLOSED. Sprint 002
(Position Sizing Calculator) is code complete with one open item: **A-011 —
one real morning sizing vs hand math — scheduled for Monday 2026-07-06.**

---

## Current Status

- Canonical folder `~/Documents/Claude/Projects/bsl-coach` (iCloud, MacBook Pro ↔ Mac Studio, per-machine Cowork projects per D-023). Git `https://github.com/Holmesnett/bsl-coach.git`, pushed through the 7/2 EOD commits.
- **Shipped and live-verified:** `bsl-size` (81 tests) + `bsl-ledger` (202 total tests green); ledger reproduced the NOW trade (+$458.61) against IBKR Desktop exactly.
- **Morning routine OPERATIONAL (first full run 2026-07-02):** PDF + call-transcript filing → board → hand-generated Pine watchlist indicator → TV alerts (5-min close through KL) → tier rubric → stop framework. Pain point proven: hand-writing the Pine shipped a bug (empty-array loop guard) that cost chart-debugging time — the motivation for Sprint 004.
- **New standing artifacts (2026-07-02):** `journal/YYYY-MM-DD.md` daily journals; `journal/watchlist.md` + `journal/tickers/{TICKER}.md` (per-ticker level maps, "Set" dates, dead-if lines, git-diff history); `pine/bsl_pm_watchlist_YYYY-MM-DD.pine` dated Pine outputs (stable indicator title "BSL PM Watchlist").
- **Scheduled automations (Cowork runtime, not src/):** `eod-trading-recap` (weekdays 4:15p ET) and `premarket-watchlist-scan` (weekdays 7:45a ET) — both read/write journal files; neither touches src/ or places orders.
- PM Planning fixture corpus: **90 PDFs** in `references/client-docs/` (May 2025 – Jul 2026) + call-transcript markdowns. Q-010 archive feature lands in this sprint.
- Working parser `pm_pdf_to_pine.py` (daily use since 2026-06-16) still lives OUTSIDE the repo — **Dave copies it to `references/legacy-parser/` before the Builder starts** (prior art only; Builder implements fresh).

## Active Sprint

`planning/sprints/004-pm-parser/` — PM Planning Parser Migration (parse → JSON → Pine + board generators + archive).

## Live-account context

- IBKR account LIVE. NLV $3,707,218.20 at 2026-07-02 midday (drifts with legacy MTM; all caps % of NLV). Never auto-fire orders. Never propose trades.
- Active BSL ledger: 1 trade, 1 win, +$458.61 (NOW, 2026-07-01). Registry-based tagging (D-018). Zero BSL trades 7/2 (deliberate workflow-build day).
- BTC ~$60.4K vs the crypto complex's $60K dead-if line — context for the current watchlist (HOOD/MSTR/CRCL), not a code concern.

## Next Actions

1. Dave: copy `pm_pdf_to_pine.py` (+ 1–2 of its dated .pine outputs) into `references/legacy-parser/`.
2. Builder (Claude Code): apply this pack (`node scripts/apply-architect-pack.js`), then execute Sprint 004 from `planning/sprints/004-pm-parser/`.
3. Monday 7/6: A-011 sizing dry-run (closes Sprint 002); Sprint 004's live acceptance (A-010) runs on the first real PDF after code-complete.
4. After Sprint 004: journaling automation (Q-011) is the leading Sprint 005 candidate.

## Blockers

None. (Sprint 004 start gated only on the legacy parser copy — Next Action 1.)

## Watch Items

- iCloud dataless files on Mac Studio (R-005 flavor): host-side reads materialize; `brctl download` recommended once.
- A-011 (Sprint 002) still open until Monday's run.
- Q-006 lockup review scheduled 2026-12-09.

============================================================
FILE: planning/STATUS.json
============================================================

{
  "schemaVersion": 1,
  "phase": "build",
  "sprint": "004-pm-parser",
  "updated": "2026-07-02"
}

============================================================
FILE: planning/sprints/004-pm-parser/requirements.md
============================================================

# Sprint 004 Requirements — PM Planning Parser Migration

## Why (business goal)

Every trading morning starts with Adam's PM Planning PDF (~8:45 ET). Today the
pipeline from PDF to actionable surfaces is manual: a Claude session reads the
PDF, hand-builds the board, and hand-writes the day's Pine watchlist indicator.
On 2026-07-02 — the first full live morning — the hand-written Pine shipped a
runtime bug (invalid empty-array loop guard) that silently drew nothing on 8 of
9 tickers and cost the open's prep time. The working extraction logic that has
parsed these PDFs daily since 2026-06-16 (`pm_pdf_to_pine.py`) lives outside
the repo, untested, unversioned. A 90-PDF fixture corpus is already filed.
Migrate the capability into `src/` with tests, and make the morning outputs
(watchlist JSON, Pine file, board markdown) generated, not hand-written.

## What

Extend `src/bsl_coach/` with a parser and two generators behind one CLI:

1. **PDF parser** (`pm_parser.py`) — pdfplumber-based extraction of the PM
   Planning PDF into a versioned JSON model (`bsl-pmplan-1`): plan date,
   watchlist setups per ticker (section, side, entry KL, ordered targets,
   conditional flip setups like QQQ's "if we break below, short off X").
2. **Pine generator** (`pine_gen.py`) — JSON → dated Pine v5 file
   (`pine/bsl_pm_watchlist_YYYY-MM-DD.pine`) reproducing the proven 2026-07-02
   template: stable indicator title "BSL PM Watchlist", per-symbol levels
   (entry purple / targets green / supports-downside red / session H-L yellow
   dotted / current-price white dotted), labels, self-diagnosis label for
   off-watchlist symbols, and alert() on a completed 5-min close through an
   entry KL (both directions).
3. **Board generator** (`board_gen.py`) — JSON → markdown board table
   (ticker / side / KL / targets / conditional) suitable for pasting into the
   daily journal.
4. **`bsl-pm` CLI** (`cli_pm.py`) — subcommands: `parse <pdf> [--json out]`,
   `pine <json|pdf> [--out] [--copy]` (pbcopy per D-005, optional flag),
   `board <json|pdf>`, `archive` behavior below.
5. **Archive (Q-010)** — on successful parse, copy the source PDF into
   `data/pdf_archive/` (git-ignored), idempotent, never move/delete the
   original. (The D-017 Downloads-filing script remains separate and untouched.)

## Functional requirements

- FR-1: JSON schema `bsl-pmplan-1`: `{schema, source_pdf, plan_date (ET
  YYYY-MM-DD, from the PDF title line), setups: [{ticker, section
  ("adam"|"community"), side ("long"|"short"), condition ("primary"|
  "if_break_below"), entry, targets: [..ordered..], raw_text}]}`. Prices are
  JSON numbers parsed as Decimal; `raw_text` preserves the source bullet.
- FR-2: Level-text tolerance. The PDFs write levels as "the 729.60's KL",
  "the 733's KL", "737.35's", "the 59.51's KL/62.80's KL" (slash = two
  targets), occasional doubled dots ("140..50's" appears in call notes) and
  missing apostrophes ("125.71s KL"). The extractor must handle: N's / Ns /
  N.NN's / slash-separated pairs, and strip the "s"/"'s" decoration. Unknown
  bullet shapes must be reported (see FR-5), never silently dropped.
- FR-3: Conditional setups: a bullet containing a break-below (or break-above)
  clause yields TWO setup rows for that ticker: the primary and the
  conditional with its own entry and targets (QQQ pattern, seen 7/1 and 7/2).
- FR-4: Sections: setups under "Adam's Watchlist" → section "adam"; under
  "COMMUNITY WATCHLIST" → "community". Header text may carry emoji/decoration.
- FR-5: Corpus behavior: `bsl-pm parse` on any of the 90 corpus PDFs must exit
  0 with a parse report (n setups extracted, n bullets unrecognized, listed
  verbatim) or exit 2 with a loud diagnostic — never a traceback, never
  silent partial output. Unrecognized bullets go into the JSON under
  `unparsed: [..]`.
- FR-6: Pine generator hard requirements: valid Pine v5; every `for` loop over
  a possibly-empty array is guarded by an `if array.size(x) > 0` block (the
  2026-07-02 bug class — regression-tested by generating a ticker with no
  short entries and no supports); stable indicator title; no info tables or
  data panels (memory: dashboard-chart-no-overlap); alert() only, no
  alertcondition.
- FR-7: Board generator: markdown table exactly matching the journal
  conventions established 2026-07-02 (see journal/2026-07-02.md board layout);
  conditional setups rendered on their own row.
- FR-8: Determinism: same input PDF → byte-identical JSON, Pine, and board
  outputs (stable ordering; no timestamps inside generated Pine except the
  dated filename; JSON `source_pdf` is the basename only).
- FR-9: Exit codes: 0 parse OK (including unparsed-bullet warnings), 2 invalid
  input/unreadable PDF, 3 output-write failure. `--json` report for `parse`.

## Out of scope (hard boundaries)

- No sizing, risk, or P&L math (bsl-size / bsl-ledger untouched; their suites
  must pass unmodified).
- No MCP calls, no network, no order code (D-003/D-013/D-014).
- No transcript/Zoom-notes parsing (v2 candidate; PDFs only).
- No auto-writing to `journal/` or `journal/tickers/` — homework files remain
  human-curated; the board output is copy-paste material.
- No TradingView automation beyond optional `pbcopy` (D-005).
- No modification of the two Cowork scheduled tasks or hand-built pine/ files.

## Rigor

Not money-touching in the D-009 sense (no dollars computed), BUT extraction
errors put wrong levels on live charts. Raised bar accordingly: golden-value
extraction tests on a curated fixture set (below) are mandatory, and the
corpus sweep is an acceptance gate.

============================================================
FILE: planning/sprints/004-pm-parser/blueprint.md
============================================================

# Sprint 004 Blueprint — PM Planning Parser Migration

## Layout

```
src/bsl_coach/
  pm_parser.py        # pdfplumber extraction -> PmPlan model -> bsl-pmplan-1 JSON
  pine_gen.py         # PmPlan -> Pine v5 text (template below)
  board_gen.py        # PmPlan -> markdown board table
  cli_pm.py           # `bsl-pm` entrypoint: parse / pine / board (+archive)
tests/
  test_pm_parser.py   # golden extraction + tolerance cases + corpus sweep
  test_pine_gen.py    # golden-file Pine + empty-array regression + validity checks
  test_board_gen.py
  test_cli_pm.py
  fixtures/
    pmplan_2026_07_02.expected.json
    pine_2026_07_02.expected.pine
    board_2026_07_02.expected.md
samples/
  pm_watchlist.example.json
docs/PARSER_RECIPE.md # morning flow: PDF lands -> bsl-pm pine --copy -> paste over saved TV script -> re-arm alerts
references/legacy-parser/   # Dave-provided prior art (READ-ONLY for Builder)
```

pyproject: add `pdfplumber` dependency (documented — the legacy parser already
depends on it) and console script `bsl-pm = bsl_coach.cli_pm:main`.

## Golden extraction values (curated fixtures — encode as exact-match tests)

**07_02_2026 PM Planning.pdf** (all "long" unless noted; targets in order):
- QQQ primary: entry 729.60, targets [733, 735, 737.35]; conditional
  if_break_below: side short, entry 725.60, targets [720, 714.70]
- WEN 9.07 → [9.79, 10]; BB 12.94 → [14]; MSTR 100 → [103.43, 107.76];
  CRCL 65.60 → [67.74, 71]; PLTR 130.72 → [134.40, 136.10, 140.50]  (adam)
- HOOD 112.43 → [115.15, 117.76]; COIN 166.43 → [172, 182.50];
  TSLA 430 → [445]  (community)

**07_01_2026 PM Planning.pdf**:
- QQQ primary: 733 → [736, 737.35]; conditional short 729.60 → [725.60, 723.60]
- NKE 40.91 → [41.82, 43]; FMC 12.38 → [13, 13.65];
  OKLO 55.90 → [57.95, 59.51, 62.80]  ← slash pair "59.51's KL/62.80's KL";
  NOW 105 → [109.26, 115]; META 600 → [613.21, 629.50];
  TSLA 421.70 → [430, 445]  (adam)
- AAPL 293 → [297.51, 300]; LUNR 23 → [24, 25.20]; PLTR 120 → [125.71,
  130.72]  ← "125.71s KL" missing apostrophe  (community)

Builder adds ≥3 more curated fixtures from OLDER corpus PDFs (pick spread
across May 2025 / autumn 2025 / spring 2026), hand-verifying values against
the PDFs and recording them in the test file with a comment citing the page.

## Corpus sweep (acceptance gate)

A test (or marked slow test) runs `parse` across ALL PDFs in
`references/client-docs/` (90 at authoring time): assert exit-0 semantics for
every file, zero tracebacks, and emit a summary table (file → setups parsed /
bullets unrecognized). Unrecognized-bullet rate is reported, not asserted to
be zero — old formats may differ; the report tells us where. Persist the
sweep summary to the sprint CLOSEOUT.

## Pine template (generate exactly this shape)

The checked-in `pine/bsl_pm_watchlist_2026-07-02.pine` (final fixed version,
commit 2466554 + the self-diagnosis label added later on 7/2) is the
authoritative template — the golden Pine fixture is derived from it with the
known values above. Structural requirements repeated from FR-6: v5; stable
title "BSL PM Watchlist"; inputs for toggles/colors; per-symbol level arrays
filled in a `barstate.isfirst` block via `if t == "TICKER"` chains; ALL loops
over possibly-empty arrays guarded; session H/L + current-price dotted lines;
right-edge labels; grey "no levels for <ticker> on today's sheet" label when
the symbol has no entries; `alert()` on confirmed close up-through long
entries and down-through short entries. Ticker with targets-but-no-supports
and ticker with no-short-entries must appear in generated-output tests (the
7/2 bug class).

## Level classification for Pine colors

From the model: entry rows → eL (long) / eS (short/conditional). Targets → tp.
"Supports": the PDF does not publish supports as a distinct list inside the
watchlist bullets (those live in Adam's call notes) — downside targets of a
conditional short ARE the red group. Do not invent supports the PDF didn't
state. (Call-note supports remain a human step in v1; transcript parsing is
out of scope.)

## Parsing notes (from the two authored PDFs + corpus spot-checks)

- Title line: "PM Planning with Adam (MM/DD/YYYY)" → plan_date.
- Watchlist bullets: "$TICK: Looking to go long off the X's KL for a push up
  into the Y's KL and potentially the Z's KL." Variations: "short off",
  "push down to", trailing "/W's KL" second alternative on a target, "(s)"
  decorations, unicode quotes/apostrophes, emoji in headers.
- pdfplumber text order is reliable on recent PDFs; older layouts may differ —
  hence the sweep + unparsed reporting rather than hard failure.

## What the Builder must NOT do

No MCP/network/order code (extend `tests/test_guardrails.py` to the new
modules). No edits to risk_math/snapshot/ledger/registry/trades/cli/cli_ledger
beyond pyproject wiring. No writes to journal/, planning/memory/,
references/ (READ corpus only), or the scheduled-task files. `pbcopy` only
behind an explicit `--copy` flag, subprocess-safe on non-macOS (graceful
no-op + message). Legacy parser is reference, not import — no `sys.path`
tricks into references/.

============================================================
FILE: planning/sprints/004-pm-parser/acceptance.md
============================================================

# Sprint 004 Acceptance — PM Planning Parser Migration

- **A-001** — Full suite green; Sprints 002+003 tests (202) pass untouched.
- **A-002** — Golden extraction: 07/01 and 07/02 fixtures reproduce the
  blueprint's values exactly (every ticker, entry, target order, section,
  side, conditional), plus ≥3 Builder-curated older-PDF fixtures with
  hand-verified values.
- **A-003** — Tolerance cases unit-tested: slash target pairs, missing
  apostrophe, doubled dots, unicode apostrophes, emoji headers; unknown
  bullet shapes land in `unparsed` and the parse report, never dropped.
- **A-004** — Corpus sweep: all PDFs in references/client-docs/ parse without
  traceback; sweep summary (per-file setup counts + unrecognized bullets)
  recorded in CLOSEOUT.
- **A-005** — Pine golden file: generated 07/02 Pine matches the expected
  fixture byte-for-byte; regression tests cover a symbol with no short
  entries and no red-group levels (the 7/2 empty-array bug class); generated
  output contains no unguarded `for i = 0 to array.size(...) - 1` over a
  possibly-empty array and no `to na` loop bounds.
- **A-006** — Board golden file matches; conditional setups render as their
  own rows.
- **A-007** — Determinism: parsing the same PDF twice yields byte-identical
  JSON/Pine/board outputs.
- **A-008** — Archive: parse copies the PDF to data/pdf_archive/ (git-ignored,
  idempotent, original untouched); `.gitignore` updated.
- **A-009** — Guardrails extended: grep-clean for `create_order_instruction` /
  `ib_insync` / `mcp__` / network imports across new modules; docs updated
  (PARSER_RECIPE.md, ARCHITECTURE.md, VALIDATION.md, README).
- **A-010** — Live check (Dave drives, first trading morning after
  code-complete): `bsl-pm pine --copy` on the day's real PDF → paste over the
  saved TV script → levels verified correct on 2+ tickers against the PDF by
  eye; board pasted into the day's journal. Sign-off in CLOSEOUT + STATE.md.

============================================================
FILE: planning/sprints/004-pm-parser/handoff-prompt.md
============================================================

# Sprint 004 Builder Handoff — PM Planning Parser Migration

You are the Builder for BSL Coach Sprint 004. Read, in order: `AGENTS.md`,
`planning/STATE.md`, `planning/DECISIONS.md` (D-003, D-005, D-009, D-014,
D-017 govern here), `planning/DOMAIN.md`, `planning/memory/
dashboard-chart-no-overlap.md`, then all four files in
`planning/sprints/004-pm-parser/`. Implement from the sprint files only.

Prerequisite check: `references/legacy-parser/pm_pdf_to_pine.py` must exist
(Dave copies it in). It is PRIOR ART ONLY — read it for parsing insights on
older PDF formats, but implement fresh in `src/bsl_coach/` per the blueprint.
If it is missing, stop and flag rather than guessing at legacy behavior.

Build: pm_parser.py, pine_gen.py, board_gen.py, cli_pm.py (`bsl-pm`), the
fixture set, the corpus sweep, and docs/PARSER_RECIPE.md.

Hard rules:

- NO MCP calls, NO network, NO order code, NO sizing/P&L math. Guardrail tests
  extended to the new modules.
- Existing 202 tests pass unmodified; bsl-size / bsl-ledger behavior untouched.
- The authoritative Pine template is the checked-in
  `pine/bsl_pm_watchlist_2026-07-02.pine` (with self-diagnosis label). Every
  array loop in generated Pine is size-guarded — the 2026-07-02 production bug
  gets an explicit regression test.
- Chart outputs carry no info tables/data panels (dashboard-chart-no-overlap).
- Never write to journal/, references/ (read-only corpus), planning/memory/,
  or Cowork scheduled-task files. Archive writes go to data/pdf_archive/ only.
- Decimal for prices; deterministic outputs; fail loud (exit 2/3), never
  silent partial parses.

Definition of done: A-001..A-009 verified by you with commands documented in
CLOSEOUT.md; A-010 flagged as awaiting Dave's first live morning. Update
planning/STATE.md, planning/FILE_INVENTORY.md, docs/ARCHITECTURE.md,
docs/VALIDATION.md; record new decisions from D-024 onward; note the corpus
sweep results; commit and push.

============================================================
FILE: docs/ARCHITECTURE.md
============================================================

# Architecture — BSL Coach v1

## Shape

Local, file-based Python on macOS. No web framework, no database, no daemon. Three layers:

1. **Claude runtime (Cowork / Claude sessions / scheduled tasks)** — the only place MCP tools exist. Fetches live account data via the IBKR MCP connector and refreshes the snapshot files; invokes CLIs; relays results; runs the premarket scan (7:45a ET) and EOD recap (4:15p ET) scheduled tasks that maintain journal files. Later sprints: stages orders via `create_order_instruction` (human-transmitted always, D-003).
2. **Pure Python (`src/bsl_coach/`)** — testable logic with zero network access (D-014). Sprint 002: `risk_math`, `snapshot`, `cli` (`bsl-size`). Sprint 003: `registry`, `trades`, `ledger`, `cli_ledger` (`bsl-ledger`). Sprint 004: `pm_parser`, `pine_gen`, `board_gen`, `cli_pm` (`bsl-pm`). Later: TUI dashboard (open question Q-002).
3. **External surfaces** — TradingView (generated Pine via `pbcopy` + paste over one saved indicator, D-005), IBKR Desktop (manual execution), iCloud (folder sync), GitHub (version control).

## Snapshot-file interface (D-014 / D-020)

Claude sessions write `data/account_snapshot.json` (`bsl-snapshot-1`) and
`data/trades_snapshot.json` (`bsl-trades-1`); git-ignored, versioned,
staleness-checked; CLI flags override.

## Data flow (morning)

PM PDF lands → `bsl-pm parse` (bsl-pmplan-1 JSON, PDF archived to
data/pdf_archive/) → `bsl-pm pine --copy` (dated Pine, pasted over the saved
"BSL PM Watchlist" TV indicator; alerts re-armed by hand) + `bsl-pm board`
(markdown into the day's journal). Sizing: Claude refreshes account snapshot →
`bsl-size` (+`--register` tags BSL trades, D-018). Ledger: Claude refreshes
trades snapshot → `bsl-ledger` (episodes, ET buckets D-021, budget usage —
warnings only). Journal/watchlist homework files in `journal/` are
human-curated; scheduled tasks update them from live data, `src/` never does.

## Key boundaries

- A trade is Active BSL iff registered (D-018). Risk anchors to NLV, never
  buying power (D-019). Execution always human (D-003); nothing transmits,
  blocks, or enforces.
- Parser tolerance: unknown watchlist bullet shapes surface in parse reports
  (`unparsed`), never silently dropped; corpus sweep tracks format drift.
- Chart layers carry no tabular/info panels (dashboard-chart-no-overlap).

## Future (not yet authorized)

Journaling automation (Q-011, Sprint 005 candidate); observability TUI
(Q-002); transcript parsing; premarket-BSL variant (paper-track first);
order-staging integration last (D-013).

============================================================
FILE: docs/VALIDATION.md
============================================================

# Validation — BSL Coach

## Rigor model (D-009)

Micro-app rigor everywhere except money-touching code (sizes, stops, risk
dollars, caps, P&L, budgets, NLV math) which gets the mandatory edge-case
matrix. Sprint 004 adds a second raised-bar category: **level-extraction
correctness** — not money math, but wrong levels reach live charts; golden
fixtures + corpus sweep are mandatory gates.

## Sprint 002 validation (shipped)

81 tests green; D-009 matrix on risk_math; guardrail grep in
tests/test_guardrails.py; live dress rehearsal vs hand math exact.
A-011 (one real morning sizing) scheduled 2026-07-06.

## Sprint 003 validation (shipped)

Ground-truth gate passed: NOW fixture reproduces +$458.61 via IBKR
`realized_pnl`; ET bucketing incl. 20:00-ET rollover + DST dates; budget
thresholds 75%/100%; dedupe; review-list routing. Live A-011 signed off
2026-07-01 against IBKR Desktop records. 202 tests total.

## Sprint 004 validation (active)

- Gate 1 — golden extraction: 07/01 + 07/02 fixtures exact; ≥3 curated older
  PDFs hand-verified.
- Gate 2 — corpus sweep: every PDF in references/client-docs/ parses without
  traceback; unrecognized-bullet report persisted to CLOSEOUT.
- Gate 3 — Pine golden file byte-exact; empty-array regression (the 2026-07-02
  production bug) explicitly tested; no unguarded loops in generated output.
- Gate 4 — determinism (byte-identical re-runs) + guardrails extended.
- Gate 5 — A-010 live morning: real PDF → generated Pine on charts → levels
  eye-verified vs PDF; Dave signs off.

## Standing rules

- A failing or missing test on money math OR level extraction blocks sprint
  completion — no exceptions.
- Every acceptance item maps to a command or a documented manual check.
- Validation behavior changes get recorded here at each sprint boundary.
