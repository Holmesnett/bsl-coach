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
