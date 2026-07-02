# File Inventory

Snapshot as of Sprint 003 Builder completion (2026-07-01). Maintained at sprint boundaries.

---

```
bsl-coach/
├── AGENTS.md                       # roles, rules, sprint workflow
├── README.md                       # scaffold readme + Sprint 002/003 Quick Starts
├── pyproject.toml                  # package metadata; bsl-size + bsl-ledger entry points
├── .gitignore                      # excludes real snapshots + registry, pycache, .DS_Store
├── project-start.md                # scaffold quickstart
├── architect-chat-starter-prompt.md# intake + pack rules
├── .120x/method-manifest.json
├── docs/
│   ├── ARCHITECTURE.md             # v1 system shape (updated at each pack)
│   ├── API.md                      # placeholder
│   ├── RIGOR_PROFILE.md            # Micro-app profile; amended by D-009 (hybrid)
│   ├── SIZING_RECIPE.md            # conversational MCP→snapshot→CLI flow (Sprint 002)
│   ├── LEDGER_RECIPE.md            # conversational MCP→snapshots→bsl-ledger flow (Sprint 003)
│   └── VALIDATION.md               # validation approach + sprint commands
├── planning/
│   ├── ARCHITECT_BRIEFING.md       # 2026-07-02 handoff from outgoing Architect
│   ├── STATE.md
│   ├── DECISIONS.md                # D-001..D-022
│   ├── DOMAIN.md
│   ├── RISKS.md
│   ├── QUESTIONS.md
│   ├── FILE_INVENTORY.md           # (this file)
│   ├── INTAKE.md                   # original intake capture
│   ├── STATUS.json
│   ├── memory/                     # mirrored Cowork memory (reference, not doctrine)
│   ├── architect-packs/
│   │   ├── README.md
│   │   ├── architect-pack-001-discovery.md
│   │   └── architect-pack-002-ledger.md
│   └── sprints/
│       ├── 001-discovery-architecture/       # discovery record
│       ├── 002-position-sizing-calculator/   # CLOSEOUT.md (A-011 pending)
│       └── 003-active-bsl-ledger/            # CLOSEOUT.md (A-011 pending)
├── references/
│   ├── client-docs/                # PM Planning PDFs + course materials (Q-003)
│   ├── source-app/                 # destination for pm_pdf_to_pine.py at migration sprint
│   └── platform/
├── samples/
│   ├── account_snapshot.example.json   # bsl-snapshot-1 (now incl. optional available_funds)
│   ├── trades_snapshot.example.json    # bsl-trades-1 example (Sprint 003)
│   └── bsl_registry.example.json       # bsl-registry-1 example (Sprint 003)
├── scripts/
│   ├── apply-architect-pack.js
│   └── update-method.js
├── src/
│   └── bsl_coach/                  # pure Python, stdlib-only, no network
│       ├── __init__.py             # __version__
│       ├── risk_math.py            # Decimal tier/cap math (Sprint 002)
│       ├── snapshot.py             # bsl-snapshot-1 read/validate + staleness (+available_funds)
│       ├── cli.py                  # bsl-size CLI (exit 0/2/3/4) + --register
│       ├── registry.py             # bsl-registry-1 load/save/tag/untag (Sprint 003, D-018)
│       ├── trades.py               # bsl-trades-1 ingest, UTC→ET, dedupe (Sprint 003, D-021)
│       ├── ledger.py               # episodes, ET buckets, budgets (money-touching, D-009)
│       └── cli_ledger.py           # bsl-ledger CLI (report/tag/untag/list; exit 0/4/5)
├── templates/
└── tests/                          # 202 tests (81 Sprint 002 + 121 Sprint 003)
    ├── fixtures/
    │   └── now_2026_07_01_fills.json  # ground-truth NOW fixture (+$458.61, R-011)
    ├── test_risk_math.py           # D-009 matrix + worked reference examples
    ├── test_snapshot.py            # missing/stale/malformed handling
    ├── test_cli.py                 # bsl-size flags, exit codes, --json
    ├── test_registry.py            # registry round trip, ET dates, malformed entries
    ├── test_trades.py              # ET/DST conversion, parse, dedupe, staleness
    ├── test_ledger.py              # D-009 matrix: matching/episodes/buckets/budgets
    ├── test_cli_ledger.py          # report/exit codes/--json parity/tag-untag/--register
    └── test_guardrails.py          # scripted A-008 grep across all 7 modules
```

Not committed (git-ignored): `data/account_snapshot.json`,
`data/trades_snapshot.json`, `data/bsl_registry.json` — real account data,
written per `docs/SIZING_RECIPE.md` / `docs/LEDGER_RECIPE.md`.

## Code outside this folder (known, pending migration)

- `pm_pdf_to_pine.py` — working PDF→Pine parser, daily use since 2026-06-16, in a separate Cowork outputs directory on the MacBook Pro.
- `bsl_pm_watchlist_YYYY-MM-DD.pine` — generated dated Pine scripts.
