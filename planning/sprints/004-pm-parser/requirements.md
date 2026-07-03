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
