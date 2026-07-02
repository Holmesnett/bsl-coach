# Project State

**Project:** BSL Coach
**Client:** Hudson Mac Cayman Holding Company
**Last updated:** 2026-07-01 (Architect Pack 001 applied)

---

## Current Phase

Build — Sprint 002 (Position Sizing Calculator)

Discovery / Architecture (Sprint 001) is complete. This pack is its output.

---

## Current Status

- Canonical project folder: `~/Documents/Claude/Projects/bsl-coach` (iCloud-shared between MacBook Pro and Mac Studio; single Cowork project named "BSL Coach" points at it).
- Discovery complete: planning files populated, 15 decisions recorded, Sprint 002 specified.
- Working parser (`pm_pdf_to_pine.py`) still lives in a separate Cowork outputs directory — in daily use since 2026-06-16, migrates into `src/` in a later sprint (see D-010 alternatives).
- No application code in `src/` yet. Sprint 002 authorizes the first implementation work.

## Active Sprint

`planning/sprints/002-position-sizing-calculator/`

Sprint 002 — Position Sizing Calculator (CLI core + conversational wrapper; tiers + caps only; numbers only, no order staging).

## Live-account context

- IBKR account is LIVE (~$3.9M NLV, 47 legacy positions). Never auto-fire orders. Never propose trades.
- Active BSL ledger cutoff: 2026-07-01 (first tagged trade: NOW long 1000 @ $105.57).
- Post-Dec-9-2026 SPCX lockup, NLV scales to $10M+; %-based framework auto-scales (review then).

## Next Actions

1. Initialize git in the project folder (if not already) and set remote to `https://github.com/Holmesnett/bsl-coach.git` (D-007); first push.
2. Builder reads `planning/sprints/002-position-sizing-calculator/` (all four files) and implements.
3. On sprint completion: update this file, DECISIONS.md, FILE_INVENTORY.md, docs/; push.

## Blockers

None.

## Watch Items

- Money-touching code carries a raised validation bar (D-009). Acceptance is not negotiable on the risk-math test matrix.
- Let iCloud sync settle before switching devices; push to GitHub once the repo exists.
- Keep secrets and account credentials out of project files.
