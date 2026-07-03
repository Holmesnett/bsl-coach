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
