# Architect Briefing — 2026-07-01 ~23:00 ET

_Current-state snapshot per the 120x method. Written by the Architect (Fable 5, Cowork on Dave's MacBook Pro) at the close of the 2026-07-01 build evening. Any fresh session — either machine, either role — reads this first, then AGENTS.md, then the planning files, then `planning/memory/`. If anything here conflicts with STATE.md/DECISIONS.md, the planning files win._

---

## Where things stand — plain English

This project went from Discovery to two shipped, live-verified sprints in one evening (2026-07-01):

- **Sprint 001 (Discovery/Architecture): CLOSED.** Planning files fully populated; decisions D-001..D-022; Architect Packs 001 and 002 applied.
- **Sprint 002 (Position Sizing Calculator): code complete, one item open.** `bsl-size` CLI + pure Decimal risk math, 81 tests. Dress-rehearsed against live account data (NLV $3,819,828.43) and verified against hand math. **A-011 — one real morning sizing after Adam's call — is the ONLY open item; it closes the sprint.**
- **Sprint 003 (Active BSL Ledger + Budget Checks): CLOSED, A-011 signed off live.** `bsl-ledger` reproduced the real NOW trade (+$458.61) exactly against IBKR Desktop's records; 31 non-BSL fills correctly routed to the review list; 202 tests green total.

Git: `https://github.com/Holmesnett/bsl-coach.git`, main at `4302391` (or later). Verify local == origin before working — iCloud sync plus git both carry this folder across machines.

## The morning routine (the reason this system exists)

Dave says "run the morning" (or drops the PDF). The session then:

1. Finds the newest `*PM Planning*.pdf` in `~/Downloads` (needs Downloads folder access — request it), copies it into `references/client-docs/` (`scripts/file_pm_planning.py` does this too).
2. Reads the PDF; extracts tickers, directions, entry KLs, T1/T2, conditional setups, Adam's sizing flags.
3. Fetches live NLV + positions + trades via the IBKR MCP connector (find tools via ToolSearch — server prefix is an opaque id; search "account" or "ibkr"); writes `data/account_snapshot.json` and `data/trades_snapshot.json` per the schemas in `docs/SIZING_RECIPE.md` / `docs/LEDGER_RECIPE.md`.
4. Presents the day's board: setups + cap room + ledger state (`bsl-ledger report`).
5. Conversation: Dave picks setups, sets stops (Adam publishes none — stop is always Dave's), tier decided together per the two-vote rule (Adam's flag + Dave's read; NEVER auto-derived).
6. Sizes approved setups: `PYTHONPATH=src python3 -m bsl_coach.cli TICKER --direction ... --entry ... --stop ... --tier ...` (+ `--register` to tag it as an Active BSL trade — registration IS the BSL tag, D-018).
7. Dave builds and transmits every order manually in IBKR Desktop (D-003 — nothing is ever auto-fired; the system never proposes trades).

## Live-account context

- IBKR account is LIVE, ~$3.82M NLV, 47 legacy positions (sophisticated hedged book — no beginner framing, no trade recommendations, ever).
- Active BSL ledger: cutoff 2026-07-01; 1 trade, 1 win, +$458.61 (NOW long 1000 @ 105.57 → 106.04).
- Tagging is registry-based (`data/bsl_registry.json`), NOT date-based — Dave makes non-BSL trades daily (D-018).
- Caps at current NLV: daily $38.2K / weekly $114.6K / monthly $191K; per-trade tiers 0.10–0.25% NLV, $50K hard cap, 5% concentration. All %-based; auto-scales post-Dec-9 lockup ($10M+ NLV, review then — Q-006).

## Cross-device setup (D-023)

One canonical folder: `~/Documents/Claude/Projects/bsl-coach` (iCloud-synced Documents). One Cowork project named "BSL Coach" on EACH machine (MacBook Pro + Mac Studio), both connected to that same folder. The folder — not any chat — is the source of truth. Before switching machines: update STATE.md, commit, push, let iCloud settle. Each machine needs its own grants: Downloads folder access and the IBKR MCP connector.

## What's next (not yet authorized)

Sprint 004 candidates, in rough order of Dave's interest: daily trade journaling (Q-011 — ledger already generates the quantitative half), parser migration (87-PDF fixture corpus waiting in `references/client-docs/`), observability TUI (framework choice Q-002; the abandoned May repo is NOT a reference — D-015). Order staging (write side of the connector) remains further out.

## Standing rules (never relax these)

Execution always manual (D-003). No MCP/network in `src/` (D-014). Risk anchored to NLV, never buying power (D-019). Money-touching code gets the D-009 test matrix. Tier is always a human decision. ET bucketing everywhere (D-021). The Builder implements only from `planning/sprints/`; the Architect never writes production code outside an authorized utility (D-017).
