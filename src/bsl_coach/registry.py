"""BSL trade registry — the tagging system (D-018).

A trade is an Active BSL trade if and only if it is registered here.
Registration happens at sizing time (``bsl-size ... --register``) or
manually (``bsl-ledger tag`` / ``untag``). No auto-tagging heuristics,
ever (D-018): date-based tagging was falsified by real fills on
2026-07-01.

Schema (``bsl-registry-1``), stored at ``data/bsl_registry.json``:

    { "schema": "bsl-registry-1",
      "entries": [ { "id": "2026-07-01-NOW-1", "symbol": "NOW",
        "direction": "long", "registered_at": "2026-07-01T14:55:00Z",
        "entry": "105.57", "stop": "104.59", "tier": "base",
        "shares_sized": 1602, "status": "active", "note": "" } ] }

Manual ``tag`` entries have no sizing context, so ``entry``, ``stop``,
``tier`` and ``shares_sized`` are null for them (D-022). Matching (FR-4)
only uses symbol + registration ET date, so this loses nothing.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from zoneinfo import ZoneInfo

SCHEMA = "bsl-registry-1"
DEFAULT_PATH = Path("data") / "bsl_registry.json"

ET = ZoneInfo("America/New_York")

VALID_STATUSES = ("active", "closed", "abandoned")


class RegistryError(Exception):
    """The registry file is malformed, or an operation is invalid."""


@dataclass(frozen=True)
class RegistryEntry:
    """One registered BSL trade (FR-1)."""

    id: str
    symbol: str
    direction: str  # "long" | "short"
    registered_at: datetime  # UTC, tz-aware
    entry: Decimal | None = None
    stop: Decimal | None = None
    tier: str | None = None
    shares_sized: int | None = None
    status: str = "active"
    note: str = ""

    @property
    def registered_et_date(self) -> date:
        """Registration date in America/New_York — governs matching (FR-4)."""
        return self.registered_at.astimezone(ET).date()


@dataclass
class Registry:
    entries: list[RegistryEntry] = field(default_factory=list)
    path: Path = DEFAULT_PATH


def _parse_utc(name: str, raw: object) -> datetime:
    if not isinstance(raw, str):
        raise RegistryError(f"registry field {name!r} must be an ISO8601 string")
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as exc:
        raise RegistryError(f"registry field {name!r} not valid ISO8601: {raw!r}") from exc
    if dt.tzinfo is None:
        raise RegistryError(f"registry field {name!r} must be timezone-aware: {raw!r}")
    return dt.astimezone(timezone.utc)


def _optional_decimal(name: str, raw: object) -> Decimal | None:
    if raw is None:
        return None
    if isinstance(raw, bool):
        raise RegistryError(f"registry field {name!r} must be a number, got bool")
    if isinstance(raw, (int, Decimal)):
        return Decimal(raw)
    if isinstance(raw, str):
        try:
            return Decimal(raw)
        except InvalidOperation as exc:
            raise RegistryError(f"registry field {name!r} not a number: {raw!r}") from exc
    raise RegistryError(f"registry field {name!r} has unsupported type {type(raw).__name__}")


def _entry_from_dict(raw: object) -> RegistryEntry:
    if not isinstance(raw, dict):
        raise RegistryError("registry entries must be JSON objects")
    for required in ("id", "symbol", "direction", "registered_at", "status"):
        if required not in raw:
            raise RegistryError(f"registry entry missing required field {required!r}")
    entry_id = raw["id"]
    symbol = raw["symbol"]
    direction = raw["direction"]
    status = raw["status"]
    if not isinstance(entry_id, str) or not entry_id:
        raise RegistryError(f"registry entry id invalid: {entry_id!r}")
    if not isinstance(symbol, str) or not symbol:
        raise RegistryError(f"registry entry symbol invalid: {symbol!r}")
    if direction not in ("long", "short"):
        raise RegistryError(f"registry entry direction invalid: {direction!r}")
    if status not in VALID_STATUSES:
        raise RegistryError(f"registry entry status invalid: {status!r}")
    shares_raw = raw.get("shares_sized")
    if shares_raw is not None and (isinstance(shares_raw, bool) or not isinstance(shares_raw, int)):
        raise RegistryError(f"registry entry shares_sized must be an int: {shares_raw!r}")
    note = raw.get("note", "")
    if not isinstance(note, str):
        raise RegistryError(f"registry entry note must be a string: {note!r}")
    tier = raw.get("tier")
    if tier is not None and not isinstance(tier, str):
        raise RegistryError(f"registry entry tier must be a string: {tier!r}")
    return RegistryEntry(
        id=entry_id,
        symbol=symbol.upper(),
        direction=direction,
        registered_at=_parse_utc("registered_at", raw["registered_at"]),
        entry=_optional_decimal("entry", raw.get("entry")),
        stop=_optional_decimal("stop", raw.get("stop")),
        tier=tier,
        shares_sized=shares_raw,
        status=status,
        note=note,
    )


def load_registry(path: Path | str = DEFAULT_PATH) -> Registry:
    """Load the registry. A missing file is an empty registry (first run);
    anything else wrong is a loud failure."""
    path = Path(path)
    if not path.exists():
        return Registry(entries=[], path=path)
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RegistryError(f"cannot read registry file {path}: {exc}") from exc
    try:
        data = json.loads(raw, parse_float=Decimal)
    except json.JSONDecodeError as exc:
        raise RegistryError(f"registry file {path} is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise RegistryError(f"registry file {path} must contain a JSON object")
    schema = data.get("schema")
    if schema != SCHEMA:
        raise RegistryError(
            f"registry file {path} has schema {schema!r}, expected {SCHEMA!r}"
        )
    entries_raw = data.get("entries", [])
    if not isinstance(entries_raw, list):
        raise RegistryError(f"registry file {path} 'entries' must be a list")
    entries = [_entry_from_dict(item) for item in entries_raw]
    seen: set[str] = set()
    for entry in entries:
        if entry.id in seen:
            raise RegistryError(f"registry file {path} has duplicate id {entry.id!r}")
        seen.add(entry.id)
    return Registry(entries=entries, path=path)


def _entry_to_dict(entry: RegistryEntry) -> dict:
    return {
        "id": entry.id,
        "symbol": entry.symbol,
        "direction": entry.direction,
        "registered_at": entry.registered_at.astimezone(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        "entry": str(entry.entry) if entry.entry is not None else None,
        "stop": str(entry.stop) if entry.stop is not None else None,
        "tier": entry.tier,
        "shares_sized": entry.shares_sized,
        "status": entry.status,
        "note": entry.note,
    }


def save_registry(registry: Registry) -> None:
    """Write the registry back to its path (creates data/ if needed)."""
    registry.path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"schema": SCHEMA, "entries": [_entry_to_dict(e) for e in registry.entries]}
    registry.path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def next_id(registry: Registry, symbol: str, et_day: date) -> str:
    """IDs are ``YYYY-MM-DD-SYMBOL-N`` on the registration ET date."""
    prefix = f"{et_day.isoformat()}-{symbol.upper()}-"
    n = 1
    existing = {e.id for e in registry.entries}
    while f"{prefix}{n}" in existing:
        n += 1
    return f"{prefix}{n}"


def add_entry(
    registry: Registry,
    *,
    symbol: str,
    direction: str,
    registered_at: datetime | None = None,
    entry: Decimal | None = None,
    stop: Decimal | None = None,
    tier: str | None = None,
    shares_sized: int | None = None,
    note: str = "",
) -> RegistryEntry:
    """Append a new entry and persist. Returns the created entry."""
    if direction not in ("long", "short"):
        raise RegistryError(f"direction must be 'long' or 'short', got {direction!r}")
    registered_at = registered_at or datetime.now(timezone.utc)
    if registered_at.tzinfo is None:
        raise RegistryError("registered_at must be timezone-aware")
    registered_at = registered_at.astimezone(timezone.utc)
    et_day = registered_at.astimezone(ET).date()
    new = RegistryEntry(
        id=next_id(registry, symbol, et_day),
        symbol=symbol.upper(),
        direction=direction,
        registered_at=registered_at,
        entry=entry,
        stop=stop,
        tier=tier,
        shares_sized=shares_sized,
        status="active",
        note=note,
    )
    registry.entries.append(new)
    save_registry(registry)
    return new


def tag(
    registry: Registry,
    symbol: str,
    *,
    et_date: date | None = None,
    note: str = "",
    now: datetime | None = None,
) -> RegistryEntry:
    """Manual tag (FR-3). ``--date`` gives the registration ET date; entries
    tagged for a past date register at 00:00 ET that day so same-day fills
    match (FR-4)."""
    now = now or datetime.now(timezone.utc)
    if et_date is None:
        registered_at = now
    else:
        registered_at = datetime(
            et_date.year, et_date.month, et_date.day, 0, 0, 0, tzinfo=ET
        ).astimezone(timezone.utc)
    return add_entry(
        registry,
        symbol=symbol,
        direction="long",
        registered_at=registered_at,
        note=note or "manual tag",
    )


def untag(registry: Registry, entry_id: str) -> RegistryEntry:
    """Remove an entry by id and persist. Loud failure if absent."""
    for i, entry in enumerate(registry.entries):
        if entry.id == entry_id:
            removed = registry.entries.pop(i)
            save_registry(registry)
            return removed
    raise RegistryError(f"no registry entry with id {entry_id!r}")
