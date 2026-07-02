# Project State

**Project:** BSL Coach
**Client:** Hudson Mac Cayman Holding Company
**Last updated:** 2026-07-01 (Sprint 002 Builder work complete; A-011 pending)

---

## Current Phase

Build — Sprint 002 (Position Sizing Calculator) — **code complete, awaiting Dave's A-011 live smoke test**

Discovery / Architecture (Sprint 001) is complete.

---

## Current Status

- Canonical project folder: `~/Documents/Claude/Projects/bsl-coach` (iCloud-shared between MacBook Pro and Mac Studio; single Cowork project named "BSL Coach" points at it).
- Git initialized 2026-07-01; remote `https://github.com/Holmesnett/bsl-coach.git` (D-007); initial scaffold commit + Sprint 002 commit pushed.
- **Sprint 002 shipped:** `src/bsl_coach/` (risk_math / snapshot / cli), 81 tests green, A-001..A-010 verified with commands documented in `planning/sprints/002-position-sizing-calculator/CLOSEOUT.md`. D-016 recorded.
- **A-011 open:** Dave runs one real morning sizing (recipe in `docs/SIZING_RECIPE.md`) and checks against hand math; record sign-off in CLOSEOUT.md and here.
- Working parser (`pm_pdf_to_pine.py`) still lives in a separate Cowork outputs directory — in daily use since 2026-06-16, migrates into `src/` in a later sprint (see D-010 alternatives).

## Active Sprint

`planning/sprints/002-position-sizing-calculator/`

Sprint 002 — Position Sizing Calculator. Builder phase done; sprint closes on A-011 sign-off.

## Live-account context

- IBKR account is LIVE (~$3.9M NLV, 47 legacy positions). Never auto-fire orders. Never propose trades.
- Active BSL ledger cutoff: 2026-07-01 (first tagged trade: NOW long 1000 @ $105.57).
- Post-Dec-9-2026 SPCX lockup, NLV scales to $10M+; %-based framework auto-scales (review then).

## Next Actions

1. **Dave: A-011 live smoke test** — one real morning sizing via `docs/SIZING_RECIPE.md` (or manual flags), sanity-check against hand math, record sign-off in sprint 002 CLOSEOUT.md and here.
2. On A-011 sign-off, Sprint 002 closes; Architect specifies the next sprint (likely the Active-vs-Legacy ledger tracker per D-012 / ARCHITECTURE.md roadmap).

## Blockers

None.

## Watch Items

- Money-touching code carries a raised validation bar (D-009). Acceptance is not negotiable on the risk-math test matrix.
- Let iCloud sync settle before switching devices; push to GitHub once the repo exists.
- Keep secrets and account credentials out of project files.
