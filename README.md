# BSL Coach

**Client:** Hudson Mac Cayman Holding Company  
**Description:** Daily pre-market automation pipeline that turns Adam Raposa's Pre-Market Planning PDF into TradingView-ready Pine Scripts, risk-adjusted position sizes, and cleanly separated Active BSL vs Legacy Portfolio P&L, for a solo high-net-worth trader executing BSL (Buy-Support / Sell-Resistance) setups.  
**Project type:** Workflow automation  
**Tech stack:** - Python 3 (parsers, position size calculator, P&L tracker, TUI dashboard)- pdfplumber (PDF ingestion for Adam Raposa's Pre-Market Planning PDFs)- Pine Script v5 (TradingView chart indicators; script transfer via `pbcopy` + paste)- IBKR MCP connector (via claude.ai IBKR AI Instructions feature — provides `get_account_summary`, `get_account_positions`, `get_account_orders`, `get_account_trades`, `get_price_snapshot`, and `create_order_instruction` for staged bracket orders)- IB Gateway (installed and running for API access; historical fallback path if the MCP connector goes down)- Python `rich` or `textual` for the persistent Terminal UI dashboard (framework choice TBD)- Git + private GitHub repo `bsl-coach` for version control- Local files + iCloud Drive for cross-device workspace folder sync between MacBook Pro and Mac Studio- Fable 5 (Anthropic coding-focused agent) as the Builder / code-execution layer, orchestrated from Claude in Cowork as the Architect- Cowork runtime on macOS- No web framework, no database in v1 (SQLite optional in v2 if trade-history persistence is needed beyond IBKR's own record)

---

## Quick Start — Position Sizing Calculator (Sprint 002)

The first shipped tool: `bsl-size`, a risk-based position sizing CLI.
Numbers only — it never stages or transmits orders.

### Install

Stdlib-only at runtime; pytest for tests. Either run in place:

```bash
cd ~/Documents/Claude/Projects/bsl-coach
PYTHONPATH=src python3 -m bsl_coach.cli --help
```

or install editable to get `bsl-size` on PATH:

```bash
pip install -e .
bsl-size --help
```

### First sizing (offline, all flags)

```bash
PYTHONPATH=src python3 -m bsl_coach.cli NOW \
  --direction long --entry 105.57 --stop 104.59 --tier base \
  --nlv 3890000 --existing-value 0
```

Output: exact share count, position value, dollar risk, concentration %,
every cap check (hard $50K cap, 5% concentration), and the binding
constraint. Add `--json` for machine-readable output.

Tiers (per `planning/DOMAIN.md`): `base` 0.10% / `medium` 0.15% /
`high` 0.20% / `max` 0.25% of NLV. The tier is always your input — never
derived.

### With live account data

A Claude session fetches NLV + positions via the IBKR MCP connector and
writes `data/account_snapshot.json` (see `samples/account_snapshot.example.json`);
then `--nlv`/`--existing-value` can be omitted. Full flow:
**`docs/SIZING_RECIPE.md`**. Snapshots older than 60 minutes trigger a loud
staleness warning. Real snapshots are git-ignored.

### Tests

```bash
PYTHONPATH=src python3 -m pytest
```

The risk math carries a mandatory edge-case matrix (D-009) — money-touching
code is never shipped untested.

---

## Purpose

This project folder was created by the 120x Project Launcher for the 120x Architect / Builder workflow.

It is ready for project-specific discovery and architecture planning.

---

## Project Metadata

| Field | Value |
|---|---|
| Project name | BSL Coach |
| Client name | Hudson Mac Cayman Holding Company |
| Project slug | bsl-coach |
| One-sentence description | Daily pre-market automation pipeline that turns Adam Raposa's Pre-Market Planning PDF into TradingView-ready Pine Scripts, risk-adjusted position sizes, and cleanly separated Active BSL vs Legacy Portfolio P&L, for a solo high-net-worth trader executing BSL (Buy-Support / Sell-Resistance) setups. |
| Project type | Workflow automation |
| Planning folder | bsl-coach/ |
| Implementation repo | Downloaded project folder |
| Canonical GitHub repo | UNKNOWN — Dave to create private GitHub repo `bsl-coach` under his personal account or the Hudson Mac Cayman org; URL to be added to this intake once created. |
| Tech stack | - Python 3 (parsers, position size calculator, P&L tracker, TUI dashboard)- pdfplumber (PDF ingestion for Adam Raposa's Pre-Market Planning PDFs)- Pine Script v5 (TradingView chart indicators; script transfer via `pbcopy` + paste)- IBKR MCP connector (via claude.ai IBKR AI Instructions feature — provides `get_account_summary`, `get_account_positions`, `get_account_orders`, `get_account_trades`, `get_price_snapshot`, and `create_order_instruction` for staged bracket orders)- IB Gateway (installed and running for API access; historical fallback path if the MCP connector goes down)- Python `rich` or `textual` for the persistent Terminal UI dashboard (framework choice TBD)- Git + private GitHub repo `bsl-coach` for version control- Local files + iCloud Drive for cross-device workspace folder sync between MacBook Pro and Mac Studio- Fable 5 (Anthropic coding-focused agent) as the Builder / code-execution layer, orchestrated from Claude in Cowork as the Architect- Cowork runtime on macOS- No web framework, no database in v1 (SQLite optional in v2 if trade-history persistence is needed beyond IBKR's own record) |

---

## Current Status

- Project folder created from the reusable 120x scaffold.
- Starter docs have been personalized from CLI metadata.
- No application code has been written yet.
- Next workflow step is Architect Pack 001 for discovery and architecture planning.

---

## Next Steps

1. Review `project-start.md`.
2. Open `architect-chat-starter-prompt.md`.
3. Start a new Architect chat.
4. Start Architect Pack 001 discovery.
5. Generate Architect Pack 001 only after explicit approval.
6. Save the Architect Pack in `planning/architect-packs/`.
7. Dry-run the importer.
8. Apply the Architect Pack after review.

Dry-run command shape:

`node scripts/apply-architect-pack.js planning/architect-packs/architect-pack-###-{sprint-name}.md --dry-run`

Apply command shape:

`node scripts/apply-architect-pack.js planning/architect-packs/architect-pack-###-{sprint-name}.md`

After a pack is applied, Builders implement from the generated sprint files under `planning/sprints/`, not directly from the Architect Pack.
