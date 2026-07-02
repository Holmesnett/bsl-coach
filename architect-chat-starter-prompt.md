# Architect Chat Starter Prompt

I am starting a new 120x Architect / Builder project.

Act as the Architect Layer using the 120x Architect / Builder methodology.

## Project Metadata

- Project name: BSL Coach
- Client: Hudson Mac Cayman Holding Company
- Project slug: bsl-coach
- Planning folder: bsl-coach/
- Implementation repo: Downloaded project folder
- Canonical GitHub repo: UNKNOWN — Dave to create private GitHub repo `bsl-coach` under his personal account or the Hudson Mac Cayman org; URL to be added to this intake once created.
- One-sentence description: Daily pre-market automation pipeline that turns Adam Raposa's Pre-Market Planning PDF into TradingView-ready Pine Scripts, risk-adjusted position sizes, and cleanly separated Active BSL vs Legacy Portfolio P&L, for a solo high-net-worth trader executing BSL (Buy-Support / Sell-Resistance) setups.
- Project type: Workflow automation
- Tech stack: - Python 3 (parsers, position size calculator, P&L tracker, TUI dashboard)- pdfplumber (PDF ingestion for Adam Raposa's Pre-Market Planning PDFs)- Pine Script v5 (TradingView chart indicators; script transfer via `pbcopy` + paste)- IBKR MCP connector (via claude.ai IBKR AI Instructions feature — provides `get_account_summary`, `get_account_positions`, `get_account_orders`, `get_account_trades`, `get_price_snapshot`, and `create_order_instruction` for staged bracket orders)- IB Gateway (installed and running for API access; historical fallback path if the MCP connector goes down)- Python `rich` or `textual` for the persistent Terminal UI dashboard (framework choice TBD)- Git + private GitHub repo `bsl-coach` for version control- Local files + iCloud Drive for cross-device workspace folder sync between MacBook Pro and Mac Studio- Fable 5 (Anthropic coding-focused agent) as the Builder / code-execution layer, orchestrated from Claude in Cowork as the Architect- Cowork runtime on macOS- No web framework, no database in v1 (SQLite optional in v2 if trade-history persistence is needed beyond IBKR's own record)

## Current Status

- The project folder has been created from the reusable 120x scaffold.
- No application code has been written yet.
- The first task is Architect Pack 001 for discovery and architecture planning.

## 120x Methodology Context

- Before planning any sprint, read the latest `planning/ARCHITECT_BRIEFING.md` if present (the operator will paste it). Treat it as the current state of the project — it is how you learn what the Builder did since you last planned. If it conflicts with your memory, the briefing wins.
- Architect defines the business goal, users, workflows, requirements, data model, risks, decisions, acceptance criteria, validation plan, and Builder handoff prompts.
- Builder executes from written artifacts.
- The handoff is a folder, not a conversation.
- The project folder is the durable source of truth.
- Every implementation sprint should include:
  - `requirements.md`
  - `blueprint.md`
  - `acceptance.md`
  - `handoff-prompt.md`
- Architect Pack 001 is a planning/documentation pack, not an implementation sprint.
- Do not write application code in Architect Pack 001.

## Optional Methodology Source References

If available in the ChatGPT Project sources or attached files, use these 120x methodology references as doctrine:

- `120x-architect-builder-philosophy.md`
- `120x-new-project-quickstart-v2.md`
- `120x-project-scaffold-instructions.md`
- `ARCHITECT_PACK_WORKFLOW.md`
- `templates/method/120x-architect-builder-method-starter.md`

Do not summarize those methodology files unless needed. Use them to keep the Architect Pack aligned with the 120x workflow.

## Source Material Folder Conventions

- `references/client-docs/` is for client documents, proposals, emails, meeting notes, and intake material.
- `references/source-app/` is for existing app, code, assets, exports, or source-system material.
- `references/platform/` is for platform notes, repo notes, hosting notes, and integration context.
- `samples/` is for sample data, exports, workbooks, fixtures, and generated examples.
- `docs/` is for durable technical documentation.
- `planning/` is for project state, decisions, domain context, risks, questions, file inventory, and sprint artifacts.

## Project Intake Context

Use the intake context below as the primary project context for Architect Pack 001.

If the intake is incomplete, do not invent details. Preserve unknowns in `planning/QUESTIONS.md` and label assumptions clearly.

### Who Will Use This App

Micro app

### Business Problem

Dave Holmes manages a live, complex trading book (~$4M NLV, 47 positions including multi-leg options structures) and takes discretionary swing trades based on the Buy-Support / Sell-Resistance ("BSL") methodology taught by Adam Raposa at humbledtrader.com. Each morning at 8:30 AM ET, Adam runs a live Pre-Market Planning ("PM Planning") call and publishes a PDF listing 7-10 watchlist tickers with Entry Key Level + Target 1 + Target 2, but no explicit stop losses. Currently Dave manually marks up TradingView charts, calculates position sizes by hand under time pressure right before market open, and has no separation between the mark-to-market swings of his 47-position legacy portfolio and the P&L generated by his active BSL trades — so risk-rule enforcement is unreliable because daily / weekly / monthly loss-cap triggers cannot distinguish portfolio drift noise from actual active-trading performance. Post-Dec-9 2026 SPCX lockup expiration, Dave's NLV scales to $10M+, amplifying every current workflow inefficiency.

### Primary Users / Roles

Solo operator: Dave Holmes, who is trader, analyst, and decision-maker for all positions and all trade execution. Adam Raposa appears in the data flow as an external source (PM Planning PDFs, BSL course materials) but is not a system user. The Humbled Trader Discord community appears as an informal source of BSL setups Dave may elect to take. All trade execution is manual — Dave reviews and confirms every order in IBKR Desktop.

### Current Workflow

- 8:30 AM ET: Attend Adam Raposa's live Pre-Market Planning call on humbledtrader.com
- ~8:45 AM ET: Receive PM Planning PDF listing 7-10 watchlist tickers with Entry / T1 / T2 Key Levels
- Manually open each ticker in TradingView and draw horizontal lines at the KLs (30-50 minutes total for the full watchlist)
- Manually determine a stop loss per ticker (Adam does not publish stops)
- Manually calculate position sizes on the fly before market open
- Monitor charts and price alerts through the session
- When a setup triggers, switch to IBKR Desktop and manually build a bracket order (Entry + Stop + T1/T2 as OCO)
- End of day / week: informally review trades with no formal split between Legacy portfolio MTM changes and Active BSL trade P&L
- In parallel: track additional BSL setups posted in the Humbled Trader Discord community, plus multi-day BSL setups Dave discovers through his own independent research — with no unified intake channel for these non-PDF sources

### Pain Points

- 30-50 minutes of manual chart markup each morning before market open; error-prone under time pressure
- No systematic conviction grading, so it is hard to size differently for high- vs low-conviction setups
- Position sizing math done by hand under time pressure right before open
- No live risk-budget enforcement; daily / weekly / monthly loss caps are enforced only by memory and discipline
- Legacy 47-position portfolio MTM noise contaminates the daily P&L signal, so risk rules keyed on P&L cannot fire on the right signal
- No cross-device continuity between MacBook Pro and Mac Studio (Cowork projects are stored per-machine with no cloud sync)
- No version control or persistent audit trail for the parser, Pine Scripts, or documentation
- No unified intake channel for non-PDF BSL setups (Discord community posts, Dave's own multi-day research)

### Target Workflow

- 8:30 AM ET: Adam Raposa's Pre-Market Planning call begins
- ~8:45 AM ET: PDF delivered to the Cowork project; Python parser (pdfplumber) extracts tickers, Entry KL, T1, T2, and conditional (inverse-scenario) setups
- Dave provides conviction tier (Base / Medium / High / Max / Pass) and stop price per ticker through a structured input in the Claude project chat
- Enhanced parser regenerates a dated Pine Script (`bsl_pm_watchlist_YYYY-MM-DD.pine`) with: Entry / T1 / T2 / Stop lines per ticker, approach alerts that fire when price nears any Entry KL, an on-chart sizing display driven by current NLV + per-ticker conviction tier + a 5% concentration cap, and a total-if-all-stops-hit sanity check against the daily risk cap
- Dave pastes the script into TradingView's Pine Editor (auto-copied via `pbcopy` on the local machine) → all charts are marked automatically as he flips tickers
- Non-PDF BSL setups (Discord posts, Dave's own multi-day research) are pasted into the Claude project chat in a one-line structured format and merged into the same parser flow, producing the same Pine Script + sizing artifacts
- When a setup approaches confirmation or an alert fires, Dave issues a command via project chat (e.g., "Stage a bracket order for NOW: buy 1500 at 106.02, stop 104.60, target 109.27"); Claude calls `create_order_instruction` via the IBKR MCP connector, which stages the bracket order in IBKR Desktop's Review Instructions tab
- Dave reviews the staged order in IBKR Desktop and clicks to actually transmit it — execution is always manual
- A persistent Terminal UI dashboard (Python + `rich` or `textual`) runs on Dave's secondary monitor showing: active positions with entry / stop / target / live P&L, daily / WTD / MTD Active BSL P&L, Legacy Portfolio MTM change, daily risk budget usage vs cap, open orders, and alerts firing — refreshes every 10-30 seconds via the IBKR MCP connector
- P&L is auto-tagged as Legacy (position opened before a cutoff date) vs Active BSL (opened on / after the cutoff, proposed 2026-07-01) using `get_account_trades` timestamps; risk framework caps apply to Active BSL only, not portfolio drift
- `state.md` in the shared iCloud workspace folder captures project state for cross-device handoff between MacBook Pro and Mac Studio; individual memory files (execution stack, risk framework, IBKR connector notes, dashboard-chart separation) are mirrored into the workspace so both machines' Cowork projects can read them
- All source code (parser, TUI dashboard, sizing calculator, Pine templates) is version-controlled in the private GitHub repo `bsl-coach`

### Source Materials

- Adam Raposa's daily Pre-Market Planning PDFs from humbledtrader.com (8:30 AM ET call)
- Humbled Trader Discord community BSL setup posts (paste-based intake in v1)
- Dave's own multi-day BSL research and discoveries (paste-based intake in v1)
- Adam Raposa's BSL course materials from humbledtrader.com (PDFs, notes, video transcripts) — provided by Dave as a reference corpus for Fable 5 build-time context and for future Claude sessions
- Dave's live IBKR account state via the IBKR MCP connector (positions, orders, trades, balances, price snapshots)
- TradingView chart interface as Pine Script destination
- 120x.ai Builder methodology as the project structure

### Systems / Tools Involved

- Cowork (Claude desktop app; project runtime — Architect layer)
- Fable 5 (Anthropic coding-focused agent — Builder layer, executes code work)
- Python 3 + pdfplumber (PDF parser)
- TradingView Pine Script v5 (chart markup; paste from clipboard via `pbcopy`)
- Interactive Brokers Desktop (order execution; live account with real capital)
- IB Gateway (installed and running for API access; historical fallback path)
- IBKR MCP connector (via claude.ai IBKR AI Instructions feature; enables `get_account_summary`, `get_account_positions`, `get_account_orders`, `get_account_trades`, `get_price_snapshot`, and `create_order_instruction`)
- Python `rich` or `textual` (Terminal UI dashboard framework — choice TBD)
- GitHub (private repo `bsl-coach`) for version control
- iCloud Drive (workspace folder sync across MacBook Pro and Mac Studio)
- Humbled Trader Discord (informal BSL setup source — copy/paste v1; no Discord MCP connector in Anthropic's vetted registry as of 2026-07-01)

### Data Inputs And Outputs

Inputs:
- Daily Pre-Market Planning PDF from Adam Raposa (structured watchlist)
- Discord community BSL setup posts (unstructured paste)
- Dave's own multi-day BSL research setups (unstructured paste)
- Live IBKR account data: real-time positions, orders, trades, balances, price snapshots
- Dave's per-ticker conviction grade (Base / Medium / High / Max / Pass) and stop price
- Account NLV (auto-fetched via IBKR MCP connector)
- Adam Raposa's BSL course materials (reference corpus for Fable 5 and future Claude sessions)

Outputs:
- Dated Pine Script files (`bsl_pm_watchlist_YYYY-MM-DD.pine`) with KLs, stops, conviction tiers, approach alerts, and on-chart sizing display
- Live-computed position size recommendations (shares, position value, risk in dollars, concentration check pass/fail, daily budget check pass/fail)
- Staged bracket orders in IBKR Desktop's Review Instructions tab (via `create_order_instruction`; never auto-fired)
- Persistent Terminal UI dashboard showing positions, P&L split (Legacy vs Active BSL), risk budget usage, open orders, alerts firing
- `state.md` snapshot of project state for cross-device continuity
- Individual memory files (execution stack, risk framework, IBKR connector notes) mirrored to the workspace folder for both-device access

### Out Of Scope For First Version

- Automated order placement or execution — Dave always executes manually in IBKR Desktop; the system may propose or stage orders via `create_order_instruction`, but never fires them
- ML-based signal generation or trade prediction — this project follows discretionary BSL setups from Adam Raposa, the Humbled Trader Discord community, or Dave's own research; no model training
- Managing the 47-position Legacy portfolio — Legacy positions are tracked as MTM baseline only; no active management by this project's tools
- Financial advisory or investment recommendations for Dave from Claude on live capital — Claude's built-in safety rules apply regardless of project scope

### Success Criteria

- Fully automated PDF → dated Pine Script pipeline (with conviction tiers, stops, on-chart sizing display, approach alerts); daily workflow requires zero manual chart markup
- Live position size calculator that reads NLV and open positions via the IBKR MCP connector, enforces the risk framework (0.10-0.25% per-trade tiers, 1% daily / 3% weekly / 5% monthly caps, 5% single-position concentration cap), and rejects trades that would violate caps
- Daily P&L tracker with clean Legacy vs Active BSL separation, so risk rules trigger on the active-trading signal only
- Cross-device portability via `state.md` + shared iCloud workspace folder; either Mac can pick up work without re-explaining context

### Open Questions

- Canonical GitHub repo URL — Dave to create the private repo `bsl-coach` and provide the URL for this intake
- Cutoff date for Legacy vs Active BSL P&L separation — proposed 2026-07-01 (day of first tagged BSL trade, $NOW); needs Dave's explicit confirmation
- TUI dashboard framework choice — `rich` (simpler, static-refresh dashboard) vs `textual` (more interactive, event-driven)
- Fable 5 model access and version confirmation in the current Cowork environment
- Post-Dec-9-2026 SPCX lockup: framework is %-based so should auto-scale from $4M to $10M+; explicit review at that point to confirm caps still feel appropriate at the new capital level
- Discord traffic volume — does BSL post volume from the Humbled Trader Discord warrant a v2 webhook receiver that watches specific channels and forwards new setups to the parser, or does paste-based intake remain sufficient?
- Pine Script push automation — TradingView has no public API and no MCP connector; is `pbcopy` + paste sufficient in v1, or is a Claude-in-Chrome automation path worth exploring in v2?
- BSL course materials scope and format — which materials will Dave provide (PDF course workbook, video transcripts, notes) and how should they be indexed for Fable 5 build-time reference?

## Rigor Profile

This profile is derived from the "Who will use this app?" intake answer. Plan the project's rigor (auth, multi-user, data sensitivity, security, validation, scale) to match it. The full profile is in the generated `docs/RIGOR_PROFILE.md`.

**Tier: Micro app.** Just me or a couple of trusted people; low stakes. Bias to the smallest thing that works.

Plan rigor to match this tier across access/auth, multi-user, data sensitivity, security, validation, and scale. See `docs/RIGOR_PROFILE.md` for the full profile.

- **Access / Auth:** Single user or a tiny trusted group. Auth optional or the simplest thing that works (a single login, a shared secret, or none if local-only). Do not build accounts, roles, or invites.
- **Multi-user / Tenancy:** None. Single-tenant, single-user assumptions are fine.
- **Data Sensitivity:** Assume no third-party PII. Local or simple storage is acceptable.
- **Security:** Standard hygiene only — no secrets in code, validate the obvious inputs. Skip threat modeling, rate limiting, and abuse prevention.
- **Validation & Tests:** Cover the happy path and the one or two failure modes that would lose the user's data. Do not over-test.
- **Scale:** Assume tiny. No caching, queues, or horizontal-scale design.
- **Plan For:** Speed to a working tool. Bias to the smallest thing that works.

## Mandatory Discovery Gate

Before creating Architect Pack 001, check whether the intake is complete enough to produce useful Builder-ready planning documents.

If any of the following are TBD, vague, missing, or unclear, do not create the Architect Pack yet:

- business problem
- primary users / roles
- current workflow
- pain points
- target workflow
- systems / tools involved
- data inputs and outputs
- out-of-scope boundaries
- success criteria
- MVP / smallest useful next sprint

### Tier-specific confirmation — Micro app

This is a **Micro-app** project (single or a few trusted users; low stakes). Before generating Architect Pack 001, CONFIRM the project is genuinely low-stakes — single/few trusted users, no sensitive third-party data, no public exposure. If any of those is false, **raise the tier** and re-plan rigor before producing the pack.

Instead, run a discovery brainstorm first.

The discovery brainstorm should:

- ask practical, targeted questions
- avoid overwhelming me
- group questions by business goal, workflow, users, data, success criteria, and MVP scope
- propose 2-3 possible project directions if the idea is vague
- help me choose the smallest useful first version
- preserve unknowns instead of inventing them
- challenge weak assumptions
- keep the project from becoming too broad

Do not generate the downloadable Architect Pack until I explicitly say one of the following:

- "Generate the pack"
- "Create the pack"
- "Make the Architect Pack"
- "Proceed with the pack"

If the intake is incomplete, your output should be a discovery conversation, not a file.

## Task

Begin the Architect Pack 001 process.

First, apply the Mandatory Discovery Gate.

If the intake is incomplete, run the discovery brainstorm and do not create the pack yet.

If the intake is complete enough and I have explicitly approved pack generation, create the downloadable Architect Pack file.

Save Architect Packs in `planning/architect-packs/`. The importer still runs from the project root with a relative pack path.

The pack should populate:

- `planning/STATE.md`
- `planning/DECISIONS.md`
- `planning/DOMAIN.md`
- `planning/RISKS.md`
- `planning/QUESTIONS.md`
- `planning/FILE_INVENTORY.md`
- `planning/sprints/001-discovery-architecture/requirements.md`
- `planning/sprints/001-discovery-architecture/blueprint.md`
- `planning/sprints/001-discovery-architecture/acceptance.md`
- `planning/sprints/001-discovery-architecture/handoff-prompt.md`
- `docs/ARCHITECTURE.md`
- `docs/API.md`, if useful
- `docs/VALIDATION.md`

## Builder-Ready Sprint Expectations

Any sprint created by Architect Pack 001 should be small enough for a Builder to execute from the folder without redefining scope.

The sprint artifacts should include:

- clear in-scope and out-of-scope boundaries
- requirements tied to the business goal
- a practical implementation blueprint
- acceptance criteria that can be checked
- validation expectations
- risks and open questions
- an exact Builder handoff prompt

## Architect Pack Output Requirement

Only after I explicitly say "Generate the pack," create a downloadable Markdown file named:

`architect-pack-001-discovery.md`

Do not paste the full Architect Pack into chat unless file creation is unavailable.

The file must be ready to use with:

`node scripts/apply-architect-pack.js planning/architect-packs/architect-pack-001-discovery.md --dry-run`

After dry-run review, it should be ready to apply with:

`node scripts/apply-architect-pack.js planning/architect-packs/architect-pack-001-discovery.md`

## Delimiter Rules

The Architect Pack must use this exact file section format:

```text
============================================================
FILE: relative/path/from/project-root.md
============================================================

File content goes here.
```

Important:

- Every separator line must be exactly 60 equals signs.
- Do not shorten the separator.
- Do not use markdown headings instead of `FILE:` sections.
- Do not wrap the entire Architect Pack in triple backticks.
- Do not include extra commentary inside the downloadable pack unless it belongs in a target file.

## Rules

- Do not write application code.
- Do not write application code in Architect Pack 001.
- Do not invent unknown facts.
- Use assumptions only when necessary and label them clearly.
- Keep first drafts practical and lightweight.
- Keep the MVP and next sprint practical.
- Create Builder-ready requirements, blueprint, acceptance criteria, and handoff prompt.
- Output should be ready for `scripts/apply-architect-pack.js`.
- After the pack is applied, Builders should implement from the generated files under `planning/sprints/`, not directly from the Architect Pack.
