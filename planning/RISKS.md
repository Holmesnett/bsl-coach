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
