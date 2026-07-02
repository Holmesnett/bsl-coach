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
