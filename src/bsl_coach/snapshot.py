"""Account snapshot file: read, validate, staleness check.

The snapshot is the interface between the Claude runtime (which can call
the IBKR MCP connector) and this pure-Python package, which must never
touch the network (D-014). A Claude session — or Dave by hand — writes
``data/account_snapshot.json``; this module only reads it.

Schema (versioned for future migration):

    {
      "schema": "bsl-snapshot-1",
      "as_of": "2026-07-01T13:05:00Z",        # UTC ISO8601
      "nlv": 3890000,
      "positions": {"NOW": 105570.00},         # symbol -> market value
      "available_funds": 2100000               # optional; informational (D-019)
    }

``available_funds`` was added (optionally) in Sprint 003 for the
ledger's informational margin-feasibility line (D-019). Snapshots
without it remain fully valid — Sprint 002 behavior is unchanged.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

SCHEMA = "bsl-snapshot-1"
DEFAULT_PATH = Path("data") / "account_snapshot.json"

#: A snapshot at or beyond this age is stale (warn loudly, never use silently).
DEFAULT_STALE_AFTER = timedelta(hours=1)


class SnapshotError(Exception):
    """The snapshot file is missing, unreadable, or malformed (CLI exit 4)."""


@dataclass(frozen=True)
class Snapshot:
    nlv: Decimal
    positions: dict[str, Decimal] = field(default_factory=dict)
    as_of: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    path: Path | None = None
    available_funds: Decimal | None = None  # informational only (D-019)

    def age(self, now: datetime | None = None) -> timedelta:
        now = now or datetime.now(timezone.utc)
        return max(now - self.as_of, timedelta(0))

    def is_stale(
        self,
        now: datetime | None = None,
        stale_after: timedelta = DEFAULT_STALE_AFTER,
    ) -> bool:
        # Stale fires AT the threshold (age >= stale_after), per blueprint.
        return self.age(now) >= stale_after


def _decimal_value(name: str, value: object) -> Decimal:
    if isinstance(value, bool):
        raise SnapshotError(f"snapshot field {name!r} must be a number, got bool")
    if isinstance(value, (int, Decimal)):
        return Decimal(value)
    if isinstance(value, str):
        try:
            return Decimal(value)
        except InvalidOperation as exc:
            raise SnapshotError(
                f"snapshot field {name!r} is not a valid number: {value!r}"
            ) from exc
    raise SnapshotError(
        f"snapshot field {name!r} has unsupported type {type(value).__name__}"
    )


def load_snapshot(path: Path | str = DEFAULT_PATH) -> Snapshot:
    """Load and validate a snapshot file. Fails loudly on any problem."""
    path = Path(path)
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SnapshotError(f"snapshot file not found: {path}") from exc
    except OSError as exc:
        raise SnapshotError(f"cannot read snapshot file {path}: {exc}") from exc

    try:
        # parse_float=Decimal keeps floats out of money math entirely.
        data = json.loads(raw, parse_float=Decimal)
    except json.JSONDecodeError as exc:
        raise SnapshotError(f"snapshot file {path} is not valid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise SnapshotError(f"snapshot file {path} must contain a JSON object")

    schema = data.get("schema")
    if schema != SCHEMA:
        raise SnapshotError(
            f"snapshot file {path} has schema {schema!r}, expected {SCHEMA!r}"
        )

    if "as_of" not in data:
        raise SnapshotError(f"snapshot file {path} is missing 'as_of'")
    as_of_raw = data["as_of"]
    if not isinstance(as_of_raw, str):
        raise SnapshotError(f"snapshot 'as_of' must be an ISO8601 string")
    try:
        as_of = datetime.fromisoformat(as_of_raw.replace("Z", "+00:00"))
    except ValueError as exc:
        raise SnapshotError(
            f"snapshot 'as_of' is not valid ISO8601: {as_of_raw!r}"
        ) from exc
    if as_of.tzinfo is None:
        raise SnapshotError(
            f"snapshot 'as_of' must be timezone-aware (UTC 'Z'): {as_of_raw!r}"
        )

    if "nlv" not in data:
        raise SnapshotError(f"snapshot file {path} is missing 'nlv'")
    nlv = _decimal_value("nlv", data["nlv"])
    if nlv <= 0:
        raise SnapshotError(f"snapshot 'nlv' must be > 0, got {nlv}")

    positions_raw = data.get("positions", {})
    if not isinstance(positions_raw, dict):
        raise SnapshotError("snapshot 'positions' must be an object")
    positions: dict[str, Decimal] = {}
    for symbol, value in positions_raw.items():
        if not isinstance(symbol, str) or not symbol:
            raise SnapshotError(f"snapshot position symbol invalid: {symbol!r}")
        positions[symbol.upper()] = _decimal_value(f"positions[{symbol}]", value)

    available_funds: Decimal | None = None
    if data.get("available_funds") is not None:
        available_funds = _decimal_value("available_funds", data["available_funds"])

    return Snapshot(
        nlv=nlv,
        positions=positions,
        as_of=as_of,
        path=path,
        available_funds=available_funds,
    )
