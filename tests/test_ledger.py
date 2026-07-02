"""Ledger engine tests — episodes, ET buckets, budget math.

This is money-touching code, so the full D-009 matrix applies: the
ground-truth gate (R-011), every blueprint edge case, and the worked
budget figures at the real NLV.
"""

from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path

import pytest

from bsl_coach.ledger import (
    LedgerError,
    build_episodes,
    build_ledger,
    bucket_pnl,
    compute_budgets,
    match_fills,
    month_start,
    week_start,
)
from bsl_coach.registry import Registry, RegistryEntry
from bsl_coach.trades import Fill, load_trades

FIXTURE = Path(__file__).parent / "fixtures" / "now_2026_07_01_fills.json"
NLV = Decimal("3819828.43")  # live NLV 2026-07-01 (STATE.md)

_counter = [0]


def mk_fill(
    symbol="NOW",
    side="BUY",
    size="100",
    pnl="0",
    time="2026-07-01T14:59:38Z",
    sec_type="STK",
    price="105.57",
):
    _counter[0] += 1
    return Fill(
        trade_id=f"f{_counter[0]}",
        symbol=symbol,
        sec_type=sec_type,
        side=side,
        size=Decimal(size),
        price=Decimal(price),
        trade_time=datetime.fromisoformat(time.replace("Z", "+00:00")),
        realized_pnl=Decimal(pnl),
    )


def mk_registry(*symbol_dates):
    entries = []
    for i, (symbol, iso_utc) in enumerate(symbol_dates, start=1):
        entries.append(
            RegistryEntry(
                id=f"reg-{i}",
                symbol=symbol,
                direction="long",
                registered_at=datetime.fromisoformat(iso_utc.replace("Z", "+00:00")),
            )
        )
    return Registry(entries=entries)


NOW_REGISTRY = mk_registry(("NOW", "2026-07-01T14:55:00Z"))


class TestGroundTruth:
    """A-002 / R-011 — the gate. Real NOW fills, real +$458.61."""

    def test_now_fixture_reproduces_458_61(self):
        fills = load_trades(FIXTURE).fills
        ledger = build_ledger(fills, NOW_REGISTRY, NLV, date(2026, 7, 1))
        assert len(ledger.episodes) == 1
        episode = ledger.episodes[0]
        assert episode.closed
        assert episode.symbol == "NOW"
        assert episode.direction == "long"
        assert episode.entry_shares == Decimal("1000")
        # +$458.61 within +/- $0.01 (acceptance A-002); actual is exact.
        assert abs(episode.realized_pnl - Decimal("458.61")) <= Decimal("0.01")
        assert episode.closed_et_date == date(2026, 7, 1)
        assert episode.opened_et_date == date(2026, 7, 1)
        assert ledger.review == []

    def test_now_fixture_bucketed_to_et_2026_07_01(self):
        fills = load_trades(FIXTURE).fills
        matched = match_fills(fills, NOW_REGISTRY).matched
        d = date(2026, 7, 1)
        assert abs(bucket_pnl(matched, d, d) - Decimal("458.61")) <= Decimal("0.01")
        # Nothing lands on 07-02 even though the snapshot was pulled then.
        assert bucket_pnl(matched, date(2026, 7, 2), date(2026, 7, 2)) == 0


class TestMatching:
    """FR-4 + A-006 — review list, never episode P&L."""

    def test_unregistered_symbol_goes_to_review(self):
        fills = [mk_fill(symbol="MU", pnl="100")]
        result = match_fills(fills, NOW_REGISTRY)
        assert result.matched == []
        assert len(result.review) == 1
        assert "not registered" in result.review[0].reason

    def test_opt_fill_in_registered_symbol_goes_to_review(self):
        fills = [mk_fill(sec_type="OPT", pnl="500")]
        result = match_fills(fills, NOW_REGISTRY)
        assert result.matched == []
        assert "OPT" in result.review[0].reason

    def test_other_sec_type_goes_to_review(self):
        fills = [mk_fill(sec_type="FUT")]
        result = match_fills(fills, NOW_REGISTRY)
        assert result.matched == []
        assert "FUT" in result.review[0].reason

    def test_pre_registration_fill_goes_to_review(self):
        fills = [mk_fill(time="2026-06-30T15:00:00Z", pnl="250")]
        result = match_fills(fills, NOW_REGISTRY)
        assert result.matched == []
        assert "precedes registration" in result.review[0].reason

    def test_same_et_day_earlier_clock_time_matches(self):
        # Dave may register moments AFTER entry — same ET day is inclusive.
        fills = [mk_fill(time="2026-07-01T14:50:00Z")]  # before 14:55 registration
        result = match_fills(fills, NOW_REGISTRY)
        assert len(result.matched) == 1
        assert result.review == []

    def test_review_fills_never_enter_pnl(self):
        fills = [
            mk_fill(time="2026-06-30T15:00:00Z", pnl="1000"),  # pre-registration
            mk_fill(sec_type="OPT", pnl="1000"),
            mk_fill(symbol="MU", pnl="1000"),
        ]
        ledger = build_ledger(fills, NOW_REGISTRY, NLV, date(2026, 7, 1))
        assert ledger.episodes == []
        assert len(ledger.review) == 3
        assert all(b.pnl == 0 for b in ledger.budgets)


class TestEpisodes:
    """FR-5 — entry fills to flat; re-entry = new episode; shorts."""

    def test_multi_fill_episode_the_now_shape(self):
        fills = [
            mk_fill(side="BUY", size="600"),
            mk_fill(side="BUY", size="400"),
            mk_fill(side="SELL", size="700", pnl="300", time="2026-07-01T18:55:00Z"),
            mk_fill(side="SELL", size="300", pnl="158.61", time="2026-07-01T18:55:01Z"),
        ]
        episodes, warnings = build_episodes(fills)
        assert warnings == []
        assert len(episodes) == 1
        assert episodes[0].closed
        assert episodes[0].realized_pnl == Decimal("458.61")

    def test_reentry_same_day_is_second_episode(self):
        fills = [
            mk_fill(side="BUY", time="2026-07-01T14:00:00Z"),
            mk_fill(side="SELL", pnl="50", time="2026-07-01T15:00:00Z"),
            mk_fill(side="BUY", time="2026-07-01T16:00:00Z"),
            mk_fill(side="SELL", pnl="-20", time="2026-07-01T17:00:00Z"),
        ]
        episodes, _ = build_episodes(fills)
        assert len(episodes) == 2
        assert [e.realized_pnl for e in episodes] == [Decimal("50"), Decimal("-20")]
        assert all(e.closed for e in episodes)

    def test_short_episode_sell_first(self):
        fills = [
            mk_fill(side="SELL", size="200", time="2026-07-01T14:00:00Z"),
            mk_fill(side="BUY", size="200", pnl="75.25", time="2026-07-01T15:00:00Z"),
        ]
        episodes, _ = build_episodes(fills)
        assert len(episodes) == 1
        assert episodes[0].direction == "short"
        assert episodes[0].closed
        assert episodes[0].entry_shares == Decimal("200")
        assert episodes[0].realized_pnl == Decimal("75.25")

    def test_open_episode_realized_counts_position_stays_open(self):
        fills = [
            mk_fill(side="BUY", size="1000"),
            mk_fill(side="SELL", size="400", pnl="120", time="2026-07-01T18:00:00Z"),
        ]
        episodes, _ = build_episodes(fills)
        assert len(episodes) == 1
        assert not episodes[0].closed
        assert episodes[0].open_size == Decimal("600")
        assert episodes[0].realized_pnl == Decimal("120")

    def test_partial_exit_spanning_two_et_days_splits_pnl(self):
        """P&L lands in the ET date of each closing fill (FR-5)."""
        fills = [
            mk_fill(side="BUY", size="1000", time="2026-07-01T14:00:00Z"),
            mk_fill(side="SELL", size="500", pnl="200", time="2026-07-01T19:00:00Z"),
            # 01:30Z on 07-02 is still ET 07-01... use 15:00Z on 07-02 for day 2.
            mk_fill(side="SELL", size="500", pnl="258.61", time="2026-07-02T15:00:00Z"),
        ]
        matched = match_fills(fills, NOW_REGISTRY).matched
        assert bucket_pnl(matched, date(2026, 7, 1), date(2026, 7, 1)) == Decimal("200")
        assert bucket_pnl(matched, date(2026, 7, 2), date(2026, 7, 2)) == Decimal("258.61")
        episodes, _ = build_episodes(matched)
        assert len(episodes) == 1 and episodes[0].closed
        assert episodes[0].realized_pnl == Decimal("458.61")

    def test_rollover_fill_lands_on_et_prior_day(self):
        """A-004: 2026-07-02T01:30Z belongs to ET 2026-07-01."""
        fills = [
            mk_fill(side="BUY", size="100", time="2026-07-01T14:00:00Z"),
            mk_fill(side="SELL", size="100", pnl="99", time="2026-07-02T01:30:00Z"),
        ]
        matched = match_fills(fills, NOW_REGISTRY).matched
        assert bucket_pnl(matched, date(2026, 7, 1), date(2026, 7, 1)) == Decimal("99")
        assert bucket_pnl(matched, date(2026, 7, 2), date(2026, 7, 2)) == 0

    def test_fractional_sizes_close_exactly(self):
        fills = [
            mk_fill(side="BUY", size="10.5"),
            mk_fill(side="SELL", size="10.5", pnl="1.234567", time="2026-07-01T18:00:00Z"),
        ]
        episodes, _ = build_episodes(fills)
        assert episodes[0].closed
        assert episodes[0].realized_pnl == Decimal("1.234567")

    def test_zero_realized_on_entry_fills_contributes_nothing(self):
        fills = [
            mk_fill(side="BUY", size="100", pnl="0"),
            mk_fill(side="BUY", size="100", pnl="0"),
            mk_fill(side="SELL", size="200", pnl="42", time="2026-07-01T18:00:00Z"),
        ]
        episodes, _ = build_episodes(fills)
        assert episodes[0].realized_pnl == Decimal("42")

    def test_cross_through_zero_splits_with_warning(self):
        fills = [
            mk_fill(side="BUY", size="100", time="2026-07-01T14:00:00Z"),
            mk_fill(side="SELL", size="250", pnl="30", time="2026-07-01T15:00:00Z"),
            mk_fill(side="BUY", size="150", pnl="10", time="2026-07-01T16:00:00Z"),
        ]
        episodes, warnings = build_episodes(fills)
        assert len(warnings) == 1 and "crossed through zero" in warnings[0]
        assert len(episodes) == 2
        first, second = episodes
        assert first.closed and first.realized_pnl == Decimal("30")
        assert second.closed and second.direction == "short"
        assert second.realized_pnl == Decimal("10")


class TestBuckets:
    def test_week_start_is_monday(self):
        assert week_start(date(2026, 7, 1)) == date(2026, 6, 29)  # Wed -> Mon
        assert week_start(date(2026, 6, 29)) == date(2026, 6, 29)  # Mon -> itself
        assert week_start(date(2026, 7, 5)) == date(2026, 6, 29)  # Sun -> past Mon

    def test_month_start(self):
        assert month_start(date(2026, 7, 15)) == date(2026, 7, 1)

    def test_week_boundary_excludes_prior_week(self):
        fills = [
            mk_fill(side="BUY", size="100", time="2026-06-26T14:00:00Z"),  # prior Fri
            mk_fill(side="SELL", size="100", pnl="-500", time="2026-06-26T18:00:00Z"),
            mk_fill(side="BUY", size="100", time="2026-06-29T14:00:00Z"),  # Monday
            mk_fill(side="SELL", size="100", pnl="-100", time="2026-06-29T18:00:00Z"),
        ]
        reg = mk_registry(("NOW", "2026-06-01T12:00:00Z"))
        matched = match_fills(fills, reg).matched
        today = date(2026, 7, 1)
        assert bucket_pnl(matched, week_start(today), today) == Decimal("-100")
        assert bucket_pnl(matched, month_start(today), today) == Decimal("0")  # June excluded

    def test_month_boundary_excludes_prior_month(self):
        fills = [
            mk_fill(side="BUY", size="100", time="2026-06-30T14:00:00Z"),
            mk_fill(side="SELL", size="100", pnl="-999", time="2026-06-30T18:00:00Z"),
        ]
        reg = mk_registry(("NOW", "2026-06-01T12:00:00Z"))
        matched = match_fills(fills, reg).matched
        today = date(2026, 7, 1)
        assert bucket_pnl(matched, month_start(today), today) == 0
        assert bucket_pnl(matched, date(2026, 6, 1), date(2026, 6, 30)) == Decimal("-999")


class TestBudgets:
    """FR-7 + A-005 — worked figures at the real NLV, both thresholds."""

    def _budget_for(self, pnl, nlv=NLV, name="daily"):
        today = date(2026, 7, 1)
        fills = [
            mk_fill(side="BUY", size="100", time="2026-07-01T14:00:00Z"),
            mk_fill(side="SELL", size="100", pnl=str(pnl), time="2026-07-01T18:00:00Z"),
        ]
        budgets = compute_budgets(fills, nlv, today)
        return {b.name: b for b in budgets}[name]

    def test_caps_at_live_nlv_match_blueprint(self):
        budgets = {b.name: b for b in compute_budgets([], NLV, date(2026, 7, 1))}
        assert budgets["daily"].cap == Decimal("38198.28")
        assert budgets["weekly"].cap == Decimal("114594.85")
        assert budgets["monthly"].cap == Decimal("190991.42")

    def test_caps_derive_from_nlv_never_hardcoded(self):
        budgets = {b.name: b for b in compute_budgets([], Decimal("1000000"), date(2026, 7, 1))}
        assert budgets["daily"].cap == Decimal("10000.00")
        assert budgets["weekly"].cap == Decimal("30000.00")
        assert budgets["monthly"].cap == Decimal("50000.00")

    def test_minus_30000_is_78_5_pct_warning(self):
        b = self._budget_for("-30000")
        assert b.usage_pct == Decimal("78.5")
        assert b.status == "WARNING"
        assert b.action is None

    def test_exactly_75_pct_fires_warning(self):
        # 0.75 * 38198.28 = 28648.71 exactly.
        b = self._budget_for("-28648.71")
        assert b.usage_pct == Decimal("75.0")
        assert b.status == "WARNING"

    def test_just_below_75_pct_is_ok(self):
        b = self._budget_for("-28648.70")
        assert b.status == "OK"

    def test_exactly_100_pct_is_standdown(self):
        b = self._budget_for("-38198.28")
        assert b.usage_pct == Decimal("100.0")
        assert b.status == "STAND DOWN"
        assert "STOP FOR THE DAY" in b.action

    def test_beyond_100_pct_is_standdown(self):
        b = self._budget_for("-50000")
        assert b.status == "STAND DOWN"

    def test_profitable_bucket_is_zero_usage(self):
        b = self._budget_for("458.61")
        assert b.usage_pct == Decimal("0.0")
        assert b.status == "OK"
        assert b.pnl == Decimal("458.61")

    def test_weekly_and_monthly_action_text(self):
        weekly = self._budget_for("-114594.85", name="weekly")
        assert weekly.status == "STAND DOWN"
        assert "HALVE NEXT WEEK'S SIZING" in weekly.action
        monthly = self._budget_for("-190991.42", name="monthly")
        assert monthly.status == "STAND DOWN"
        assert "JOURNAL" in monthly.action

    @pytest.mark.parametrize("nlv", [Decimal("0"), Decimal("-5")])
    def test_zero_or_negative_nlv_fails_loudly_never_divides(self, nlv):
        with pytest.raises(LedgerError):
            compute_budgets([], nlv, date(2026, 7, 1))


class TestBuildLedger:
    def test_standdown_flag_and_warning_text(self):
        fills = [
            mk_fill(side="BUY", size="100", time="2026-07-01T14:00:00Z"),
            mk_fill(side="SELL", size="100", pnl="-38198.28", time="2026-07-01T18:00:00Z"),
        ]
        ledger = build_ledger(fills, NOW_REGISTRY, NLV, date(2026, 7, 1))
        assert ledger.standdown
        assert any("STOP FOR THE DAY" in w for w in ledger.warnings)
        # Informational only — the ledger reports, never blocks (D-003).
        assert any("D-003" in w for w in ledger.warnings)

    def test_warning_threshold_message(self):
        fills = [
            mk_fill(side="BUY", size="100", time="2026-07-01T14:00:00Z"),
            mk_fill(side="SELL", size="100", pnl="-30000", time="2026-07-01T18:00:00Z"),
        ]
        ledger = build_ledger(fills, NOW_REGISTRY, NLV, date(2026, 7, 1))
        assert not ledger.standdown
        assert any("78.5%" in w for w in ledger.warnings)
