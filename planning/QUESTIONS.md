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
