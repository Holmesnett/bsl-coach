"""``bsl-ledger`` — Active BSL episode ledger and budget report.

Subcommands:
    report (default) — TODAY / WTD / MTD realized P&L vs loss caps,
                       episodes, open positions, review list
    tag SYMBOL       — manually register a symbol (D-018)
    untag ID         — remove a registry entry
    list             — show the registry

Exit codes (FR-9):
    0 — report OK (including warnings)
    4 — snapshot/registry file missing or malformed, or invalid inputs
    5 — any loss cap at >= 100% usage (stand-down state; the report still
        prints — this code only lets scripts DETECT the state, D-003:
        nothing is ever blocked)

No network I/O, no MCP, no order code (D-013, D-014). Data arrives via
the snapshot files written by a Claude session (see docs/LEDGER_RECIPE.md).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path

from . import __version__
from .ledger import Ledger, LedgerError, build_ledger
from .registry import (
    DEFAULT_PATH as REGISTRY_DEFAULT_PATH,
    Registry,
    RegistryError,
    load_registry,
    tag as registry_tag,
    untag as registry_untag,
)
from .snapshot import (
    DEFAULT_PATH as ACCOUNT_DEFAULT_PATH,
    Snapshot,
    SnapshotError,
    load_snapshot,
)
from .trades import (
    DEFAULT_PATH as TRADES_DEFAULT_PATH,
    TradesError,
    TradesSnapshot,
    et_date,
    load_trades,
)

EXIT_OK = 0
EXIT_INPUT_PROBLEM = 4
EXIT_STANDDOWN = 5


def _decimal_arg(text: str) -> Decimal:
    try:
        value = Decimal(text)
    except InvalidOperation:
        raise argparse.ArgumentTypeError(f"not a valid number: {text!r}")
    if not value.is_finite():
        raise argparse.ArgumentTypeError(f"must be finite: {text!r}")
    return value


def _date_arg(text: str) -> date:
    try:
        return date.fromisoformat(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"not a valid YYYY-MM-DD date: {text!r}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bsl-ledger",
        description=(
            "Active BSL episode ledger and loss-budget report. Informational "
            "only — never blocks, stages, or transmits anything."
        ),
    )
    parser.add_argument(
        "--version", action="version", version=f"bsl-ledger {__version__}"
    )
    sub = parser.add_subparsers(dest="command")

    report = sub.add_parser("report", help="ledger + budget report (the default)")
    report.add_argument(
        "--trades-snapshot",
        type=Path,
        default=TRADES_DEFAULT_PATH,
        help=f"trades snapshot file (default: {TRADES_DEFAULT_PATH})",
    )
    report.add_argument(
        "--account-snapshot",
        type=Path,
        default=ACCOUNT_DEFAULT_PATH,
        help=f"account snapshot file (default: {ACCOUNT_DEFAULT_PATH})",
    )
    report.add_argument(
        "--registry",
        type=Path,
        default=REGISTRY_DEFAULT_PATH,
        help=f"registry file (default: {REGISTRY_DEFAULT_PATH})",
    )
    report.add_argument(
        "--nlv",
        type=_decimal_arg,
        default=None,
        help="override NLV (otherwise read from the account snapshot)",
    )
    report.add_argument(
        "--today",
        type=_date_arg,
        default=None,
        help=(
            "override the report's ET 'today' (default: the ET date of the "
            "trades snapshot's as_of — keeps the report a pure function of "
            "its inputs)"
        ),
    )
    report.add_argument(
        "--snapshot-max-age-minutes",
        type=int,
        default=60,
        help="snapshot age at/beyond which a staleness warning fires (default 60)",
    )
    report.add_argument("--json", action="store_true", help="emit machine-readable JSON")

    tag_p = sub.add_parser("tag", help="manually register a symbol as Active BSL")
    tag_p.add_argument("symbol", help="ticker symbol, e.g. NOW")
    tag_p.add_argument(
        "--date",
        type=_date_arg,
        default=None,
        help="registration ET date (default: today); fills on/after this ET date match",
    )
    tag_p.add_argument("--note", default="", help="free-text note")
    tag_p.add_argument(
        "--registry", type=Path, default=REGISTRY_DEFAULT_PATH,
        help=f"registry file (default: {REGISTRY_DEFAULT_PATH})",
    )

    untag_p = sub.add_parser("untag", help="remove a registry entry by id")
    untag_p.add_argument("id", help="registry entry id, e.g. 2026-07-01-NOW-1")
    untag_p.add_argument(
        "--registry", type=Path, default=REGISTRY_DEFAULT_PATH,
        help=f"registry file (default: {REGISTRY_DEFAULT_PATH})",
    )

    list_p = sub.add_parser("list", help="show the registry")
    list_p.add_argument(
        "--registry", type=Path, default=REGISTRY_DEFAULT_PATH,
        help=f"registry file (default: {REGISTRY_DEFAULT_PATH})",
    )
    list_p.add_argument("--json", action="store_true", help="emit machine-readable JSON")

    return parser


# --- report ----------------------------------------------------------------


def _staleness_warnings(
    trades: TradesSnapshot,
    account: Snapshot | None,
    max_age_minutes: int,
) -> list[str]:
    warnings: list[str] = []
    threshold = timedelta(minutes=max_age_minutes)
    if trades.is_stale(stale_after=threshold):
        minutes = int(trades.age().total_seconds()) // 60
        warnings.append(
            f"*** STALE TRADES SNAPSHOT: {trades.path} is {minutes} minutes old "
            f"(threshold {max_age_minutes}) — refresh via the ledger recipe ***"
        )
    if account is not None and account.is_stale(stale_after=threshold):
        minutes = int(account.age().total_seconds()) // 60
        warnings.append(
            f"*** STALE ACCOUNT SNAPSHOT: {account.path} is {minutes} minutes old "
            f"(threshold {max_age_minutes}) — NLV-derived caps may be outdated ***"
        )
    if trades.duplicate_trade_ids:
        warnings.append(
            f"deduplicated {len(trades.duplicate_trade_ids)} duplicate fill(s) "
            f"by trade_id (overlapping snapshot pulls)"
        )
    return warnings


def _render_report_human(
    ledger: Ledger,
    trades: TradesSnapshot,
    account: Snapshot | None,
    registry: Registry,
    nlv: Decimal,
    nlv_source: str,
    today: date,
    warnings: list[str],
) -> str:
    lines: list[str] = []
    lines.append(f"BSL Ledger — Active BSL realized P&L (ET day {today.isoformat()})")
    lines.append(
        f"Trades as-of: {trades.as_of.isoformat().replace('+00:00', 'Z')}  "
        f"({len(trades.fills)} fills, period {trades.period or 'n/a'})"
    )
    lines.append(f"NLV: ${nlv:,.2f}  (source: {nlv_source})")
    if account is not None and account.available_funds is not None:
        lines.append(
            f"Margin (informational only, D-019): available funds "
            f"${account.available_funds:,.2f}"
        )
    else:
        lines.append(
            "Margin (informational only, D-019): available funds n/a "
            "(not in account snapshot)"
        )
    lines.append("")

    lines.append("Loss budgets (Active BSL realized only; losses count, profits = 0%):")
    for b in ledger.budgets:
        lines.append(
            f"  {b.label:<5} [{b.start.isoformat()} .. {b.end.isoformat()}]  "
            f"P&L {'+' if b.pnl >= 0 else '-'}${abs(b.pnl):,.2f}  "
            f"cap ${b.cap:,.2f}  usage {b.usage_pct}%  {b.status}"
        )
        if b.action:
            lines.append(f"        ACTION: {b.action}")
    lines.append("")

    open_eps = [e for e in ledger.episodes if not e.closed]
    closed_eps = [e for e in ledger.episodes if e.closed]

    lines.append(f"Open registered positions ({len(open_eps)}):")
    if not open_eps:
        lines.append("  (none)")
    for e in open_eps:
        mv = account.positions.get(e.symbol) if account is not None else None
        mv_text = f"  mkt value ${mv:,.2f} (unrealized info only, never in caps)" if mv is not None else ""
        lines.append(
            f"  {e.symbol} {e.direction} open {e.open_size} sh, "
            f"realized so far {'+' if e.realized_pnl >= 0 else '-'}${abs(e.realized_pnl):,.2f}"
            f"{mv_text}"
        )
    lines.append("")

    lines.append(f"Closed episodes ({len(closed_eps)}):")
    if not closed_eps:
        lines.append("  (none)")
    for e in closed_eps:
        lines.append(
            f"  {e.symbol} {e.direction} {e.entry_shares} sh  "
            f"{e.opened_et_date.isoformat()} -> {e.closed_et_date.isoformat()}  "
            f"realized {'+' if e.realized_pnl >= 0 else '-'}${abs(e.realized_pnl):,.2f}  "
            f"({len(e.fills)} fills)"
        )
    lines.append("")

    lines.append(f"Review list — excluded from episode P&L ({len(ledger.review)}):")
    if not ledger.review:
        lines.append("  (none)")
    for item in ledger.review:
        f = item.fill
        lines.append(
            f"  {f.et_date.isoformat()} {f.symbol} {f.sec_type} {f.side} "
            f"{f.size} @ {f.price} — {item.reason}"
        )

    for w in warnings:
        lines.append(f"WARNING: {w}")
    return "\n".join(lines)


def _render_report_json(
    ledger: Ledger,
    trades: TradesSnapshot,
    account: Snapshot | None,
    registry: Registry,
    nlv: Decimal,
    nlv_source: str,
    today: date,
    warnings: list[str],
) -> str:
    payload = {
        "today_et": today.isoformat(),
        "trades_as_of": trades.as_of.isoformat().replace("+00:00", "Z"),
        "fill_count": len(trades.fills),
        "period": trades.period,
        "nlv": str(nlv),
        "nlv_source": nlv_source,
        "available_funds": (
            str(account.available_funds)
            if account is not None and account.available_funds is not None
            else None
        ),
        "budgets": [
            {
                "name": b.name,
                "label": b.label,
                "start_et": b.start.isoformat(),
                "end_et": b.end.isoformat(),
                "realized_pnl": str(b.pnl),
                "cap": str(b.cap),
                "usage_pct": str(b.usage_pct),
                "status": b.status,
                "action": b.action,
            }
            for b in ledger.budgets
        ],
        "open_positions": [
            {
                "symbol": e.symbol,
                "direction": e.direction,
                "open_size": str(e.open_size),
                "realized_pnl_so_far": str(e.realized_pnl),
                "market_value": (
                    str(account.positions[e.symbol])
                    if account is not None and e.symbol in account.positions
                    else None
                ),
            }
            for e in ledger.episodes
            if not e.closed
        ],
        "closed_episodes": [
            {
                "symbol": e.symbol,
                "direction": e.direction,
                "shares": str(e.entry_shares),
                "opened_et": e.opened_et_date.isoformat(),
                "closed_et": e.closed_et_date.isoformat() if e.closed_et_date else None,
                "realized_pnl": str(e.realized_pnl),
                "fill_count": len(e.fills),
            }
            for e in ledger.episodes
            if e.closed
        ],
        "review": [
            {
                "trade_id": item.fill.trade_id,
                "et_date": item.fill.et_date.isoformat(),
                "symbol": item.fill.symbol,
                "sec_type": item.fill.sec_type,
                "side": item.fill.side,
                "size": str(item.fill.size),
                "price": str(item.fill.price),
                "reason": item.reason,
            }
            for item in ledger.review
        ],
        "standdown": ledger.standdown,
        "warnings": warnings,
    }
    return json.dumps(payload, indent=2)


def _run_report(args: argparse.Namespace) -> int:
    try:
        trades = load_trades(args.trades_snapshot)
    except TradesError as exc:
        print(f"TRADES SNAPSHOT ERROR: {exc}", file=sys.stderr)
        return EXIT_INPUT_PROBLEM

    try:
        registry = load_registry(args.registry)
    except RegistryError as exc:
        print(f"REGISTRY ERROR: {exc}", file=sys.stderr)
        return EXIT_INPUT_PROBLEM

    account: Snapshot | None = None
    if args.nlv is not None:
        nlv = args.nlv
        nlv_source = "flags"
        # Account snapshot still useful for market values / margin line if present.
        try:
            account = load_snapshot(args.account_snapshot)
        except SnapshotError:
            account = None
    else:
        try:
            account = load_snapshot(args.account_snapshot)
        except SnapshotError as exc:
            print(f"ACCOUNT SNAPSHOT ERROR: {exc}", file=sys.stderr)
            print(
                "caps derive from NLV — refresh the account snapshot or pass --nlv",
                file=sys.stderr,
            )
            return EXIT_INPUT_PROBLEM
        nlv = account.nlv
        nlv_source = (
            f"snapshot {args.account_snapshot} "
            f"(as_of {account.as_of.isoformat().replace('+00:00', 'Z')})"
        )

    if nlv <= 0:
        print(f"INVALID NLV: must be > 0, got {nlv}", file=sys.stderr)
        return EXIT_INPUT_PROBLEM

    today = args.today if args.today is not None else et_date(trades.as_of)

    warnings = _staleness_warnings(trades, account, args.snapshot_max_age_minutes)

    try:
        ledger = build_ledger(trades.fills, registry, nlv, today)
    except LedgerError as exc:
        print(f"LEDGER ERROR: {exc}", file=sys.stderr)
        return EXIT_INPUT_PROBLEM

    all_warnings = warnings + ledger.warnings
    render = _render_report_json if args.json else _render_report_human
    print(
        render(ledger, trades, account, registry, nlv, nlv_source, today, all_warnings)
    )
    return EXIT_STANDDOWN if ledger.standdown else EXIT_OK


# --- tag / untag / list ------------------------------------------------------


def _run_tag(args: argparse.Namespace) -> int:
    try:
        registry = load_registry(args.registry)
        entry = registry_tag(
            registry, args.symbol.upper(), et_date=args.date, note=args.note
        )
    except RegistryError as exc:
        print(f"REGISTRY ERROR: {exc}", file=sys.stderr)
        return EXIT_INPUT_PROBLEM
    print(
        f"TAGGED: {entry.id}  {entry.symbol}  registered_at "
        f"{entry.registered_at.isoformat().replace('+00:00', 'Z')} "
        f"(ET date {entry.registered_et_date.isoformat()})"
    )
    return EXIT_OK


def _run_untag(args: argparse.Namespace) -> int:
    try:
        registry = load_registry(args.registry)
        removed = registry_untag(registry, args.id)
    except RegistryError as exc:
        print(f"REGISTRY ERROR: {exc}", file=sys.stderr)
        return EXIT_INPUT_PROBLEM
    print(f"UNTAGGED: {removed.id}  {removed.symbol}")
    return EXIT_OK


def _run_list(args: argparse.Namespace) -> int:
    try:
        registry = load_registry(args.registry)
    except RegistryError as exc:
        print(f"REGISTRY ERROR: {exc}", file=sys.stderr)
        return EXIT_INPUT_PROBLEM
    if args.json:
        payload = [
            {
                "id": e.id,
                "symbol": e.symbol,
                "direction": e.direction,
                "registered_at": e.registered_at.isoformat().replace("+00:00", "Z"),
                "registered_et_date": e.registered_et_date.isoformat(),
                "entry": str(e.entry) if e.entry is not None else None,
                "stop": str(e.stop) if e.stop is not None else None,
                "tier": e.tier,
                "shares_sized": e.shares_sized,
                "status": e.status,
                "note": e.note,
            }
            for e in registry.entries
        ]
        print(json.dumps(payload, indent=2))
        return EXIT_OK
    if not registry.entries:
        print(f"registry {registry.path}: (empty)")
        return EXIT_OK
    print(f"registry {registry.path}: {len(registry.entries)} entries")
    for e in registry.entries:
        sized = (
            f"entry {e.entry} stop {e.stop} tier {e.tier} shares {e.shares_sized}"
            if e.entry is not None
            else "manual tag (no sizing context)"
        )
        note = f"  note: {e.note}" if e.note else ""
        print(
            f"  {e.id}  {e.symbol} {e.direction} [{e.status}]  "
            f"ET {e.registered_et_date.isoformat()}  {sized}{note}"
        )
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        # Bare `bsl-ledger` == `bsl-ledger report` with defaults. (Any
        # report flag without the subcommand already errors at parse time.)
        args = parser.parse_args(["report"])
    if args.command == "report":
        return _run_report(args)
    if args.command == "tag":
        return _run_tag(args)
    if args.command == "untag":
        return _run_untag(args)
    if args.command == "list":
        return _run_list(args)
    parser.error(f"unknown command {args.command!r}")
    return EXIT_INPUT_PROBLEM  # unreachable; parser.error raises SystemExit(2)


if __name__ == "__main__":
    sys.exit(main())
