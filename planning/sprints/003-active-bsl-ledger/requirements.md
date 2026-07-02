# Sprint 003 Requirements — Active BSL Ledger & Budget Checks

## Why (business goal)

The risk framework's loss caps (daily 1% / weekly 3% / monthly 5% of NLV) currently exist only in Dave's memory. They cannot fire on the right signal because the 47-position Legacy book's MTM noise swamps the Active BSL P&L — and because Dave also makes non-BSL trades after the 2026-07-01 cutoff (MU rolls, SNDU/SHAZ adds, recurring PURR buys), so date-based tagging misclassifies (proven against real fills on 2026-07-01). Tonight's NOW trade required manual archaeology through raw fills to answer "how did my one BSL trade do?" — that question must be one command.

## What

Extend `src/bsl_coach/` with:

1. **BSL trade registry** (`data/bsl_registry.json`) — the tagging system (D-018). A trade is a BSL trade if and only if it is registered. Registration happens at sizing (`bsl-size ... --register`) or manually (`bsl-ledger tag` / `untag` / `list`).
2. **Trades snapshot ingest** (`data/trades_snapshot.json`) — raw IBKR fills written by a Claude session from `get_account_trades` (D-020, same pattern as the account snapshot per D-014). Python never calls MCP.
3. **Ledger engine** — matches STK fills to registered setups, builds trade episodes (entry fills → flat), computes realized P&L per episode from IBKR's per-fill `realized_pnl`, buckets by ET day/week/month (D-021).
4. **Budget checks** — Active BSL realized P&L vs caps: daily 1.0%, weekly 3.0%, monthly 5.0% of NLV (NLV from the account snapshot). Warnings at 75% usage; stand-down messaging at 100% per the framework (daily → stop for the day; weekly → halve next week's sizing; monthly → stop a week and journal). **Warnings only — nothing is ever blocked; execution is manual anyway (D-003).**
5. **`bsl-ledger` CLI report** — today / WTD / MTD Active BSL realized P&L, per-episode lines, budget usage, open registered positions (unrealized shown as info, NOT counted toward caps), unmatched-fill review list, and an informational margin-feasibility line (available funds from the account snapshot) per D-019.

## Functional requirements

- FR-1: Registry entries carry: id, symbol, direction, registered_at (UTC ISO Z), entry, stop, tier, shares_sized, status (active/closed/abandoned), note. Versioned schema `bsl-registry-1`.
- FR-2: `bsl-size --register` appends a registry entry on a successful sizing (exit 0 only). No flag → no registration (sizing alone never tags).
- FR-3: `bsl-ledger tag SYMBOL [--date YYYY-MM-DD] [--note ...]` and `bsl-ledger untag <id>` provide the manual override; `bsl-ledger list` shows the registry.
- FR-4: Matching rule: STK fills only, fill symbol == registered symbol, fill ET date >= registration ET date (same-ET-day inclusive regardless of clock time — Dave may register moments after entry). OPT fills never match in v1; those in registered symbols appear on the review list.
- FR-5: Episode = consecutive matched fills from first entry until net shares return to zero. Re-entry after flat starts a new episode. Episode realized P&L = sum of matched fills' `realized_pnl`. Bucket attribution: P&L lands in the ET date of each closing fill.
- FR-6: All bucketing in America/New_York (D-021): day = ET calendar day; week = Mon–Fri ET containing the day; month = ET calendar month. Fill timestamps arrive UTC and convert at ingest.
- FR-7: Budget usage = losses only: usage = max(0, −bucket_P&L) / cap. Profitable buckets show 0% usage. Caps derive from snapshot NLV at report time.
- FR-8: Snapshot rules mirror Sprint 002: versioned schemas, staleness warnings (trades snapshot ≥ 60 min default), malformed = loud failure. Duplicate fills across overlapping snapshot pulls dedupe by `trade_id`.
- FR-9: Exit codes: 0 = report OK (including warnings), 4 = snapshot missing/malformed, 5 = any cap at ≥ 100% (report still prints; the code lets Claude sessions and scripts detect stand-down state).
- FR-10: `--json` output for the full report, semantically matching the human output.

## Out of scope (hard boundaries)

- Blocking or preventing anything — this sprint informs; it never enforces (execution is manual, D-003).
- Options-strategy BSL trades (v1 is STK episodes only; OPT fills go to the review list).
- Auto-tagging heuristics of any kind — registry and manual tags only (D-018).
- MCP calls, network I/O, order staging (D-013, D-014).
- TUI dashboard, parser migration, unrealized P&L counting toward caps.

## Rigor

D-009 applies in full — P&L aggregation and budget math are money-touching. The NOW trade ground truth (R-011) gates trust in IBKR's `realized_pnl` field.
