"""Pure position-sizing math for BSL Coach.

Pure module: no I/O, no prints, no file access, no network (D-014).
All money values are ``Decimal``; share counts are ``int``. Floats are
rejected at the boundary — they never touch money math.

The tier table and caps below mirror the risk framework in
``planning/DOMAIN.md`` ("Business Rules — Risk Framework", 2026-07-01).
If the framework changes there, change it here and nowhere else.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation

# --------------------------------------------------------------------------
# Constants — single source of truth; see planning/DOMAIN.md risk framework.
# --------------------------------------------------------------------------

#: Per-trade risk as a fraction of NLV, by conviction tier (DOMAIN.md).
TIER_PCT: dict[str, Decimal] = {
    "base": Decimal("0.0010"),  # 0.10% of NLV
    "medium": Decimal("0.0015"),  # 0.15% of NLV
    "high": Decimal("0.0020"),  # 0.20% of NLV
    "max": Decimal("0.0025"),  # 0.25% of NLV
}

#: No single trade risks more than this, regardless of tier or NLV (FR-2).
HARD_CAP_DOLLARS = Decimal("50000")

#: No single position exceeds this fraction of NLV, counting any existing
#: position in the same symbol (FR-5).
CONCENTRATION_LIMIT = Decimal("0.05")

#: Quantum for reported percentage figures (display precision only).
_PCT_QUANTUM = Decimal("0.0001")

VALID_DIRECTIONS = ("long", "short")

# Check names / statuses used in SizingResult.checks
CHECK_HARD_CAP = "hard_cap"
CHECK_CONCENTRATION = "concentration"
STATUS_PASS = "pass"
STATUS_CAPPED = "capped"
STATUS_FAIL = "fail"


# --------------------------------------------------------------------------
# Exceptions
# --------------------------------------------------------------------------


class InvalidInputError(ValueError):
    """An input is missing, malformed, or out of range. No sizing output."""


class InvalidStopError(InvalidInputError):
    """Stop does not sit strictly on the protective side of entry (FR-4)."""


class NoViableSizeError(Exception):
    """The inputs produce zero tradeable shares (FR-6).

    Raised instead of returning a zero-share result so callers can never
    mistake 0 for a tradeable size.
    """

    def __init__(self, message: str, *, reason: str) -> None:
        super().__init__(message)
        self.reason = reason


# --------------------------------------------------------------------------
# Result
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class SizingResult:
    """Outcome of a sizing computation. All money values are Decimal."""

    direction: str
    entry: Decimal
    stop: Decimal
    stop_distance: Decimal
    tier: str
    nlv: Decimal
    existing_value: Decimal
    tier_risk_dollars: Decimal  # tier% x NLV, before the hard cap
    risk_budget_dollars: Decimal  # after the hard cap (FR-2)
    shares_uncapped: int  # from the risk budget alone (FR-3)
    shares: int  # final, after concentration (FR-5)
    position_value: Decimal  # shares x entry
    risk_dollars: Decimal  # actual: shares x stop_distance
    risk_pct_of_nlv: Decimal  # percentage, quantized for display
    concentration_pct: Decimal  # (position_value + existing) / NLV, as %
    checks: dict[str, str]  # check name -> pass | capped | fail
    binding_constraint: str | None
    warnings: list[str] = field(default_factory=list)


# --------------------------------------------------------------------------
# Input normalization
# --------------------------------------------------------------------------


def _to_decimal(name: str, value: object) -> Decimal:
    """Convert an input to Decimal, rejecting floats and bad values."""
    if isinstance(value, bool):
        raise InvalidInputError(f"{name} must be a number, got bool")
    if isinstance(value, float):
        raise InvalidInputError(
            f"{name} must not be a float — pass Decimal, int, or str "
            f"(floats never touch money math)"
        )
    if isinstance(value, Decimal):
        d = value
    elif isinstance(value, (int, str)):
        try:
            d = Decimal(value)
        except InvalidOperation as exc:
            raise InvalidInputError(f"{name} is not a valid number: {value!r}") from exc
    else:
        raise InvalidInputError(f"{name} has unsupported type {type(value).__name__}")
    if not d.is_finite():
        raise InvalidInputError(f"{name} must be finite, got {d}")
    return d


# --------------------------------------------------------------------------
# Core computation
# --------------------------------------------------------------------------


def compute_size(
    direction: str,
    entry: object,
    stop: object,
    tier: str,
    nlv: object,
    existing_value: object = Decimal("0"),
) -> SizingResult:
    """Compute a risk-based share count with every cap checked.

    Raises:
        InvalidInputError: missing/malformed/out-of-range inputs (CLI exit 2).
        InvalidStopError: stop on the wrong side of entry, incl. equality
            (FR-4; CLI exit 2).
        NoViableSizeError: inputs produce zero tradeable shares (FR-6;
            CLI exit 3).
    """
    # --- validate ---------------------------------------------------------
    if not isinstance(direction, str) or direction.lower() not in VALID_DIRECTIONS:
        raise InvalidInputError(
            f"direction must be one of {VALID_DIRECTIONS}, got {direction!r}"
        )
    direction = direction.lower()

    if not isinstance(tier, str) or tier.lower() not in TIER_PCT:
        raise InvalidInputError(
            f"tier must be one of {tuple(TIER_PCT)}, got {tier!r} "
            f"(the tier is always Dave's input — never derived)"
        )
    tier = tier.lower()

    if nlv is None:
        raise InvalidInputError("NLV is required (absent NLV cannot be sized against)")
    entry_d = _to_decimal("entry", entry)
    stop_d = _to_decimal("stop", stop)
    nlv_d = _to_decimal("nlv", nlv)
    existing_d = _to_decimal("existing_value", existing_value)

    if entry_d <= 0:
        raise InvalidInputError(f"entry must be > 0, got {entry_d}")
    if stop_d <= 0:
        raise InvalidInputError(f"stop must be > 0, got {stop_d}")
    if nlv_d <= 0:
        raise InvalidInputError(f"NLV must be > 0, got {nlv_d}")
    if existing_d < 0:
        raise InvalidInputError(
            f"existing_value must be >= 0, got {existing_d} "
            f"(pass the absolute market value of any existing position)"
        )

    # FR-4: long -> stop strictly below entry; short -> strictly above.
    if direction == "long" and not stop_d < entry_d:
        raise InvalidStopError(
            f"long requires stop strictly below entry: stop {stop_d} >= entry {entry_d}"
        )
    if direction == "short" and not stop_d > entry_d:
        raise InvalidStopError(
            f"short requires stop strictly above entry: stop {stop_d} <= entry {entry_d}"
        )

    stop_distance = abs(entry_d - stop_d)  # > 0 guaranteed by FR-4 checks

    warnings: list[str] = []
    checks: dict[str, str] = {}

    # --- FR-1/FR-2: tier risk, then hard cap ------------------------------
    tier_risk = nlv_d * TIER_PCT[tier]
    if tier_risk > HARD_CAP_DOLLARS:
        risk_budget = HARD_CAP_DOLLARS
        checks[CHECK_HARD_CAP] = STATUS_CAPPED
        warnings.append(
            f"hard cap binds: tier risk ${tier_risk:,.2f} trimmed to "
            f"${HARD_CAP_DOLLARS:,.2f}"
        )
    else:
        risk_budget = tier_risk
        checks[CHECK_HARD_CAP] = STATUS_PASS

    # --- FR-3: whole shares, always rounded down --------------------------
    # Decimal floor division is exact — no float wobble at boundaries.
    shares_uncapped = int(risk_budget // stop_distance)
    if shares_uncapped <= 0:
        raise NoViableSizeError(
            f"NO VIABLE SIZE: risk budget ${risk_budget:,.2f} cannot buy a "
            f"single share at stop distance ${stop_distance} — do not trade "
            f"this setup at this size",
            reason="risk budget below one share of stop distance",
        )

    # --- FR-5: concentration (after the hard cap, per blueprint precedence)
    max_position_value = nlv_d * CONCENTRATION_LIMIT
    allowed_new_value = max_position_value - existing_d
    if allowed_new_value <= 0:
        checks[CHECK_CONCENTRATION] = STATUS_FAIL
        raise NoViableSizeError(
            f"NO VIABLE SIZE: existing position value "
            f"${existing_d:,.2f} already meets or exceeds the 5% concentration "
            f"cap (${max_position_value:,.2f} at NLV ${nlv_d:,.2f}) — no new "
            f"shares allowed",
            reason="existing position at/above 5% concentration cap",
        )

    max_shares_concentration = int(allowed_new_value // entry_d)
    if max_shares_concentration < shares_uncapped:
        shares = max_shares_concentration
        checks[CHECK_CONCENTRATION] = STATUS_CAPPED
        warnings.append(
            f"concentration cap binds: shares reduced from {shares_uncapped:,} "
            f"to {shares:,} (5% of NLV = ${max_position_value:,.2f}, existing "
            f"${existing_d:,.2f})"
        )
    else:
        shares = shares_uncapped
        checks[CHECK_CONCENTRATION] = STATUS_PASS

    if shares <= 0:
        raise NoViableSizeError(
            f"NO VIABLE SIZE: concentration cap leaves room for "
            f"${allowed_new_value:,.2f} but one share costs ${entry_d} — "
            f"no new shares allowed",
            reason="concentration headroom below one share",
        )

    # --- binding constraint: the last cap that actually trimmed shares ----
    if checks[CHECK_CONCENTRATION] == STATUS_CAPPED:
        binding: str | None = CHECK_CONCENTRATION
    elif checks[CHECK_HARD_CAP] == STATUS_CAPPED:
        binding = CHECK_HARD_CAP
    else:
        binding = None

    # --- reported figures --------------------------------------------------
    position_value = shares * entry_d
    risk_dollars = shares * stop_distance
    risk_pct = (risk_dollars / nlv_d * 100).quantize(_PCT_QUANTUM)
    concentration_pct = ((position_value + existing_d) / nlv_d * 100).quantize(
        _PCT_QUANTUM
    )

    return SizingResult(
        direction=direction,
        entry=entry_d,
        stop=stop_d,
        stop_distance=stop_distance,
        tier=tier,
        nlv=nlv_d,
        existing_value=existing_d,
        tier_risk_dollars=tier_risk,
        risk_budget_dollars=risk_budget,
        shares_uncapped=shares_uncapped,
        shares=shares,
        position_value=position_value,
        risk_dollars=risk_dollars,
        risk_pct_of_nlv=risk_pct,
        concentration_pct=concentration_pct,
        checks=checks,
        binding_constraint=binding,
        warnings=warnings,
    )
