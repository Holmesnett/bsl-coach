# Sprint 002 Closeout — Position Sizing Calculator

**Builder:** Fable 5 (Claude Code)
**Date:** 2026-07-01
**Status:** Built and verified A-001..A-010. **A-011 (live smoke test) awaiting Dave's sign-off.**

---

## What shipped

- `src/bsl_coach/` — `risk_math.py` (pure Decimal math, typed exceptions),
  `snapshot.py` (versioned schema, staleness check), `cli.py` (`bsl-size`).
- `tests/` — 81 tests: `test_risk_math.py` (D-009 matrix), `test_snapshot.py`,
  `test_cli.py`, `test_guardrails.py` (scripted A-008 grep).
- `pyproject.toml` (stdlib-only runtime; `bsl-size` entry point), `.gitignore`
  (real snapshots never committed).
- `samples/account_snapshot.example.json`, `docs/SIZING_RECIPE.md`,
  README Quick Start.

## Acceptance verification (commands run 2026-07-01, all from repo root)

| Item | Command | Result |
|---|---|---|
| A-001 | `PYTHONPATH=src python3 -m pytest -q` | **81 passed** — every blueprint edge case has ≥1 test; worked examples encoded exactly |
| A-002 | `PYTHONPATH=src python3 -m bsl_coach.cli NOW --direction long --entry 105.57 --stop 104.59 --tier base --nlv 4000000 --existing-value 0` | SHARES 1,894 (uncapped 4,081), position $199,949.58, binding = concentration, exit 0 |
| A-003 | same CLI, `--tier max --nlv 30000000 --entry 100 --stop 90` | risk trimmed $75,000 → $50,000, binding = hard_cap |
| A-004 | long `--stop 101` / short `--stop 99` vs entry 100 | both **exit 2**, clear stderr message, zero stdout |
| A-005 | `--entry 6000 --stop 1000 --tier base --nlv 4000000` | **exit 3**, "NO VIABLE SIZE" on stderr, no 0-share output |
| A-006 | A-002 command with `--snapshot` pointing at an absent file | exit 0, `source: flags`, no network access (none exists in src/) |
| A-007 | fresh/stale/malformed snapshots in `/tmp/bsl-accept/` | fresh supplies NLV+existing (SHARES 842 vs NOW $105,570 existing); stale (120 min) computes with `*** STALE SNAPSHOT … 120 minutes old ***`; malformed **exit 4** |
| A-008 | `grep -r "create_order_instruction\|ib_insync\|mcp__" src/` | zero hits (also scripted permanently in `tests/test_guardrails.py`) |
| A-009 | A-002 command + `--json` piped to `json.tool` | valid JSON; `tests/test_cli.py::TestJsonOutput` asserts semantic match with human output |
| A-010 | README Quick Start + `docs/SIZING_RECIPE.md` | offline first sizing = one command; recipe documents MCP fetch → snapshot → CLI → relay end to end |
| A-011 | **Dave drives** | ⏳ AWAITING SIGN-OFF — one real morning sizing vs hand math; record here and in STATE.md |

## Builder implementation decisions (recorded as D-016)

- FR-6 is an exception (`NoViableSizeError`), not a zero-share result — a 0 can never be mistaken for tradeable.
- Staleness fires at the threshold (`age >= 60 min` default; `--snapshot-max-age-minutes`).
- Negative snapshot market value (short/options legacy positions) → absolute value used for the concentration check, with a warning.
- `--existing-value` omitted with no snapshot file → assumes $0 with a loud warning (keeps the FR-8 offline path usable); if a snapshot file exists but is unreadable, that's exit 4, never a silent 0.
- When both caps bind, `binding_constraint` names the one that trimmed the final share count (concentration after hard cap, per blueprint precedence).

## Deviations from blueprint

None of substance. Test count and file layout match the blueprint. One extra test file (`test_guardrails.py`) makes the A-008 grep permanent.
