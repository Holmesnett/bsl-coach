# Architect Briefing — 2026-07-02

_Handoff from the outgoing Architect (Claude Opus 4.7 in Cowork on Dave's MacBook Pro) to the incoming Architect (Fable 5 in Cowork). This is the "where we left off" snapshot per the 120x method. Read this first, then AGENTS.md, then the planning files, then the memory files under `planning/memory/`._

---

## Where things stand — plain English

We spent yesterday and this morning walking Dave through what he actually does when he trades, and turning that into a proper 120x project folder. The intake is complete and lives in `architect-chat-starter-prompt.md` at the project root. The planning skeleton (STATE, DECISIONS, DOMAIN, RISKS, QUESTIONS) exists but is mostly TBD placeholders — the intake seeded the header metadata but hasn't been fleshed out yet. That's what Architect Pack 001 is for.

The code that already exists is **not** in this folder yet. It lives in a separate Cowork outputs directory on the MacBook Pro and has been in daily use since 2026-06-16: a Python parser (`pm_pdf_to_pine.py`) that reads Adam Raposa's daily Pre-Market Planning PDF and emits a dated Pine Script (`bsl_pm_watchlist_YYYY-MM-DD.pine`) that Dave pastes into TradingView. The parser works — it has parsed every PDF from June 16 through today (July 1) — but it has thin edges. That code should move into `src/` in Sprint 002 or later, once we've decided the shape of what to build on top of it.

We paused mid-discovery-brainstorm to switch the underlying Cowork model from Claude Opus 4.7 to Fable 5, because Dave wanted the Architect and Builder to run on the same model and Fable was just brought back online. That's why you are reading this briefing rather than the raw intake.

## Where the brainstorm actually is (unfinished threads)

I painted the big picture for Dave and posed two open questions. He hasn't answered either yet. The next thing you do — after reading everything — is pick these up as the actual conversation.

**Open question 1 — MVP slice.** I offered three ways to slice the first *implementation* sprint after Discovery:

1. **Harden the parser we already have.** It works but has known thin edges: apostrophe typos in Adam's PDFs cause silent ticker drops (already patched once for July 1), no stop losses in the data model, no conviction tiers per ticker, no on-chart sizing display.
2. **Jump to the live-account position sizing calculator.** Reads current NLV via the IBKR MCP connector, applies Dave's risk framework (per-trade tiers + daily/weekly/monthly caps + 5% concentration cap), returns exact share count. This is the piece that actually protects Dave from a sizing mistake on real money.
3. **Build the observability TUI first.** Terminal dashboard (Python + `rich` or `textual`) showing active positions, daily/WTD/MTD Active BSL P&L, Legacy Portfolio MTM, risk budget usage, open orders. Lets Dave stop staring at IBKR Desktop all day.

Each is a different bet on what changes Dave's Monday morning most. I'd lean toward #2 because it's the piece that touches money, but I didn't push. Ask him.

**Open question 2 — rigor tier.** The intake tags this project as "Micro app" (single user, low stakes). User count is right — it's just Dave. But every output informs a real-money decision on a live account (~$4M NLV today, $10M+ after Dec 9 2026 SPCX lockup expiration). "Low stakes" is technically stretching.

My proposal to Dave (which he hasn't confirmed): **keep Micro-app rigor everywhere EXCEPT validation on money-touching code — raise the bar there.** Nothing changes on auth, multi-user, data sensitivity, or scale. But any code that does math on NLV, stop distances, position sizes, or risk-budget consumption should have real tests (both happy path and edge cases: zero stop distance, entry crossing stop, floating-point boundary conditions on share counts, NLV mid-fetch). This should reflect in acceptance criteria for any sprint that ships sizing or risk-cap logic.

If Dave wants full Micro-app rigor for speed, that's his call — but flag it explicitly rather than defaulting.

## What Dave has agreed to (informal — verify before treating as hard decisions)

These came out of prior conversation. They should probably land in `planning/DECISIONS.md` as part of Architect Pack 001, but confirm with Dave first before writing them as decisions:

- **Cutoff date for Active BSL vs Legacy P&L split: 2026-07-01** (day of first tagged BSL trade, $NOW long 1000 @ $105.57). Everything before that date = Legacy Portfolio (MTM only, not governed by risk caps). On or after = Active BSL (subject to risk framework).
- **Post-lockup NLV scaling handled by %-based framework** — $4M → $10M+ transition after Dec 9 2026 auto-scales because the framework is percentage-based, not dollar-based. Worth explicit review at that time to confirm caps feel right at the new capital level.
- **Trade execution stays manual.** The system may propose or stage bracket orders via `create_order_instruction` (which lands in IBKR Desktop's "Review Instructions" tab), but never fires them. Dave clicks to transmit every order.
- **Discord as informal paste-based intake in v1.** No Discord MCP in Anthropic's vetted registry. If volume warrants, v2 could add a webhook receiver.
- **Pine Script transfer via `pbcopy` in v1.** TradingView has no public API. Claude in Chrome could automate the paste but adds fragility.
- **`state.md` pattern for cross-device continuity** between Dave's MacBook Pro and Mac Studio via iCloud Drive sync. This briefing plus the memory files below are step 1 of that pattern in practice.
- **GitHub private repo `bsl-coach`** for version control (URL TBD; Dave to create under personal account or the Hudson Mac Cayman org).
- **Fable 5 as the Builder** — Dave has a Builder terminal window teed up on Fable 5. The Cowork Architect now runs on Fable 5 as well (you).

## Active live-account context at time of handoff

Dave is currently in a live BSL position — this is the trade that anchors the "Active BSL" cutoff:

- **Ticker:** NOW (ServiceNow)
- **Position:** Long 1000 shares, average fill $105.57
- **Bracket structure:** Sell limit at $109.27 (T1), sell stop at $104.59
- **Last snapshot before handoff:** $106.03, +$460 unrealized, ~3% away from T1
- **From:** Adam Raposa's PM Planning PDF, 2026-07-01, entry KL 105 / T1 109.26 / T2 115
- **Sizing profile:** ~$980 risk = 0.025% of $4M NLV, well below base tier (0.10%). Concentration = 2.6%, well under 5% cap.

Do not propose changes to this position. Dave manages it manually.

## Broader account context

- Live IBKR account (NOT paper — earlier notes about paper mode DU9889832 are outdated as of 2026-07-01).
- ~$3.89M NLV, 47 open positions including multi-leg options structures (MU spreads, MRVL spreads, HOOD spreads, MSTR/TSLA/CBRS collars, etc.). Dave runs a sophisticated hedged book — do not treat him as a beginner and do not offer beginner framing in advice.
- IBKR MCP connector confirmed available in Cowork on 2026-07-01 (tools begin with `mcp__e6eff5f8-fb46-4232-8801-605c334177f8__`). This supersedes the older ibkr-claude-connector memory file which says the connector was Cowork-unavailable — that fact was correct on 2026-06-17 but is no longer true.

## Existing code (in a separate outputs directory on MacBook Pro, NOT yet in this folder)

Two working artifacts that need to be moved into `src/` at some point:

- `pm_pdf_to_pine.py` — Python parser using pdfplumber. Reads Adam's PM PDF, extracts tickers + KLs + conditional setups, renders into a Pine Script template. Handles primary and inverse-scenario setups. Regex for setup extraction was patched once for missing-apostrophe typos in Adam's writing.
- `bsl_pm_watchlist_YYYY-MM-DD.pine` (multiple dated files) — TradingView Pine Script v5 indicator with entry/T1/T2/stop lines, VWAP, prior-day LOCH, session shading, conditional setup rendering, optional info table (default off per Dave's dashboard-chart-no-overlap preference).

These have been in daily use since 2026-06-16. They work. They're not tested formally. Moving them into `src/` with a real test harness is a good candidate for early Sprint work.

## What to do next (Fable 5, when you pick up)

1. **Read this briefing.** Then AGENTS.md, then the planning files (STATE, DECISIONS, DOMAIN, RISKS, QUESTIONS), then the memory files under `planning/memory/`.
2. **Open the conversation in the Architect voice** — calm, plain English, no jargon. Confirm to Dave that you've caught up. Ask if the two open questions are still the right questions or if his thinking has moved.
3. **Have the back-and-forth.** Don't jump to producing a pack. Discovery is a conversation.
4. **Only when Dave explicitly says "generate the pack" (or equivalent)** — produce `planning/architect-packs/architect-pack-001-discovery.md` per the delimiter rules in `architect-chat-starter-prompt.md`, then stop.

## One asymmetry to know about

The outgoing Architect (Claude Opus 4.7) has been in this project for two solid days of conversation across two Cowork sessions. Fable 5 is walking in cold. Everything meaningful should be in this briefing and the folder — but if you find something that seems obvious to Dave and confusing to you, ask. Dave has been generous with context throughout; he won't mind explaining anything twice.

Good luck. The folder is the source of truth from here.
