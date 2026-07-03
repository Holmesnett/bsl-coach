# Validation — BSL Coach

## Rigor model (D-009)

Micro-app rigor everywhere except money-touching code (sizes, stops, risk
dollars, caps, P&L, budgets, NLV math) which gets the mandatory edge-case
matrix. Sprint 004 adds a second raised-bar category: **level-extraction
correctness** — not money math, but wrong levels reach live charts; golden
fixtures + corpus sweep are mandatory gates.

## Sprint 002 validation (shipped)

81 tests green; D-009 matrix on risk_math; guardrail grep in
tests/test_guardrails.py; live dress rehearsal vs hand math exact.
A-011 (one real morning sizing) scheduled 2026-07-06.

## Sprint 003 validation (shipped)

Ground-truth gate passed: NOW fixture reproduces +$458.61 via IBKR
`realized_pnl`; ET bucketing incl. 20:00-ET rollover + DST dates; budget
thresholds 75%/100%; dedupe; review-list routing. Live A-011 signed off
2026-07-01 against IBKR Desktop records. 202 tests total.

## Sprint 004 validation (active)

- Gate 1 — golden extraction: 07/01 + 07/02 fixtures exact; ≥3 curated older
  PDFs hand-verified.
- Gate 2 — corpus sweep: every PDF in references/client-docs/ parses without
  traceback; unrecognized-bullet report persisted to CLOSEOUT.
- Gate 3 — Pine golden file byte-exact; empty-array regression (the 2026-07-02
  production bug) explicitly tested; no unguarded loops in generated output.
- Gate 4 — determinism (byte-identical re-runs) + guardrails extended.
- Gate 5 — A-010 live morning: real PDF → generated Pine on charts → levels
  eye-verified vs PDF; Dave signs off.

## Standing rules

- A failing or missing test on money math OR level extraction blocks sprint
  completion — no exceptions.
- Every acceptance item maps to a command or a documented manual check.
- Validation behavior changes get recorded here at each sprint boundary.
