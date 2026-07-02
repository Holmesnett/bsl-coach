"""Trades snapshot ingest — raw IBKR fills via the snapshot pattern (D-020).

A Claude session (or Dave by hand) writes ``data/trades_snapshot.json``
from ``get_account_trades``; this module only reads it (D-014 — Python
never calls MCP, never touches the network).

Schema (``bsl-trades-1``):

    { "schema": "bsl-trades-1", "as_of": "<UTC ISO Z>", "period": "DAYS_30",
      "trades": [ ...raw fill objects... ] }

Observed fill fields (probed live 2026-07-01): ``trade_id``, ``symbol``,
``sec_type`` (STK/OPT), ``side`` (BUY/SELL), ``size`` (may be fractional
— Decimal), ``price``, ``trade_time`` (UTC ISO Z), ``commission``,
``net_amount``, ``realized_pnl``, ``order_id``. Unknown extra fields are
ignored, not fatal. Duplicate ``trade_id``s (overlapping snapshot pulls)
dedupe to the first occurrence (FR-8).

All bucketing is America/New_York (D-021): timestamps arrive UTC and
convert at ingest via stdlib ``zoneinfo``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from zoneinfo import ZoneInfo

SCHEMA = "bsl-trades-1"
DEFAULT_PATH = Path("data") / "trades_snapshot.json"

ET = ZoneInfo("America/New_York")

#: A trades snapshot at or beyond this age is stale (FR-8; warn, never block).
DEFAULT_STALE_AFTER = timedelta(minutes=60)


class TradesError(Exception):
    """The trades snapshot is missing, unreadable, or malformed (exit 4)."""


def to_et(dt: datetime) -> datetime:
    """Convert a tz-aware datetime to America/New_York (D-021)."""
    if dt.tzinfo is None:
        raise TradesError(f"naive datetime cannot be bucketed: {dt!r}")
    return dt.astimezone(ET)


def et_date(dt: datetime) -> date:
    """The ET calendar day a UTC fill timestamp belongs to (D-021).

    Example: 2026-07-02T01:30:00Z -> ET 2026-07-01 (21:30 EDT).
    """
    return to_et(dt).date()


@dataclass(frozen=True)
class Fill:
    """One raw IBKR fill, parsed. Money fields are Decimal, never float."""

    trade_id: str
    symbol: str
    sec_type: str  # "STK" | "OPT" | anything else IBKR reports
    side: str  # "BUY" | "SELL"
    size: Decimal
    price: Decimal
    trade_time: datetime  # UTC, tz-aware
    realized_pnl: Decimal  # missing/null in the feed -> 0 (entry fills)
    commission: Decimal | None = None
    net_amount: Decimal | None = None
    order_id: str | None = None

    @property
    def et_date(self) -> date:
        return et_date(self.trade_time)

    @property
    def signed_size(self) -> Decimal:
        """BUY positive, SELL negative — for net-share episode tracking."""
        return self.size if self.side == "BUY" else -self.size


@dataclass
class TradesSnapshot:
    as_of: datetime
    fills: list[Fill] = field(default_factory=list)
    period: str | None = None
    path: Path | None = None
    duplicate_trade_ids: list[str] = field(default_factory=list)

    def age(self, now: datetime | None = None) -> timedelta:
        now = now or datetime.now(timezone.utc)
        return max(now - self.as_of, timedelta(0))

    def is_stale(
        self,
        now: datetime | None = None,
        stale_after: timedelta = DEFAULT_STALE_AFTER,
    ) -> bool:
        # Stale fires AT the threshold (age >= stale_after), matching Sprint 002.
        return self.age(now) >= stale_after


def _decimal_field(name: str, value: object) -> Decimal:
    if isinstance(value, bool):
        raise TradesError(f"fill field {name!r} must be a number, got bool")
    if isinstance(value, (int, Decimal)):
        return Decimal(value)
    if isinstance(value, str):
        try:
            return Decimal(value)
        except InvalidOperation as exc:
            raise TradesError(f"fill field {name!r} is not a valid number: {value!r}") from exc
    raise TradesError(f"fill field {name!r} has unsupported type {type(value).__name__}")


def _optional_decimal_field(name: str, value: object) -> Decimal | None:
    if value is None:
        return None
    return _decimal_field(name, value)


def _parse_trade_time(raw: object) -> datetime:
    if not isinstance(raw, str):
        raise TradesError(f"fill 'trade_time' must be an ISO8601 string, got {raw!r}")
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as exc:
        raise TradesError(f"fill 'trade_time' is not valid ISO8601: {raw!r}") from exc
    if dt.tzinfo is None:
        raise TradesError(f"fill 'trade_time' must be timezone-aware (UTC 'Z'): {raw!r}")
    return dt.astimezone(timezone.utc)


def parse_fill(raw: object) -> Fill:
    """Parse one raw fill object. Unknown extra fields are ignored (FR-8);
    missing required fields fail loudly."""
    if not isinstance(raw, dict):
        raise TradesError(f"each trade must be a JSON object, got {type(raw).__name__}")
    for required in ("trade_id", "symbol", "sec_type", "side", "size", "price", "trade_time"):
        if required not in raw:
            raise TradesError(f"fill missing required field {required!r}: {raw!r}")
    trade_id = raw["trade_id"]
    if isinstance(trade_id, int) and not isinstance(trade_id, bool):
        trade_id = str(trade_id)  # IBKR sometimes reports numeric ids
    if not isinstance(trade_id, str) or not trade_id:
        raise TradesError(f"fill 'trade_id' invalid: {raw['trade_id']!r}")
    symbol = raw["symbol"]
    if not isinstance(symbol, str) or not symbol:
        raise TradesError(f"fill 'symbol' invalid: {symbol!r}")
    sec_type = raw["sec_type"]
    if not isinstance(sec_type, str) or not sec_type:
        raise TradesError(f"fill 'sec_type' invalid: {sec_type!r}")
    side = raw["side"]
    if side not in ("BUY", "SELL"):
        raise TradesError(f"fill 'side' must be BUY or SELL, got {side!r}")
    size = _decimal_field("size", raw["size"])
    if size <= 0:
        raise TradesError(f"fill 'size' must be > 0, got {size}")
    price = _decimal_field("price", raw["price"])
    # realized_pnl may be missing or null on entry fills -> Decimal 0.
    realized_pnl = _optional_decimal_field("realized_pnl", raw.get("realized_pnl"))
    if realized_pnl is None:
        realized_pnl = Decimal("0")
    order_id_raw = raw.get("order_id")
    if isinstance(order_id_raw, int) and not isinstance(order_id_raw, bool):
        order_id_raw = str(order_id_raw)
    if order_id_raw is not None and not isinstance(order_id_raw, str):
        raise TradesError(f"fill 'order_id' invalid: {order_id_raw!r}")
    return Fill(
        trade_id=trade_id,
        symbol=symbol.upper(),
        sec_type=sec_type.upper(),
        side=side,
        size=size,
        price=price,
        trade_time=_parse_trade_time(raw["trade_time"]),
        realized_pnl=realized_pnl,
        commission=_optional_decimal_field("commission", raw.get("commission")),
        net_amount=_optional_decimal_field("net_amount", raw.get("net_amount")),
        order_id=order_id_raw,
    )


def load_trades(path: Path | str = DEFAULT_PATH) -> TradesSnapshot:
    """Load and validate a trades snapshot. Fails loudly on any problem.

    Fills are deduped by ``trade_id`` (first occurrence wins) so
    overlapping snapshot pulls produce identical ledger output (FR-8),
    and returned sorted by (trade_time, trade_id) for determinism.
    """
    path = Path(path)
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise TradesError(f"trades snapshot not found: {path}") from exc
    except OSError as exc:
        raise TradesError(f"cannot read trades snapshot {path}: {exc}") from exc

    try:
        data = json.loads(raw, parse_float=Decimal)
    except json.JSONDecodeError as exc:
        raise TradesError(f"trades snapshot {path} is not valid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise TradesError(f"trades snapshot {path} must contain a JSON object")
    schema = data.get("schema")
    if schema != SCHEMA:
        raise TradesError(
            f"trades snapshot {path} has schema {schema!r}, expected {SCHEMA!r}"
        )
    if "as_of" not in data:
        raise TradesError(f"trades snapshot {path} is missing 'as_of'")
    as_of_raw = data["as_of"]
    if not isinstance(as_of_raw, str):
        raise TradesError("trades snapshot 'as_of' must be an ISO8601 string")
    try:
        as_of = datetime.fromisoformat(as_of_raw.replace("Z", "+00:00"))
    except ValueError as exc:
        raise TradesError(f"trades snapshot 'as_of' not valid ISO8601: {as_of_raw!r}") from exc
    if as_of.tzinfo is None:
        raise TradesError(f"trades snapshot 'as_of' must be timezone-aware: {as_of_raw!r}")

    trades_raw = data.get("trades")
    if not isinstance(trades_raw, list):
        raise TradesError(f"trades snapshot {path} 'trades' must be a list")

    fills: list[Fill] = []
    seen: set[str] = set()
    duplicates: list[str] = []
    for item in trades_raw:
        fill = parse_fill(item)
        if fill.trade_id in seen:
            duplicates.append(fill.trade_id)
            continue
        seen.add(fill.trade_id)
        fills.append(fill)
    fills.sort(key=lambda f: (f.trade_time, f.trade_id))

    period = data.get("period")
    if period is not None and not isinstance(period, str):
        raise TradesError(f"trades snapshot 'period' must be a string: {period!r}")

    return TradesSnapshot(
        as_of=as_of.astimezone(timezone.utc),
        fills=fills,
        period=period,
        path=path,
        duplicate_trade_ids=duplicates,
    )
