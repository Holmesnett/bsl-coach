# Sprint 004 Builder Handoff — PM Planning Parser Migration

You are the Builder for BSL Coach Sprint 004. Read, in order: `AGENTS.md`,
`planning/STATE.md`, `planning/DECISIONS.md` (D-003, D-005, D-009, D-014,
D-017 govern here), `planning/DOMAIN.md`, `planning/memory/
dashboard-chart-no-overlap.md`, then all four files in
`planning/sprints/004-pm-parser/`. Implement from the sprint files only.

Optional prior art: if `references/legacy-parser/pm_pdf_to_pine.py` exists,
read it for parsing insights on older PDF formats — but implement fresh in
`src/bsl_coach/` per the blueprint either way. If it is ABSENT (it lives on
Dave's other machine and may arrive mid-sprint or not at all — Architect
decision 2026-07-02): proceed without it; the blueprint's golden values +
parsing notes + the corpus sweep are the authority. Note its absence in
CLOSEOUT. If the sweep shows high unrecognized-bullet rates on older PDFs,
report the shapes verbatim and flag for the Architect — never guess at
legacy behavior.

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
