# File Inventory

Snapshot as of Sprint 002 Builder completion (2026-07-01). Maintained at sprint boundaries.

---

```
bsl-coach/
├── AGENTS.md                       # roles, rules, sprint workflow
├── README.md                       # scaffold readme + Sprint 002 Quick Start
├── pyproject.toml                  # package metadata, bsl-size entry point (Sprint 002)
├── .gitignore                      # excludes real snapshots, pycache, .DS_Store
├── project-start.md                # scaffold quickstart
├── architect-chat-starter-prompt.md# intake + pack rules (source for this pack)
├── .120x/method-manifest.json
├── docs/
│   ├── ARCHITECTURE.md             # v1 system shape
│   ├── API.md                      # placeholder
│   ├── RIGOR_PROFILE.md            # Micro-app profile; amended by D-009 (hybrid)
│   ├── SIZING_RECIPE.md            # conversational MCP→snapshot→CLI flow (Sprint 002)
│   └── VALIDATION.md               # validation approach + Sprint 002 commands
├── planning/
│   ├── ARCHITECT_BRIEFING.md       # 2026-07-02 handoff from outgoing Architect
│   ├── STATE.md                    # (this pack)
│   ├── DECISIONS.md                # D-001..D-016
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
│       ├── 001-discovery-architecture/   # discovery record
│       └── 002-position-sizing-calculator/  # ACTIVE sprint + CLOSEOUT.md (A-011 pending)
├── references/
│   ├── client-docs/                # PM Planning PDFs + course materials to be filed (Q-003)
│   ├── source-app/                 # destination for pm_pdf_to_pine.py at migration sprint
│   └── platform/
├── samples/
│   └── account_snapshot.example.json  # bsl-snapshot-1 schema example
├── scripts/
│   ├── apply-architect-pack.js
│   └── update-method.js
├── src/
│   └── bsl_coach/                  # Sprint 002 package (pure Python, no network)
│       ├── __init__.py             # __version__
│       ├── risk_math.py            # Decimal tier/cap math, SizingResult, typed exceptions
│       ├── snapshot.py             # snapshot read/validate + staleness
│       └── cli.py                  # bsl-size argparse CLI (exit codes 0/2/3/4)
├── templates/
└── tests/                          # 81 tests (Sprint 002)
    ├── test_risk_math.py           # D-009 matrix + worked reference examples
    ├── test_snapshot.py            # missing/stale/malformed handling
    ├── test_cli.py                 # flags, exit codes, --json, offline + snapshot paths
    └── test_guardrails.py          # scripted A-008 out-of-scope grep
```

Not committed (git-ignored): `data/account_snapshot.json` — real account snapshot, written per `docs/SIZING_RECIPE.md`.

## Code outside this folder (known, pending migration)

- `pm_pdf_to_pine.py` — working PDF→Pine parser, daily use since 2026-06-16, in a separate Cowork outputs directory on the MacBook Pro.
- `bsl_pm_watchlist_YYYY-MM-DD.pine` — generated dated Pine scripts.
