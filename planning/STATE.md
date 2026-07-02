# Project State

**Project:** BSL Coach
**Client:** Hudson Mac Cayman Holding Company
**Last updated:** 2026-07-01 (Sprint 003 Builder complete — A-011 live checks pending on both sprints)

---

## Current Phase

Build — Sprint 003 (Active BSL Ledger + Budget Checks) **code complete**.
202 tests green, A-001..A-010 verified (see sprint 003 CLOSEOUT.md) —
**awaiting Dave's A-011 live check** (one real `bsl-ledger` run vs IBKR
Desktop records).

Sprint 002 (Position Sizing Calculator) also code complete — **its A-011
live smoke test is likewise awaiting Dave** on the next real trading
morning. Neither A-011 blocks the other.

---

## Current Status

- Canonical project folder: `~/Documents/Claude/Projects/bsl-coach` (iCloud-shared MacBook Pro ↔ Mac Studio; single Cowork project "BSL Coach").
- Git remote `https://github.com/Holmesnett/bsl-coach.git`; scaffold, Sprint 002, PDF corpus, utility-script, and Sprint 003 commits pushed.
- **Sprint 002 shipped:** `src/bsl_coach/` (risk_math / snapshot / cli), `bsl-size` CLI, 81 tests. Dress-rehearsed against live account data 2026-07-01 evening (NLV $3,819,828.43; NOW sizing verified against hand math — concentration cap binding at 1,602 shares).
- **Sprint 003 shipped:** registry (`bsl-registry-1`, D-018), trades ingest (`bsl-trades-1`, UTC→ET per D-021), episode ledger + FR-7 budgets (D-009 money-touching matrix), `bsl-ledger` CLI (report/tag/untag/list, exits 0/4/5), `bsl-size --register`. Ground-truth gate passed: NOW fixture reproduces exactly +$458.61 on ET 2026-07-01 (R-011). 202 tests green; Sprint 002's 81 untouched.
- PM Planning PDF fixture corpus: 87 PDFs in `references/client-docs/` spanning May 2025 – Jul 2026 (Q-010; D-017 filing script).
- Working parser (`pm_pdf_to_pine.py`) still outside this folder; migration remains a future sprint.

## Active Sprint

None active — Sprint 003 Builder work done; both sprints close on their
A-011 sign-offs.

## Live-account context

- IBKR account is LIVE. NLV $3,819,828.43 as of 2026-07-01 ~21:30 ET. Never auto-fire orders. Never propose trades.
- Active BSL ledger cutoff: 2026-07-01. First tagged trade CLOSED same day: NOW long 1000 @ $105.57 avg (10:59 ET) → sold 1000 @ $106.04 limit (14:55 ET), realized +$458.61 net. Active BSL ledger: 1 trade, 1 win, +$458.61.
- Post-cutoff NON-BSL activity exists (MU/SNDK/SHAZ/SNDU adds, recurring PURR buys, options rolls) — this is why tagging is registry-based (D-018), not date-based; the ledger routes it to the review list, never into P&L.
- Post-Dec-9-2026 SPCX lockup, NLV scales to $10M+; %-based framework auto-scales (review then, Q-006).

## Next Actions

1. Dave: Sprint 002 A-011 — one real morning sizing vs hand math; record in sprint 002 CLOSEOUT.md and here.
2. Dave: Sprint 003 A-011 — one real `bsl-ledger` run against a fresh trades snapshot (flow: `docs/LEDGER_RECIPE.md`); NOW trade appears; totals vs IBKR Desktop. Record in sprint 003 CLOSEOUT.md and here.
3. On both sign-offs: next Architect conversation picks parser migration vs observability TUI.

## Blockers

None.

## Watch Items

- Both A-011 live checks are open — the ledger is not "trusted" until its totals are sanity-checked against IBKR Desktop once (R-011 field-semantics check on real connector output, not just the fixture).
- Money-touching code carries the D-009 raised validation bar — Sprint 003's P&L and budget math shipped with the mandatory matrix (a real double-count bug on cross-through-zero fills was caught by it pre-ship).
- Let iCloud sync settle before switching devices; push to GitHub at every sprint boundary.
