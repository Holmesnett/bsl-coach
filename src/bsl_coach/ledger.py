"""Ledger engine — episodes, ET buckets, budget math (money-touching, D-009).

Pipeline:

1. **Match** (FR-4): STK fills only; fill symbol == registered symbol;
   fill ET date >= registration ET date (same-ET-day inclusive). OPT
   fills never match in v1. Everything that does not match lands on the
   review list with a reason — it never enters episode P&L (A-006).
2. **Episodes** (FR-5): per symbol, consecutive matched fills from first
   entry until net shares return to zero. Re-entry after flat starts a
   new episode. Episode realized P&L = sum of matched fills'
   ``realized_pnl`` — IBKR's per-fill field is authoritative (R-011);
   this module never invents a P&L definition.
3. **Buckets** (FR-6, D-021): P&L lands in the ET date of each fill
   (entry fills carry 0). Day = ET calendar day; week = Mon–Fri ET
   containing the day; month = ET calendar month.
4. **Budgets** (FR-7): caps are daily 1% / weekly 3% / monthly 5% of
   snapshot NLV. Usage counts losses only: max(0, -bucket_P&L) / cap.
   Warning at >= 75%; stand-down messaging at >= 100%. **Warnings only —
   nothing is ever blocked (D-003).**
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

from .registry import Registry, RegistryEntry
from .trades import Fill

# --- Budget constants (percentages of NLV; DOMAIN.md loss caps) -----------

DAILY_CAP_PCT = Decimal("0.01")
WEEKLY_CAP_PCT = Decimal("0.03")
MONTHLY_CAP_PCT = Decimal("0.05")

#: Usage fraction at/above which a warning fires.
WARNING_USAGE = Decimal("0.75")
#: Usage fraction at/above which stand-down messaging fires (exit 5).
STANDDOWN_USAGE = Decimal("1")

CENT = Decimal("0.01")
TENTH_PCT = Decimal("0.1")

#: Prescribed stand-down actions (DOMAIN.md — informational, never enforced).
STANDDOWN_ACTIONS = {
    "daily": "STOP FOR THE DAY — daily loss cap hit.",
    "weekly": "HALVE NEXT WEEK'S SIZING — weekly loss cap hit.",
    "monthly": "STOP FOR A WEEK AND JOURNAL — monthly loss cap hit.",
}


class LedgerError(Exception):
    """Invalid ledger inputs (e.g. non-positive NLV) — loud failure, exit 4."""


# --- Matching (FR-4) -------------------------------------------------------


@dataclass(frozen=True)
class ReviewItem:
    """A fill excluded from episode P&L, surfaced for human review (A-006)."""

    fill: Fill
    reason: str


@dataclass
class MatchResult:
    matched: list[Fill]
    review: list[ReviewItem]


def match_fills(fills: list[Fill], registry: Registry) -> MatchResult:
    """Split fills into episode-eligible vs review-list per FR-4."""
    reg_dates: dict[str, date] = {}
    for entry in registry.entries:
        d = entry.registered_et_date
        existing = reg_dates.get(entry.symbol)
        if existing is None or d < existing:
            reg_dates[entry.symbol] = d

    matched: list[Fill] = []
    review: list[ReviewItem] = []
    for fill in fills:
        reg_date = reg_dates.get(fill.symbol)
        if reg_date is None:
            review.append(ReviewItem(fill, "symbol not registered"))
        elif fill.sec_type == "OPT":
            review.append(
                ReviewItem(fill, "OPT fill in registered symbol (options not matched in v1)")
            )
        elif fill.sec_type != "STK":
            review.append(
                ReviewItem(fill, f"sec_type {fill.sec_type} not matched in v1")
            )
        elif fill.et_date < reg_date:
            review.append(
                ReviewItem(
                    fill,
                    f"fill ET date {fill.et_date.isoformat()} precedes registration "
                    f"ET date {reg_date.isoformat()}",
                )
            )
        else:
            matched.append(fill)
    return MatchResult(matched=matched, review=review)


# --- Episodes (FR-5) -------------------------------------------------------


@dataclass
class Episode:
    """Consecutive matched fills in one symbol from first entry to flat."""

    symbol: str
    fills: list[Fill] = field(default_factory=list)
    open_size: Decimal = Decimal("0")  # signed net shares; 0 == closed
    #: Accumulated, not derived from ``fills``: a fill that crosses through
    #: zero appears in two episodes but its realized_pnl is attributed to
    #: exactly one (the closing episode) — never double-counted.
    realized_pnl: Decimal = Decimal("0")

    @property
    def closed(self) -> bool:
        return self.open_size == 0

    @property
    def direction(self) -> str:
        first = self.fills[0]
        return "long" if first.side == "BUY" else "short"

    @property
    def opened_et_date(self) -> date:
        return self.fills[0].et_date

    @property
    def closed_et_date(self) -> date | None:
        return self.fills[-1].et_date if self.closed else None

    @property
    def entry_shares(self) -> Decimal:
        """Total shares opened (entry-direction fills)."""
        entry_side = "BUY" if self.direction == "long" else "SELL"
        return sum((f.size for f in self.fills if f.side == entry_side), Decimal("0"))


def build_episodes(matched: list[Fill]) -> tuple[list[Episode], list[str]]:
    """Group matched fills into episodes per symbol (FR-5).

    Returns (episodes, warnings). A fill that crosses through zero
    (e.g. long 100, SELL 200) closes the current episode and opens a
    new one carrying the residual — flagged with a warning because the
    per-fill ``realized_pnl`` is attributed entirely to the closing
    episode.
    """
    by_symbol: dict[str, list[Fill]] = {}
    for fill in matched:
        by_symbol.setdefault(fill.symbol, []).append(fill)

    episodes: list[Episode] = []
    warnings: list[str] = []
    for symbol in sorted(by_symbol):
        fills = sorted(by_symbol[symbol], key=lambda f: (f.trade_time, f.trade_id))
        current: Episode | None = None
        for fill in fills:
            if current is None:
                current = Episode(symbol=symbol)
            before = current.open_size
            after = before + fill.signed_size
            current.fills.append(fill)
            current.realized_pnl += fill.realized_pnl
            if before != 0 and after != 0 and (before > 0) != (after > 0):
                # Crossed through zero: close here, reopen with the residual.
                # The fill's realized_pnl stays entirely with the closing
                # episode (added above) — the residual episode carries the
                # fill for direction/size context only.
                warnings.append(
                    f"fill {fill.trade_id} ({symbol}) crossed through zero "
                    f"({before} -> {after}); episode split — its realized_pnl is "
                    f"attributed to the closing episode; review recommended"
                )
                current.open_size = Decimal("0")
                episodes.append(current)
                current = Episode(symbol=symbol, fills=[fill], open_size=after)
                continue
            current.open_size = after
            if after == 0:
                episodes.append(current)
                current = None
        if current is not None:
            episodes.append(current)
    return episodes, warnings


# --- Buckets (FR-6, D-021) -------------------------------------------------


def week_start(day: date) -> date:
    """Monday of the Mon–Fri ET week containing ``day``."""
    return day - timedelta(days=day.weekday())


def month_start(day: date) -> date:
    return day.replace(day=1)


def bucket_pnl(matched: list[Fill], start: date, end: date) -> Decimal:
    """Realized P&L of matched fills whose ET date is in [start, end].

    Per FR-5, P&L lands in the ET date of each closing fill; entry fills
    carry realized_pnl 0, so summing per-fill values by fill ET date is
    exactly that attribution (and splits partial exits across ET days).
    """
    return sum(
        (f.realized_pnl for f in matched if start <= f.et_date <= end),
        Decimal("0"),
    )


# --- Budgets (FR-7) --------------------------------------------------------


@dataclass(frozen=True)
class BudgetStatus:
    name: str  # "daily" | "weekly" | "monthly"
    label: str  # "TODAY" | "WTD" | "MTD"
    start: date
    end: date
    pnl: Decimal
    cap: Decimal
    usage_pct: Decimal  # display value, quantized to 0.1
    status: str  # "OK" | "WARNING" | "STAND DOWN"
    action: str | None  # prescribed action text when standing down

    @property
    def standdown(self) -> bool:
        return self.status == "STAND DOWN"


def _budget(
    name: str, label: str, start: date, end: date, pnl: Decimal, nlv: Decimal, pct: Decimal
) -> BudgetStatus:
    if nlv <= 0:
        raise LedgerError(f"NLV must be > 0 for budget math, got {nlv}")
    cap = (nlv * pct).quantize(CENT, rounding=ROUND_HALF_UP)
    loss = max(Decimal("0"), -pnl)  # losses only; profitable bucket = 0% (FR-7)
    usage = loss / cap  # cap > 0 guaranteed above — never divide-by-zero
    if usage >= STANDDOWN_USAGE:
        status, action = "STAND DOWN", STANDDOWN_ACTIONS[name]
    elif usage >= WARNING_USAGE:
        status, action = "WARNING", None
    else:
        status, action = "OK", None
    usage_pct = (usage * 100).quantize(TENTH_PCT, rounding=ROUND_HALF_UP)
    return BudgetStatus(
        name=name, label=label, start=start, end=end,
        pnl=pnl, cap=cap, usage_pct=usage_pct, status=status, action=action,
    )


def compute_budgets(
    matched: list[Fill], nlv: Decimal, today: date
) -> list[BudgetStatus]:
    """TODAY / WTD / MTD budget statuses at snapshot NLV (never hardcoded)."""
    ws, ms = week_start(today), month_start(today)
    return [
        _budget("daily", "TODAY", today, today,
                bucket_pnl(matched, today, today), nlv, DAILY_CAP_PCT),
        _budget("weekly", "WTD", ws, today,
                bucket_pnl(matched, ws, today), nlv, WEEKLY_CAP_PCT),
        _budget("monthly", "MTD", ms, today,
                bucket_pnl(matched, ms, today), nlv, MONTHLY_CAP_PCT),
    ]


# --- Full ledger build ------------------------------------------------------


@dataclass
class Ledger:
    episodes: list[Episode]
    review: list[ReviewItem]
    budgets: list[BudgetStatus]
    warnings: list[str]
    matched: list[Fill]

    @property
    def standdown(self) -> bool:
        return any(b.standdown for b in self.budgets)


def build_ledger(
    fills: list[Fill], registry: Registry, nlv: Decimal, today: date
) -> Ledger:
    """The whole pipeline: match -> episodes -> budgets."""
    result = match_fills(fills, registry)
    episodes, warnings = build_episodes(result.matched)
    budgets = compute_budgets(result.matched, nlv, today)
    for b in budgets:
        if b.status == "WARNING":
            warnings.append(
                f"*** {b.label} loss-budget usage {b.usage_pct}% >= 75% of "
                f"${b.cap:,.2f} cap — approaching the {b.name} loss cap ***"
            )
        elif b.status == "STAND DOWN":
            warnings.append(
                f"*** {b.label} loss-budget usage {b.usage_pct}% >= 100% of "
                f"${b.cap:,.2f} cap — {b.action} (informational; execution is "
                f"always your call, D-003) ***"
            )
    return Ledger(
        episodes=episodes,
        review=result.review,
        budgets=budgets,
        warnings=warnings,
        matched=result.matched,
    )
