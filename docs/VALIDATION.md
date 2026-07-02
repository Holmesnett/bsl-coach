# Validation — BSL Coach

## Rigor model (D-009)

Micro-app rigor everywhere except money-touching code. Money-touching = anything computing position sizes, stop distances, risk dollars, cap checks, P&L aggregation, budget consumption, or NLV math. That code gets a mandatory test matrix: happy paths AND edge cases. Non-money code gets happy-path plus the failure modes that would lose data.

## Sprint 002 validation (shipped)

- 81 tests green (`PYTHONPATH=src python3 -m pytest -q`); D-009 matrix on `risk_math`; guardrail grep scripted in `tests/test_guardrails.py`.
- Independently re-verified by the Architect 2026-07-01: suite green, guard clean, blueprint reference example reproduced, live dress rehearsal vs hand math exact.
- A-011 (Dave's real-morning smoke test) pending.

## Sprint 003 validation (built 2026-07-01; Gate 4 pending)

- Gate 1 — ground truth: **PASSED.** `tests/fixtures/now_2026_07_01_fills.json` reproduces exactly +$458.61 through IBKR per-fill `realized_pnl` (one closed NOW episode, 1000 sh, ET 2026-07-01) — asserted in `tests/test_ledger.py::TestGroundTruth` and verified end-to-end via `bsl-ledger report` against the fixture (exit 0, caps $38,198.28 / $114,594.85 / $190,991.42 at NLV $3,819,828.43).
- Gate 2 — full matrix green: **PASSED.** 202 tests (`PYTHONPATH=src python3 -m pytest -q`): episodes (incl. cross-through-zero split — a real double-count bug caught and fixed pre-ship), ET bucketing (2026-07-02T01:30Z → ET 07-01 rollover + both DST dates), budget thresholds at exact 75%/100% boundaries with two NLVs, dedupe (A-007), review-list routing (A-006). Sprint 002's 81 tests untouched (`git diff` empty) and green.
- Gate 3 — guardrails: **PASSED.** `grep -rn "create_order_instruction\|ib_insync\|mcp__" src/` → zero hits; `tests/test_guardrails.py` now scans all 7 modules; warnings only, no enforcement paths (D-003).
- Gate 4 — A-011 live check: **PASSED 2026-07-01 ~22:30 ET.** Live report against a fresh 47-fill DAYS_7 snapshot: NOW episode +$458.61 exact vs IBKR Desktop; 31 non-BSL fills routed to review; Dave signed off (sprint 003 CLOSEOUT.md). Sprint 003 closed.

## Standing rules

- A failing or missing test on money math blocks sprint completion — no exceptions.
- Every acceptance item maps to a command or a documented manual check.
- Validation behavior changes get recorded here at each sprint boundary.
