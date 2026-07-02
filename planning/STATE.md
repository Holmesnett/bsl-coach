# Project State

**Project:** BSL Coach
**Client:** Hudson Mac Cayman Holding Company
**Last updated:** 2026-07-01 late evening (Mac Studio session: readiness verified; no sprint work)

---

## Current Phase

Build — Sprint 003 (Active BSL Ledger + Budget Checks) **complete and
closed**. A-001..A-011 all verified (see sprint 003 CLOSEOUT.md); A-011
signed off 2026-07-01 ~22:30 ET — live report vs a fresh 47-fill snapshot
matched IBKR Desktop exactly (NOW +$458.61).

Sprint 002 (Position Sizing Calculator) is code complete — **its A-011
live smoke test is still awaiting Dave** on the next real trading morning.

---

## Current Status

- Canonical project folder: `~/Documents/Claude/Projects/bsl-coach` (iCloud-shared MacBook Pro ↔ Mac Studio; single Cowork project "BSL Coach").
- Git remote `https://github.com/Holmesnett/bsl-coach.git`; scaffold, Sprint 002, PDF corpus, utility-script, and Sprint 003 commits pushed.
- **Sprint 002 shipped:** `src/bsl_coach/` (risk_math / snapshot / cli), `bsl-size` CLI, 81 tests. Dress-rehearsed against live account data 2026-07-01 evening (NLV $3,819,828.43; NOW sizing verified against hand math — concentration cap binding at 1,602 shares).
- **Sprint 003 shipped:** registry (`bsl-registry-1`, D-018), trades ingest (`bsl-trades-1`, UTC→ET per D-021), episode ledger + FR-7 budgets (D-009 money-touching matrix), `bsl-ledger` CLI (report/tag/untag/list, exits 0/4/5), `bsl-size --register`. Ground-truth gate passed: NOW fixture reproduces exactly +$458.61 on ET 2026-07-01 (R-011). 202 tests green; Sprint 002's 81 untouched.
- PM Planning PDF fixture corpus: 87 PDFs in `references/client-docs/` spanning May 2025 – Jul 2026 (Q-010; D-017 filing script).
- Working parser (`pm_pdf_to_pine.py`) still outside this folder; migration remains a future sprint.

## Active Sprint

None active — Sprint 003 closed (A-011 signed off 2026-07-01). Sprint 002
closes on its A-011 sign-off.

## Live-account context

- IBKR account is LIVE. NLV $3,819,828.43 as of 2026-07-01 ~21:30 ET. Never auto-fire orders. Never propose trades.
- Active BSL ledger cutoff: 2026-07-01. First tagged trade CLOSED same day: NOW long 1000 @ $105.57 avg (10:59 ET) → sold 1000 @ $106.04 limit (14:55 ET), realized +$458.61 net. Active BSL ledger: 1 trade, 1 win, +$458.61.
- Post-cutoff NON-BSL activity exists (MU/SNDK/SHAZ/SNDU adds, recurring PURR buys, options rolls) — this is why tagging is registry-based (D-018), not date-based; the ledger routes it to the review list, never into P&L.
- Post-Dec-9-2026 SPCX lockup, NLV scales to $10M+; %-based framework auto-scales (review then, Q-006).

## Next Actions

1. Dave: Sprint 002 A-011 — one real morning sizing vs hand math; record in sprint 002 CLOSEOUT.md and here.
2. Next Architect conversation picks the next sprint: parser migration vs observability TUI.

## Mac Studio session — 2026-07-02 (Architect) — first full morning routine

- Morning loop ran end-to-end and is now OPERATIONAL: PDF filed (D-017 script, HOME override for sandbox) + call transcript filed alongside → setups extracted → snapshots written → board presented → Pine watchlist indicator generated (`pine/bsl_pm_watchlist_2026-07-02.pine`, symbol-aware, one saved TV script + "Apply to all charts in layout", 5-min-close entry alerts via alert()).
- Zero trades (deliberate sit-out day to build workflow). Ledger TODAY $0, WTD +$458.61. NLV drifted $3.87M → $3.71M midday (legacy MTM).
- New standing artifacts: `journal/YYYY-MM-DD.md` (daily journal, seeded manually — Sprint 004 will automate the quantitative half), `journal/watchlist.md` (developing-setups index), `journal/tickers/{TICKER}.md` (per-ticker level maps w/ Set dates; history via git diffs; future parser sprint can generate Pine from these). Pine title kept stable ("BSL PM Watchlist") for daily paste-over.
- Teaching threads done live: stop = structure / size = risk / conflict = pass; tier rubric (Pass/C/B/A, max needs two votes, ceiling ~base for first 20-30 trades); five setup states observed in one session (BB walk-through, PLTR retest, HOOD blow-through, COIN runner, WEN failed KL).
- Pending: Sprint 002 A-011 (one real morning sizing vs hand math) — do next morning as dry run. Premarket-BSL variant to be specced + paper-tracked before any capital (Dave's request after HOOD). True 4pm EOD pass proposed as scheduled task.
- Machine notes: PDF read via host Read (triggers iCloud materialization); `.git/index.lock` still present — remove before next commit; journal/, pine/ dirs are new and uncommitted.
- **EOD pass (scheduled task) ran 7/2 ~16:20 ET:** ledger clean (exit 0, TODAY $0 / WTD +$458.61, no warnings); 1 fill today (recurring PURR → review list); NLV closed $3,620,674.81 (−$253.8K on day, all legacy MTM); broad PM fade — HOOD and CRCL lost their KLs on the close, BB failed KL −9.9%, MSTR alone held (100.60); journal EOD section + 3 ticker files + watchlist index updated.

## Mac Studio session — 2026-07-01 late evening (Architect)

- D-023 verified on Mac Studio: git local main == origin (`c4a6c3e`, one past `4302391`); 202 tests green; IBKR connector live (NLV $3,819,828.43, matches); `bsl-ledger report` reproduces NOW +$458.61 with 31 review-list fills. Downloads grant in place.
- iCloud dataless files bit this machine (R-005): sandbox reads failed until host-side reads forced downloads. Recommended one-time fix: `brctl download ~/Documents/Claude/Projects/bsl-coach`; keep Optimize Mac Storage off.
- **Stale `.git/index.lock` left in repo** (sandbox mount can't unlink). Will block next commit; remove with `rm .git/index.lock` first.
- 3 untracked PDFs in `references/client-docs/` (05_14 "-2" dup, 05_15, 05_20) — add or delete at next commit. Also `07_01_2026 PM Planning 2.pdf` is byte-identical to the filed 07/01 PDF.
- Teaching thread open: stop-loss selection (structure sets stop, risk sets size). Walked QQQ/NOW examples off the 07/01 sheet; Dave wants to continue live on the next morning's sheet. Pairs naturally with Sprint 002 A-011 (one real morning sizing vs hand math).

## Blockers

None.

## Watch Items

- Sprint 002's A-011 live check is still open — the sizing flow awaits one real-morning run vs hand math. (Sprint 003's ledger passed its live check: R-011 field semantics confirmed on real connector output 2026-07-01.)
- Money-touching code carries the D-009 raised validation bar — Sprint 003's P&L and budget math shipped with the mandatory matrix (a real double-count bug on cross-through-zero fills was caught by it pre-ship).
- Let iCloud sync settle before switching devices; push to GitHub at every sprint boundary.
