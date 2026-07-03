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
- Working parser `pm_pdf_to_pine.py` (daily use since 2026-06-16) lives on the MacBook Pro, outside the repo. **Optional** prior art: Dave copies it to `references/legacy-parser/` if/when found; the Builder proceeds without it (blueprint + corpus sweep are the authority — Architect decision 2026-07-02).

## Active Sprint

`planning/sprints/004-pm-parser/` — PM Planning Parser Migration (parse → JSON → Pine + board generators + archive).

## Live-account context

- IBKR account LIVE. NLV $3,707,218.20 at 2026-07-02 midday (drifts with legacy MTM; all caps % of NLV). Never auto-fire orders. Never propose trades.
- Active BSL ledger: 1 trade, 1 win, +$458.61 (NOW, 2026-07-01). Registry-based tagging (D-018). Zero BSL trades 7/2 (deliberate workflow-build day).
- BTC ~$60.4K vs the crypto complex's $60K dead-if line — context for the current watchlist (HOOD/MSTR/CRCL), not a code concern.

## Next Actions

1. Builder (Claude Code): apply this pack (`node scripts/apply-architect-pack.js`), then execute Sprint 004 from `planning/sprints/004-pm-parser/`. Legacy parser is OPTIONAL prior art (see handoff) — do not block on it.
2. Dave (whenever next on the MacBook Pro): Spotlight "pm_pdf_to_pine", copy into `references/legacy-parser/` if found — useful but not required.
3. Monday 7/6: A-011 sizing dry-run (closes Sprint 002); Sprint 004's live acceptance (A-010) runs on the first real PDF after code-complete.
4. After Sprint 004: journaling automation (Q-011) is the leading Sprint 005 candidate.

## Blockers

None. (Sprint 004 start gated only on the legacy parser copy — Next Action 1.)

## Watch Items

- iCloud dataless files on Mac Studio (R-005 flavor): host-side reads materialize; `brctl download` recommended once.
- A-011 (Sprint 002) still open until Monday's run.
- Q-006 lockup review scheduled 2026-12-09.
