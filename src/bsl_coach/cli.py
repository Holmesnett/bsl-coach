"""``bsl-size`` — position sizing CLI.

Exit codes (blueprint):
    0 — sized OK (including capped results)
    2 — invalid input (bad flags, bad stop/entry relationship, bad NLV)
    3 — no viable size (FR-6): never prints 0 shares as tradeable
    4 — snapshot problem when the snapshot was the selected data source

No network I/O, no MCP, no order construction (D-013, D-014). Account
data arrives via flags or the snapshot file only.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path

from . import __version__
from .risk_math import (
    InvalidInputError,
    NoViableSizeError,
    SizingResult,
    TIER_PCT,
    compute_size,
)
from .snapshot import DEFAULT_PATH, Snapshot, SnapshotError, load_snapshot

EXIT_OK = 0
EXIT_INVALID_INPUT = 2
EXIT_NO_VIABLE_SIZE = 3
EXIT_SNAPSHOT_PROBLEM = 4


def _decimal_arg(text: str) -> Decimal:
    try:
        value = Decimal(text)
    except InvalidOperation:
        raise argparse.ArgumentTypeError(f"not a valid number: {text!r}")
    if not value.is_finite():
        raise argparse.ArgumentTypeError(f"must be finite: {text!r}")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bsl-size",
        description=(
            "Risk-based position sizing for BSL setups. Numbers only — "
            "never stages or transmits orders."
        ),
    )
    parser.add_argument("symbol", help="ticker symbol, e.g. NOW")
    parser.add_argument(
        "--direction", required=True, choices=("long", "short"), help="trade direction"
    )
    parser.add_argument(
        "--entry", required=True, type=_decimal_arg, help="entry price"
    )
    parser.add_argument(
        "--stop",
        required=True,
        type=_decimal_arg,
        help="stop price (long: below entry; short: above entry)",
    )
    parser.add_argument(
        "--tier",
        required=True,
        choices=tuple(TIER_PCT),
        help="conviction tier (always your call — never auto-derived)",
    )
    parser.add_argument(
        "--nlv",
        type=_decimal_arg,
        default=None,
        help="account NLV in dollars; omit to read from the snapshot file",
    )
    parser.add_argument(
        "--existing-value",
        type=_decimal_arg,
        default=None,
        help=(
            "market value of any existing position in this symbol; omit to "
            "read from the snapshot file (0 if no snapshot)"
        ),
    )
    parser.add_argument(
        "--snapshot",
        type=Path,
        default=DEFAULT_PATH,
        help=f"account snapshot file (default: {DEFAULT_PATH})",
    )
    parser.add_argument(
        "--snapshot-max-age-minutes",
        type=int,
        default=60,
        help="snapshot age at/beyond which a staleness warning fires (default 60)",
    )
    parser.add_argument(
        "--json", action="store_true", help="emit machine-readable JSON"
    )
    parser.add_argument(
        "--version", action="version", version=f"bsl-size {__version__}"
    )
    return parser


def _resolve_account_data(
    args: argparse.Namespace, symbol: str, warnings: list[str]
) -> tuple[Decimal, Decimal, str, int | None]:
    """Resolve (nlv, existing_value, nlv_source, snapshot_age_seconds).

    Explicit flags always override snapshot values. Exits (via SnapshotError
    propagation to the caller) only when the snapshot was actually needed.
    """
    nlv_needed = args.nlv is None
    existing_needed = args.existing_value is None

    snapshot: Snapshot | None = None
    snapshot_age_seconds: int | None = None

    if nlv_needed or existing_needed:
        try:
            snapshot = load_snapshot(args.snapshot)
        except SnapshotError:
            if nlv_needed:
                raise  # snapshot was the selected NLV source -> exit 4
            if existing_needed and Path(args.snapshot).exists():
                raise  # file exists but is unusable -> fail loudly, exit 4
            # No snapshot file and only existing-value missing: assume 0
            # loudly rather than block the offline path (FR-8).
            warnings.append(
                f"existing-value not supplied and no snapshot at "
                f"{args.snapshot} — assuming $0 existing exposure in {symbol}; "
                f"pass --existing-value if you hold this symbol"
            )
            snapshot = None

    if snapshot is not None:
        age = snapshot.age()
        snapshot_age_seconds = int(age.total_seconds())
        stale_after = timedelta(minutes=args.snapshot_max_age_minutes)
        if snapshot.is_stale(stale_after=stale_after):
            minutes = snapshot_age_seconds // 60
            warnings.append(
                f"*** STALE SNAPSHOT: {args.snapshot} is {minutes} minutes old "
                f"(threshold {args.snapshot_max_age_minutes}) — values may be "
                f"outdated; refresh via the sizing recipe before trusting this ***"
            )

    if args.nlv is not None:
        nlv = args.nlv
        nlv_source = "flags"
    else:
        assert snapshot is not None
        nlv = snapshot.nlv
        nlv_source = f"snapshot {args.snapshot} (as_of {snapshot.as_of.isoformat()})"

    if args.existing_value is not None:
        existing = args.existing_value
    elif snapshot is not None:
        raw = snapshot.positions.get(symbol.upper(), Decimal("0"))
        existing = abs(raw)
        if raw < 0:
            warnings.append(
                f"snapshot market value for {symbol} is negative ({raw}); "
                f"using absolute value ${existing} for the concentration check"
            )
    else:
        existing = Decimal("0")

    return nlv, existing, nlv_source, snapshot_age_seconds


def _render_human(
    symbol: str,
    result: SizingResult,
    nlv_source: str,
    snapshot_age_seconds: int | None,
    warnings: list[str],
) -> str:
    lines: list[str] = []
    lines.append(
        f"BSL Size — {symbol} {result.direction} @ {result.entry}, "
        f"stop {result.stop} (distance {result.stop_distance})"
    )
    lines.append(f"NLV: ${result.nlv:,.2f}  (source: {nlv_source})")
    if snapshot_age_seconds is not None:
        lines.append(f"Snapshot age: {snapshot_age_seconds // 60} min")
    tier_pct = TIER_PCT[result.tier] * 100
    lines.append(
        f"Tier: {result.tier} ({tier_pct}% -> tier risk "
        f"${result.tier_risk_dollars:,.2f}; budget after hard cap "
        f"${result.risk_budget_dollars:,.2f})"
    )
    lines.append("")
    lines.append(f"SHARES: {result.shares:,}  (uncapped: {result.shares_uncapped:,})")
    lines.append(
        f"Position value: ${result.position_value:,.2f}  "
        f"(concentration {result.concentration_pct}% of NLV incl. existing "
        f"${result.existing_value:,.2f})"
    )
    lines.append(
        f"Dollar risk: ${result.risk_dollars:,.2f}  "
        f"({result.risk_pct_of_nlv}% of NLV)"
    )
    checks = " | ".join(
        f"{name}: {status.upper() if status != 'pass' else 'pass'}"
        for name, status in result.checks.items()
    )
    lines.append(f"Checks: {checks}")
    lines.append(f"Binding constraint: {result.binding_constraint or 'none'}")
    for w in warnings:
        lines.append(f"WARNING: {w}")
    return "\n".join(lines)


def _render_json(
    symbol: str,
    result: SizingResult,
    nlv_source: str,
    snapshot_age_seconds: int | None,
    warnings: list[str],
) -> str:
    payload = {
        "symbol": symbol,
        "direction": result.direction,
        "tier": result.tier,
        "entry": str(result.entry),
        "stop": str(result.stop),
        "stop_distance": str(result.stop_distance),
        "nlv": str(result.nlv),
        "nlv_source": nlv_source,
        "snapshot_age_seconds": snapshot_age_seconds,
        "existing_value": str(result.existing_value),
        "tier_risk_dollars": str(result.tier_risk_dollars),
        "risk_budget_dollars": str(result.risk_budget_dollars),
        "shares": result.shares,
        "shares_uncapped": result.shares_uncapped,
        "position_value": str(result.position_value),
        "risk_dollars": str(result.risk_dollars),
        "risk_pct_of_nlv": str(result.risk_pct_of_nlv),
        "concentration_pct": str(result.concentration_pct),
        "checks": result.checks,
        "binding_constraint": result.binding_constraint,
        "warnings": warnings,
    }
    return json.dumps(payload, indent=2)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    symbol = args.symbol.upper()

    warnings: list[str] = []

    try:
        nlv, existing, nlv_source, snapshot_age_seconds = _resolve_account_data(
            args, symbol, warnings
        )
    except SnapshotError as exc:
        print(f"SNAPSHOT ERROR: {exc}", file=sys.stderr)
        return EXIT_SNAPSHOT_PROBLEM

    try:
        result = compute_size(
            direction=args.direction,
            entry=args.entry,
            stop=args.stop,
            tier=args.tier,
            nlv=nlv,
            existing_value=existing,
        )
    except NoViableSizeError as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_NO_VIABLE_SIZE
    except InvalidInputError as exc:
        print(f"INVALID INPUT: {exc}", file=sys.stderr)
        return EXIT_INVALID_INPUT

    all_warnings = warnings + result.warnings
    if args.json:
        print(_render_json(symbol, result, nlv_source, snapshot_age_seconds, all_warnings))
    else:
        print(_render_human(symbol, result, nlv_source, snapshot_age_seconds, all_warnings))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
