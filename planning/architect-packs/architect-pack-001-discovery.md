============================================================
FILE: planning/STATE.md
============================================================

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

============================================================
FILE: planning/DECISIONS.md
============================================================

# Decisions

Record durable decisions future sprints must respect. Newest at the bottom.

---

## Decision Log

| # | Date | Decision | Reason | Impact |
|---|---|---|---|---|
| D-001 | 2026-07-01 | Active BSL vs Legacy P&L cutoff date is **2026-07-01** | Day of the first tagged BSL trade (NOW long 1000 @ $105.57) | Trades opened before the cutoff = Legacy (MTM only, not governed by risk caps); on/after = Active BSL (governed by the risk framework) |
| D-002 | 2026-07-01 | Risk framework is **percentage-based**, auto-scaling with NLV | $4M → $10M+ transition after the Dec 9 2026 SPCX lockup shouldn't require re-engineering | Caps scale automatically; explicit human review scheduled at lockup expiry (Q-006) |
| D-003 | 2026-07-01 | **Trade execution stays manual, always.** The system may stage bracket orders via `create_order_instruction` (IBKR Desktop → Review Instructions tab) but never transmits | Live account, real capital; human-in-the-loop is the safety boundary | No sprint may ship auto-transmit. Hard rule for every Builder |
| D-004 | 2026-07-01 | Discord setups arrive via **paste-based intake** in v1 | No Discord MCP in Anthropic's vetted registry | v2 may add a webhook receiver if volume warrants (Q-004) |
| D-005 | 2026-07-01 | Pine Script transfer via **`pbcopy` + manual paste** in v1 | TradingView has no public API | Claude-in-Chrome automation is a v2 question (Q-005) |
| D-006 | 2026-07-01 | **One canonical project folder:** `~/Documents/Claude/Projects/bsl-coach`, iCloud-shared; one Cowork project ("BSL Coach"); STATE.md is the cross-device handoff | Dave works on MacBook Pro now, Mac Studio ~90% once built; duplicate projects caused confusion on 2026-07-01 | Update STATE.md before switching machines; the folder, not any chat, is the source of truth |
| D-007 | 2026-07-01 | Version control in **private GitHub repo** `https://github.com/Holmesnett/bsl-coach.git` | Audit trail; safety net beyond iCloud sync | Push before device switches once code exists |
| D-008 | 2026-07-01 | **Fable 5 runs both roles** — Architect (Cowork) and Builder (terminal) | Dave wants Architect and Builder on the same model | Handoff remains the folder, not the conversation |
| D-009 | 2026-07-01 | **Hybrid rigor tier:** Micro-app everywhere EXCEPT money-touching code, which gets a raised validation bar | Single user, but every output informs a live-money decision on a ~$4M account | Any code computing sizes, stops, risk budgets, or NLV math needs real tests: happy path + edge cases (zero stop distance, entry crossing stop, share-count float boundaries, NLV absent/stale). Reflected in every money-touching sprint's acceptance criteria |
| D-010 | 2026-07-01 | **Sprint 002 = position sizing calculator** (chosen over parser hardening and observability TUI) | It's the piece that touches money; protects against a sizing mistake under time pressure | Parser migration into `src/` and the TUI are later sprints |
| D-011 | 2026-07-01 | Calculator interface: **CLI core + conversational wrapper** | Testable CLI (`bsl-size ...`) holds the math; Claude in Cowork can fetch live NLV via the IBKR MCP and invoke it | Math is formally testable; 9:25am ergonomics stay conversational |
| D-012 | 2026-07-01 | Sprint 002 checks: **per-trade tiers + $50K hard cap + 5% concentration only.** Daily/weekly/monthly loss budgets deferred | Loss budgets require the Active-vs-Legacy trade-tagging tracker (`get_account_trades` + D-001 cutoff) — a meaningfully bigger build | Ledger tracker + budget checks become their own sprint |
| D-013 | 2026-07-01 | Sprint 002 output: **numbers only** — no `create_order_instruction` staging | Trust the math before touching the connector's write side | Order staging is a later sprint, after the calculator has proven itself in live mornings |
| D-014 | 2026-07-01 | **IBKR MCP connector is the primary account-data path; IB Gateway/`ib_insync` is fallback.** The connector lives in the Claude runtime only — standalone Python cannot call MCP tools | Connector confirmed live in Cowork 2026-07-01 | Pure-Python code takes account data as inputs (CLI flags or snapshot file); a Claude session or Dave supplies live values. Gateway path reserved for a future standalone TUI |
| D-015 | 2026-07-01 | The May 2026 "BSL Trading Dashboard" repo (textual TUI, Sprint-001-era) is **abandoned, not a dependency** | Pre-dated the IBKR connector and the two-ledger framework; over-complicated per Dave | Do not restore, reference, or pattern-match against it. The future TUI sprint designs fresh against the MCP tools |

============================================================
FILE: planning/DOMAIN.md
============================================================

# Domain Context

Operating context for BSL Coach. Any future session should be able to reason about the system from this file without re-deriving the strategy.

---

## Client

Hudson Mac Cayman Holding Company. Sole user and decision-maker: Dave Holmes — trader, analyst, and executor for all positions. Adam Raposa (humbledtrader.com) appears in the data flow as an external source, not a user.

## Business Goal

Daily pre-market automation pipeline that turns Adam Raposa's Pre-Market Planning PDF into TradingView-ready Pine Scripts, risk-adjusted position sizes, and cleanly separated Active BSL vs Legacy Portfolio P&L, for a solo high-net-worth trader executing BSL setups.

## Key Terms

- **BSL** — the trading methodology taught by Adam Raposa (Humbled Trader). Intake records the expansion as "Buy-Support / Sell-Resistance"; see Q-008 on naming consistency. Discretionary setups at published Key Levels; never algorithmic signal generation.
- **PM Planning** — **Pre-Market** Planning. Adam's single daily brief (live call 8:30 AM ET, PDF ~8:45 AM ET). "PM" never means afternoon in this project.
- **KL (Key Level)** — a price level published in the PM Planning PDF: Entry KL, Target 1 (T1), Target 2 (T2). Adam publishes no stop losses; Dave sets stops himself.
- **Conviction tiers** — Dave's per-setup grade mapping to per-trade risk: Base 0.10% / Medium 0.15% / High 0.20% / Max 0.25% of NLV. "Pass" = no trade. Adam's "size up" flag maps to +1 tier only when Dave's own read agrees (two-vote rule — always human judgment, never automated).
- **NLV** — Net Liquidation Value of the live IBKR account (~$3.9M now; $10M+ expected after Dec 9 2026 SPCX lockup expiration).
- **Legacy Portfolio** — the 47 pre-existing positions (incl. multi-leg options structures). Tracked as MTM baseline only; not managed by this project's tools; not governed by the risk caps.
- **Active BSL** — trades opened on/after 2026-07-01 (D-001). The risk framework governs these only.
- **Staged order** — a bracket created via `create_order_instruction`, landing in IBKR Desktop's Review Instructions tab. Dave manually transmits every order (D-003).

## Business Rules — Risk Framework (established 2026-07-01)

Anchors: $5-10K/day P&L target; 10% max peak-to-trough drawdown.

- Per-trade risk by conviction: 0.10% / 0.15% / 0.20% / 0.25% of NLV.
- Hard cap: no single trade risks more than **$50,000**, regardless of tier or NLV.
- Concentration: no single position exceeds **5% of NLV** (counting any existing position in the same symbol).
- Loss caps (Active BSL ledger only — deferred to the ledger sprint, D-012): daily 1.0% → stop for the day; weekly 3.0% → halve next week's sizing; monthly 5.0% → stop a week and journal; 10% drawdown → full stop and reassess.
- At $4M: base $4K / med $6K / high $8K / max $10K risk per trade. At $10M: $10K / $15K / $20K / $25K.
- Not financial advice; a starter framework Dave iterates as live data accumulates.

## Current Workflow (pain)

8:30 call → ~8:45 PDF → 30-50 min of manual TradingView markup → manual stop selection → hand-calculated sizing under time pressure → manual bracket construction in IBKR Desktop → no Legacy/Active P&L separation, so loss caps can't fire on the right signal. Discord and Dave's own multi-day setups have no unified intake.

## Target Workflow (v1)

PDF → parser extracts tickers/KLs/conditional setups → Dave supplies conviction tier + stop per ticker → dated Pine Script (`bsl_pm_watchlist_YYYY-MM-DD.pine`) via `pbcopy` → sizing calculator returns exact share counts with cap checks → Dave stages brackets in IBKR Desktop and transmits manually → TUI dashboard (later sprint) shows positions, two-ledger P&L, risk budget usage. Non-PDF setups enter via structured paste.

## Execution stack

TradingView = chart/analysis layer (Pine indicator; no info tables duplicating dashboard data — see memory `dashboard-chart-no-overlap.md`). IBKR Desktop = execution layer (live account; staged brackets; Quick Trade buttons for scale-outs). IBKR MCP connector = account-data and staging path (Claude runtime only, D-014). IB Gateway installed as fallback. Multi-monitor: TV main screen, IBKR Desktop secondary, future TUI tertiary.

## Constraints

- Live account. Never auto-fire orders (D-003). Never propose trades or give buy/sell advice.
- Dave is an experienced trader running a hedged book — no beginner framing.
- No web framework, no database in v1 (SQLite optional in v2).
- MCP tools callable only from Claude sessions; standalone Python takes account data as inputs (D-014).
- Existing working code (`pm_pdf_to_pine.py` + dated Pine scripts, in daily use since 2026-06-16) lives outside this folder until its migration sprint.

============================================================
FILE: planning/RISKS.md
============================================================

# Risks

Known project risks and mitigation notes. Sprint 002-relevant risks first.

---

| # | Risk | Likelihood | Impact | Mitigation | Status |
|---|---|---:|---:|---|---|
| R-001 | Sizing math error on live capital (wrong tier %, rounding up instead of down, stop-distance sign error) | Low | Critical | D-009 raised validation bar: exhaustive pytest matrix on `risk_math` (zero/negative stop distance, float boundaries, hard-cap binding, both directions); `Decimal` for money math; floor-to-whole-share rounding; loud failure over silent wrong answer | Open — governs Sprint 002 acceptance |
| R-002 | Stale or wrong NLV input → sizes computed against wrong equity | Medium | High | NLV is an explicit input (flag or snapshot file) with a timestamp; CLI warns when snapshot is older than a configurable threshold (default 1 hour); output always echoes the NLV used | Open — Sprint 002 |
| R-003 | Concentration check misses an existing position in the same symbol | Medium | Medium | Existing-position value is an explicit input; conversational flow instructs Claude to fetch positions before invoking; CLI output states what existing-position value was assumed (including zero) | Open — Sprint 002 |
| R-004 | PDF format drift / Adam's apostrophe typos silently drop tickers | Medium | High | Already bitten once (patched for 2026-07-01). Formal fixture-based test harness lands with the parser-migration sprint; until then Dave eyeballs ticker count vs the PDF each morning | Open — parser sprint |
| R-005 | iCloud sync conflict or partial sync corrupts planning files / code between devices | Medium | Medium | D-006 discipline (update STATE.md, let sync settle); D-007 GitHub as the real safety net once the repo exists; keep "Optimize Mac Storage" off for the project path | Open |
| R-006 | IBKR MCP connector outage breaks the conversational data path | Low | Medium | Manual fallback: Dave reads NLV/positions off IBKR Desktop and passes them as CLI flags — the calculator works with zero connectivity. IB Gateway is the deeper fallback (D-014) | Mitigated by design |
| R-007 | Scope creep: sizing sprint grows loss budgets, staging, or TUI features | Medium | High | D-012/D-013 boundaries; acceptance includes an out-of-scope check (no MCP calls, no order code, no budget math in `src/`) | Open — Builder discipline |
| R-008 | Confusion bleed from abandoned May 2026 repo or the old April "study companion" project instructions | Low | Medium | D-015 explicitly kills the old repo; project instructions rewritten 2026-07-01 to point at this folder | Mitigated |
| R-009 | Loss-cap enforcement remains manual until the ledger sprint ships | High | Medium | Known, accepted gap (D-012). Dave enforces daily/weekly/monthly caps by discipline in the interim; ledger sprint is next in queue after 002 | Accepted interim |

============================================================
FILE: planning/QUESTIONS.md
============================================================

# Open Questions

Questions that need answers from Dave or a future sprint. Answered items move to DECISIONS.md.

---

| # | Question | Owner | Needed By | Status | Answer / Notes |
|---|---|---|---|---|---|
| Q-001 | Canonical GitHub repo URL for `bsl-coach` | Dave | Before Sprint 002 completion | **Answered 2026-07-01** | `https://github.com/Holmesnett/bsl-coach.git` — recorded in D-007 |
| Q-002 | TUI dashboard framework: `rich` (simple periodic refresh) vs `textual` (event-driven, interactive) | Dave + Architect | TUI sprint design | Open | Decide fresh against MCP-data realities; May-repo `textual` experience is NOT a precedent (D-015) |
| Q-003 | BSL course materials corpus: which materials, what format, how indexed for Builder context? | Dave | Parser-migration sprint | Open | PDFs / transcripts / notes into `references/client-docs/` |
| Q-004 | Discord volume: does Humbled Trader Discord setup flow warrant a v2 webhook receiver? | Dave | v2 planning | Open | Paste-based intake stands (D-004) until volume proves otherwise |
| Q-005 | Pine push automation: is `pbcopy` + paste sufficient long-term, or explore Claude-in-Chrome automation in v2? | Dave | v2 planning | Open | D-005 stands for v1 |
| Q-006 | Post-Dec-9-2026 lockup review: do the %-based caps still feel right at $10M+ NLV? | Dave | 2026-12-09 | Scheduled | D-002 anticipates auto-scaling; human confirmation required |
| Q-007 | Ledger sprint design: exact trade-tagging mechanics off `get_account_trades` (partial fills, options legs, symbol re-entry across the cutoff) | Architect | Sprint 003 design | Open | The daily/weekly/monthly budget checks (D-012 deferral) depend on this |
| Q-008 | BSL expansion naming: intake says "Buy-Support / Sell-Resistance"; earlier project documentation derived "Back Side Long" from the course title. Cosmetic, but docs should be consistent | Dave | Whenever convenient | Open | Zero functional impact; code says "BSL" everywhere |
| Q-009 | Snapshot-freshness threshold: is the 1-hour default stale-NLV warning (R-002) right for live mornings? | Dave | During Sprint 002 live use | Open | Tune from real use; config value, not code change |

============================================================
FILE: planning/FILE_INVENTORY.md
============================================================

# File Inventory

Snapshot as of Architect Pack 001 apply (2026-07-01). Maintained at sprint boundaries.

---

```
bsl-coach/
├── AGENTS.md                       # roles, rules, sprint workflow
├── README.md                       # scaffold readme
├── project-start.md                # scaffold quickstart
├── architect-chat-starter-prompt.md# intake + pack rules (source for this pack)
├── .120x/method-manifest.json
├── docs/
│   ├── ARCHITECTURE.md             # v1 system shape (this pack)
│   ├── API.md                      # placeholder
│   ├── RIGOR_PROFILE.md            # Micro-app profile; amended by D-009 (hybrid)
│   └── VALIDATION.md               # validation approach (this pack)
├── planning/
│   ├── ARCHITECT_BRIEFING.md       # 2026-07-02 handoff from outgoing Architect
│   ├── STATE.md                    # (this pack)
│   ├── DECISIONS.md                # D-001..D-015 (this pack)
│   ├── DOMAIN.md                   # (this pack)
│   ├── RISKS.md                    # R-001..R-009 (this pack)
│   ├── QUESTIONS.md                # Q-001..Q-009 (this pack)
│   ├── FILE_INVENTORY.md           # (this file)
│   ├── INTAKE.md                   # original intake capture
│   ├── STATUS.json                 # (this pack)
│   ├── memory/                     # mirrored Cowork memory (reference, not doctrine)
│   │   ├── README.md
│   │   ├── dashboard-chart-no-overlap.md
│   │   ├── execution-stack.md
│   │   ├── ibkr-claude-connector.md
│   │   └── risk-framework.md
│   ├── architect-packs/
│   │   ├── README.md
│   │   └── architect-pack-001-discovery.md
│   └── sprints/
│       ├── 001-discovery-architecture/   # discovery record (this pack)
│       └── 002-position-sizing-calculator/  # ACTIVE sprint (this pack)
├── references/
│   ├── client-docs/                # PM Planning PDFs + course materials to be filed (Q-003)
│   ├── source-app/                 # destination for pm_pdf_to_pine.py at migration sprint
│   └── platform/
├── samples/                        # test fixtures land here in Sprint 002
├── scripts/
│   ├── apply-architect-pack.js
│   └── update-method.js
├── src/                            # EMPTY until Sprint 002 Builder work
├── templates/
└── tests/                          # pytest lands here in Sprint 002
```

## Code outside this folder (known, pending migration)

- `pm_pdf_to_pine.py` — working PDF→Pine parser, daily use since 2026-06-16, in a separate Cowork outputs directory on the MacBook Pro.
- `bsl_pm_watchlist_YYYY-MM-DD.pine` — generated dated Pine scripts.

============================================================
FILE: planning/STATUS.json
============================================================

{
  "schemaVersion": 1,
  "phase": "build",
  "sprint": "002-position-sizing-calculator",
  "updated": "2026-07-01"
}

============================================================
FILE: planning/sprints/001-discovery-architecture/requirements.md
============================================================

# Sprint 001 Requirements — Discovery / Architecture

## Goal

Turn intake context into Builder-ready planning artifacts: populated planning files, recorded decisions, risk register, open questions, and a fully specified first implementation sprint.

## Scope

- Digest the intake (`architect-chat-starter-prompt.md`) and the outgoing Architect's handoff (`planning/ARCHITECT_BRIEFING.md`).
- Resolve the two open handoff questions with Dave: MVP slice and rigor tier.
- Confirm the eight informal agreements and record them as decisions.
- Specify Sprint 002 end-to-end (requirements, blueprint, acceptance, handoff prompt).

## Out of scope

- Any application code.
- Migrating the existing parser into `src/`.

============================================================
FILE: planning/sprints/001-discovery-architecture/blueprint.md
============================================================

# Sprint 001 Blueprint — Discovery / Architecture

Discovery ran as a conversation between Dave and the Architect (Fable 5 in Cowork) on 2026-07-01, resuming the outgoing Architect's (Claude Opus 4.7) two-day intake.

Resolved in conversation:

1. **MVP slice** → position sizing calculator (D-010), over parser hardening and the observability TUI.
2. **Rigor tier** → hybrid: Micro-app speed, raised validation on money-touching code (D-009).
3. **Interface** → CLI core + conversational wrapper (D-011).
4. **Check scope** → tiers + hard cap + concentration only; loss budgets deferred to the ledger sprint (D-012).
5. **Output** → numbers only; no order staging (D-013).
6. All eight informal agreements confirmed as-is → D-001 through D-008.
7. Housekeeping: single canonical folder established at `~/Documents/Claude/Projects/bsl-coach`; duplicate Cowork project eliminated; project renamed "BSL Coach"; project instructions rewritten to point at this folder; May 2026 repo abandoned (D-015).

The output of this sprint is Architect Pack 001 (this pack).

============================================================
FILE: planning/sprints/001-discovery-architecture/acceptance.md
============================================================

# Sprint 001 Acceptance — Discovery / Architecture

- [x] planning/DOMAIN.md populated (no TBD placeholders remain in required sections)
- [x] planning/DECISIONS.md records D-001..D-015 including the two handoff questions and all eight informal agreements
- [x] planning/RISKS.md and planning/QUESTIONS.md populated
- [x] Sprint 002 fully specified: requirements, blueprint, acceptance, handoff prompt
- [x] docs/ARCHITECTURE.md and docs/VALIDATION.md written for the v1 shape
- [x] No application code written

Sprint 001 completes when this pack is applied and Dave has reviewed the generated files.

============================================================
FILE: planning/sprints/001-discovery-architecture/handoff-prompt.md
============================================================

# Sprint 001 Handoff — Discovery / Architecture

Discovery is complete; this sprint produced planning artifacts only. There is nothing for a Builder to implement here.

Builders: proceed to `planning/sprints/002-position-sizing-calculator/` and read all four files before writing any code.

============================================================
FILE: planning/sprints/002-position-sizing-calculator/requirements.md
============================================================

# Sprint 002 Requirements — Position Sizing Calculator

## Why (business goal)

Position sizing is currently hand math under time pressure minutes before the open, against a live ~$3.9M account. A wrong size is the single most expensive mistake this project can prevent. This sprint ships a tested calculator that turns (symbol, direction, entry, stop, conviction tier, NLV, existing exposure) into an exact share count with every cap checked.

## What

A Python package `bsl_coach` in `src/` providing:

1. **Pure risk math** (`risk_math` module): tier → risk dollars, risk dollars + stop distance → share count, cap checks. No I/O, no network, no MCP. All money math in `Decimal`.
2. **CLI** (`bsl-size`): computes and prints a sizing result. Example invocation (final flag names are Builder's choice, semantics are not):

   `bsl-size NOW --direction long --entry 105.57 --stop 104.59 --tier base --nlv 3890000 --existing-value 0`

3. **Account snapshot file** (optional input): `data/account_snapshot.json` holding `{nlv, positions: {symbol: market_value}, as_of}` — written by a Claude session (via IBKR MCP) or by hand. When present and fresh, `--nlv`/`--existing-value` may be omitted. Stale snapshot (default > 1h) triggers a prominent warning, not silent use.
4. **Conversational recipe** (`docs/`): a short documented flow for Claude sessions — fetch NLV + positions via the IBKR MCP connector, refresh the snapshot file, run the CLI, relay the result. The Python never calls MCP itself (D-014).

## Functional requirements

- FR-1: Tier mapping per DOMAIN.md: base 0.10% / medium 0.15% / high 0.20% / max 0.25% of NLV.
- FR-2: Risk dollars = min(tier% × NLV, $50,000 hard cap). Output states when the hard cap binds.
- FR-3: Share count = floor(risk dollars ÷ per-share stop distance). Whole shares only, always rounded down.
- FR-4: Long: stop must be strictly below entry. Short: stop strictly above entry. Anything else (including equality) is a hard input error — non-zero exit, no numbers output.
- FR-5: Concentration check: (shares × entry) + existing same-symbol position value must not exceed 5% of NLV. When exceeded, reduce shares to the largest count that passes, and report both the capped and uncapped figures with the binding constraint named.
- FR-6: Zero computed shares (stop too tight × price too high for the risk budget) is a loud, explicit "no viable size" result — never silently output 0 as if tradeable.
- FR-7: Output (human-readable and `--json`): shares, position value, dollar risk, risk as % of NLV, concentration %, NLV used and its source/age, every check with pass/capped/fail, and the binding constraint.
- FR-8: Works completely offline via flags — no account connectivity required (R-006 fallback path).

## Out of scope (hard boundaries)

- Daily/weekly/monthly loss-budget checks and the Active-vs-Legacy ledger (D-012 — next sprint).
- Order staging / any `create_order_instruction` or MCP integration in Python code (D-013, D-014).
- PDF parser migration, Pine Script changes, TUI, alerts.
- Any auto-derivation of conviction tier — the tier is always Dave's input (two-vote rule is human).

## Rigor

D-009 applies in full: this is money-touching code. The acceptance test matrix is mandatory, not aspirational.

============================================================
FILE: planning/sprints/002-position-sizing-calculator/blueprint.md
============================================================

# Sprint 002 Blueprint — Position Sizing Calculator

## Package layout

```
src/bsl_coach/
  __init__.py          # __version__
  risk_math.py         # pure functions + SizingResult dataclass (Decimal throughout)
  snapshot.py          # read/validate data/account_snapshot.json, staleness check
  cli.py               # argparse entrypoint `bsl-size`
tests/
  test_risk_math.py    # the D-009 matrix (bulk of the sprint's test weight)
  test_snapshot.py     # missing/stale/malformed snapshot handling
  test_cli.py          # flag parsing, exit codes, --json shape, offline path
samples/
  account_snapshot.example.json
pyproject.toml         # package metadata + bsl-size entry point
README.md              # extend scaffold README: install, usage, conversational recipe pointer
docs/SIZING_RECIPE.md  # conversational flow for Claude sessions (MCP fetch → snapshot → CLI)
```

## Design rules

- `risk_math.py` is pure: `(direction, entry, stop, tier, nlv, existing_value) → SizingResult`. Raises typed exceptions (`InvalidStopError`, `InvalidInputError`) on bad input. No prints, no file access.
- All prices/values parsed to `Decimal` at the boundary; floats never touch money math. Share count is `int`.
- `SizingResult` carries: `shares`, `position_value`, `risk_dollars`, `risk_pct_of_nlv`, `concentration_pct`, `checks` (per-check status: pass / capped / fail), `binding_constraint`, `warnings`.
- Tier table and caps (50_000 hard cap, 5% concentration, tier percentages) live as named constants in one place with a comment pointing at DOMAIN.md.
- Precedence when constraints collide: hard cap trims risk dollars first (FR-2), then concentration trims shares (FR-5). The tighter result always wins; `binding_constraint` names it.
- CLI exit codes: 0 = sized OK (including capped), 2 = invalid input, 3 = no viable size, 4 = snapshot problem when snapshot was the selected source.
- Snapshot schema: `{"schema": "bsl-snapshot-1", "as_of": "<UTC ISO8601 Z>", "nlv": <number>, "positions": {"SYM": <market_value>}}`. Versioned for future migration.
- Explicit flags always override snapshot values; the output must say which source supplied NLV.

## Worked reference examples (encode these as tests)

At NLV $4,000,000:

- Base tier → risk $4,000. NOW long, entry 105.57, stop 104.59 (distance 0.98) → floor(4000/0.98) = 4,081 shares; position value $430,832 ≈ 10.8% of NLV → concentration caps shares to floor(200,000/105.57) = 1,894 shares (binding constraint: concentration).
- Max tier at NLV $30,000,000 → tier risk $75,000 → hard cap trims to $50,000 (binding constraint: hard cap).
- Long with stop ≥ entry → `InvalidStopError`, exit 2.
- Risk $4,000, stop distance $0.005 on a $1,400 stock → shares floor fine; risk $4,000, entry $1,400, stop distance $800 → floor(4000/800) = 5 shares — verify no float wobble at boundaries (use cases like distance 0.98 vs 0.9800000001).
- Existing NOW position value $150,000 at 5% cap $200,000 → only $50,000 of new position value allowed.

## Edge cases the test matrix must cover (D-009)

Zero stop distance; negative distance (stop crosses entry, both directions); equality; zero/negative/absent NLV; zero computed shares (FR-6); floor boundaries (risk exactly divisible vs off-by-a-penny); hard cap exactly at tier boundary; concentration exactly at 5%; existing position alone already ≥ 5%; penny-priced symbol vs $1,400 symbol; `--json` output parses and matches human output; stale snapshot warning fires at threshold; malformed snapshot fails loudly.

## What the Builder must NOT do

No MCP calls, no `ib_insync`, no network I/O anywhere in `src/`. No order construction. No loss-budget math. No tier auto-suggestion. No TUI. Grep-able guard: the strings `create_order_instruction`, `ib_insync`, and `mcp__` must not appear in `src/`.

============================================================
FILE: planning/sprints/002-position-sizing-calculator/acceptance.md
============================================================

# Sprint 002 Acceptance — Position Sizing Calculator

A sprint-complete claim requires every item below.

- **A-001** — `pytest` green with the full D-009 matrix implemented: every edge case listed in the blueprint has at least one test; the worked reference examples are encoded exactly.
- **A-002** — Worked example check: at NLV $4,000,000, base tier, NOW long 105.57/stop 104.59 returns 1,894 shares with concentration named as binding constraint (per blueprint math).
- **A-003** — Hard cap: max tier at NLV $30,000,000 sizes off $50,000 risk, hard cap named as binding.
- **A-004** — Direction safety: long with stop ≥ entry and short with stop ≤ entry both exit 2 with a clear message and no sizing output.
- **A-005** — No-viable-size path (FR-6) exits 3 with an explicit message; never prints 0 shares as a tradeable result.
- **A-006** — Offline path: a fully-flagged invocation with no snapshot file present succeeds with no network access.
- **A-007** — Snapshot path: fresh snapshot supplies NLV/existing-value; stale snapshot (> threshold) still computes but with a prominent warning naming the age; malformed snapshot exits 4.
- **A-008** — Out-of-scope guard: `create_order_instruction`, `ib_insync`, and `mcp__` appear nowhere in `src/` (grep check documented or scripted).
- **A-009** — `--json` output is valid JSON and semantically matches the human-readable output for the same inputs.
- **A-010** — README + `docs/SIZING_RECIPE.md`: Dave can install and run a first sizing in under 5 minutes; the conversational recipe documents the Claude-fetches-NLV flow end to end.
- **A-011** — Live smoke test (Dave drives): one real morning sizing against live NLV (via the conversational recipe or manual flags), result sanity-checked against hand math. Sign-off recorded in STATE.md.

============================================================
FILE: planning/sprints/002-position-sizing-calculator/handoff-prompt.md
============================================================

# Sprint 002 Builder Handoff — Position Sizing Calculator

You are the Builder for BSL Coach Sprint 002. Read, in order: `AGENTS.md`, `planning/STATE.md`, `planning/DECISIONS.md`, `planning/DOMAIN.md`, then all four files in `planning/sprints/002-position-sizing-calculator/`. Implement from the sprint files only.

Build the position sizing calculator exactly as specified: pure `risk_math` core (Decimal money math), `bsl-size` CLI, optional snapshot-file input, pytest matrix per the blueprint's edge-case list.

Hard rules:

- This code informs live-money decisions on a ~$3.9M account. The blueprint's test matrix is mandatory (D-009). Do not ship untested money math.
- NO MCP calls, NO `ib_insync`, NO network I/O in `src/`. Account data arrives via CLI flags or the snapshot file (D-014).
- NO order staging or order construction of any kind (D-013).
- NO loss-budget / ledger logic (D-012 — next sprint).
- Never auto-derive the conviction tier; it is always an input.
- Prefer boring, local, file-based Python. No new dependencies beyond stdlib + pytest unless you document why.
- Do not touch `planning/memory/`, `references/`, or the parser living outside this folder.

Definition of done: acceptance A-001 through A-010 verified by you with commands documented; A-011 (live smoke test) is Dave's, flagged as awaiting sign-off. Then update `planning/STATE.md`, `planning/FILE_INVENTORY.md`, and record any new decisions in `planning/DECISIONS.md` with the next D-number, plus `docs/ARCHITECTURE.md` if the shape changed.

============================================================
FILE: docs/ARCHITECTURE.md
============================================================

# Architecture — BSL Coach v1

## Shape

Local, file-based Python on macOS. No web framework, no database, no daemon. Three layers:

1. **Claude runtime (Cowork / Claude sessions)** — the only place MCP tools exist. Fetches live account data via the IBKR MCP connector, refreshes `data/account_snapshot.json`, invokes CLIs, relays results. Later sprints: stages orders via `create_order_instruction` (human-transmitted always, D-003).
2. **Pure Python (`src/bsl_coach/`)** — testable logic with zero network access (D-014). Sprint 002: `risk_math`, `snapshot`, `cli`. Later sprints add: parser (migrated `pm_pdf_to_pine.py`), ledger/tagging tracker, TUI dashboard.
3. **External surfaces** — TradingView (Pine scripts via `pbcopy`), IBKR Desktop (manual execution; Review Instructions tab for staged orders), iCloud (folder sync), GitHub (version control).

## Data flow (Sprint 002 slice)

PM PDF → (existing external parser) → Pine script → TradingView charts. In parallel: Claude fetches NLV + positions → snapshot file → `bsl-size` → share count + cap checks → Dave builds the bracket in IBKR Desktop manually.

## Key boundaries

- MCP-callable code and pure Python never mix (D-014). The snapshot file is the interface between them.
- The risk framework's constants live in one module, documented against `planning/DOMAIN.md`.
- Execution is always human (D-003). Nothing in this codebase transmits an order.

## Future (per roadmap, not yet authorized)

Sprint 003 (likely): Active-vs-Legacy ledger tracker off `get_account_trades` + D-001 cutoff → enables daily/weekly/monthly loss-budget checks. Then: parser migration with fixture tests; observability TUI (framework per Q-002); order staging integration.

============================================================
FILE: docs/VALIDATION.md
============================================================

# Validation — BSL Coach

## Rigor model (D-009)

Micro-app rigor everywhere except money-touching code. Money-touching = anything computing position sizes, stop distances, risk dollars, cap checks, budget consumption, or NLV math. That code gets a mandatory test matrix: happy paths AND edge cases (zero/negative stop distance, entry crossing stop, share-count floor boundaries, hard-cap and concentration boundaries, absent/stale account data). Non-money code (CLI plumbing, file handling, docs) gets happy-path plus the failure modes that would lose data.

## Sprint 002 validation

- `python3 -m pytest` — full suite green is the gate.
- Money math in `Decimal`; tests include float-wobble boundary cases.
- Out-of-scope guard: grep `src/` for `create_order_instruction`, `ib_insync`, `mcp__` — zero hits.
- A-011 live smoke test: Dave runs one real-morning sizing and checks it against hand math before the calculator is trusted in the daily workflow.

## Standing rules

- A failing or missing test on money math blocks sprint completion — no exceptions.
- Every acceptance item maps to a command or a documented manual check.
- Validation behavior changes get recorded here at each sprint boundary.
