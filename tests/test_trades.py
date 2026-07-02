"""Trades snapshot ingest tests — FR-8, D-020, D-021 (UTC->ET)."""

import json
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

import pytest

from bsl_coach.trades import (
    TradesError,
    et_date,
    load_trades,
    parse_fill,
)

FIXTURE = Path(__file__).parent / "fixtures" / "now_2026_07_01_fills.json"


def _valid_fill(**overrides):
    # Money fields as strings/ints: in the real path json.loads uses
    # parse_float=Decimal, so parse_fill never sees Python floats.
    fill = {
        "trade_id": "t1",
        "symbol": "NOW",
        "sec_type": "STK",
        "side": "BUY",
        "size": 100,
        "price": "105.55",
        "trade_time": "2026-07-01T14:59:38Z",
        "commission": "0.35",
        "net_amount": "-10555.35",
        "realized_pnl": "0.0",
        "order_id": "o1",
    }
    fill.update(overrides)
    return fill


def _write_snapshot(path, trades, as_of="2026-07-01T19:00:00Z"):
    payload = {"schema": "bsl-trades-1", "as_of": as_of, "period": "DAYS_30", "trades": trades}
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


class TestEtConversion:
    def test_rollover_2026_07_02_0130z_is_et_07_01(self):
        # The exact rollover observed live: 21:30 EDT on 07-01.
        dt = datetime(2026, 7, 2, 1, 30, tzinfo=timezone.utc)
        assert et_date(dt) == date(2026, 7, 1)

    def test_dst_spring_boundary_march(self):
        # DST starts 2026-03-08. 2026-03-09T00:30Z is 20:30 EDT on 03-08;
        # under the winter offset it would have read 19:30 — either way the
        # ET date must be 03-08, computed via zoneinfo not a fixed offset.
        dt = datetime(2026, 3, 9, 0, 30, tzinfo=timezone.utc)
        assert et_date(dt) == date(2026, 3, 8)
        # Just before the spring-forward instant (06:59Z = 01:59 EST).
        assert et_date(datetime(2026, 3, 8, 6, 59, tzinfo=timezone.utc)) == date(2026, 3, 8)

    def test_dst_fall_boundary_november(self):
        # DST ends 2026-11-01. 2026-11-02T04:30Z is 23:30 EST on 11-01;
        # a stale EDT offset would wrongly say 00:30 on 11-02.
        dt = datetime(2026, 11, 2, 4, 30, tzinfo=timezone.utc)
        assert et_date(dt) == date(2026, 11, 1)
        # The repeated 01:30 hour on fall-back day stays on 11-01.
        assert et_date(datetime(2026, 11, 1, 5, 30, tzinfo=timezone.utc)) == date(2026, 11, 1)

    def test_naive_datetime_rejected(self):
        with pytest.raises(TradesError):
            et_date(datetime(2026, 7, 1, 14, 0))


class TestParseFill:
    def test_decimal_types_and_fields(self):
        fill = parse_fill(_valid_fill(size="10.5", price="105.567"))
        assert fill.size == Decimal("10.5")  # fractional sizes supported
        assert isinstance(fill.size, Decimal)
        assert fill.price == Decimal("105.567")
        assert fill.trade_time == datetime(2026, 7, 1, 14, 59, 38, tzinfo=timezone.utc)
        assert fill.et_date == date(2026, 7, 1)

    def test_missing_realized_pnl_is_zero(self):
        raw = _valid_fill()
        del raw["realized_pnl"]
        assert parse_fill(raw).realized_pnl == Decimal("0")

    def test_null_realized_pnl_is_zero(self):
        assert parse_fill(_valid_fill(realized_pnl=None)).realized_pnl == Decimal("0")

    def test_unknown_extra_fields_ignored(self):
        fill = parse_fill(_valid_fill(exchange="ISLAND", liquidation=0, foo={"bar": 1}))
        assert fill.symbol == "NOW"

    def test_numeric_ids_coerced_to_str(self):
        fill = parse_fill(_valid_fill(trade_id=12345, order_id=99))
        assert fill.trade_id == "12345"
        assert fill.order_id == "99"

    def test_signed_size(self):
        assert parse_fill(_valid_fill(side="BUY")).signed_size == Decimal("100")
        assert parse_fill(_valid_fill(side="SELL")).signed_size == Decimal("-100")

    @pytest.mark.parametrize(
        "mutation",
        [
            {"side": "SHORT"},
            {"size": 0},
            {"size": -100},
            {"size": "abc"},
            {"trade_time": "2026-07-01T14:59:38"},  # naive
            {"trade_time": "yesterday"},
            {"symbol": ""},
            {"sec_type": ""},
        ],
    )
    def test_bad_field_fails_loudly(self, mutation):
        with pytest.raises(TradesError):
            parse_fill(_valid_fill(**mutation))

    @pytest.mark.parametrize(
        "missing", ["trade_id", "symbol", "sec_type", "side", "size", "price", "trade_time"]
    )
    def test_missing_required_field_fails_loudly(self, missing):
        raw = _valid_fill()
        del raw[missing]
        with pytest.raises(TradesError):
            parse_fill(raw)


class TestLoadTrades:
    def test_ground_truth_fixture_loads(self):
        snap = load_trades(FIXTURE)
        assert len(snap.fills) == 15
        assert snap.period == "DAYS_30"
        buys = [f for f in snap.fills if f.side == "BUY"]
        sells = [f for f in snap.fills if f.side == "SELL"]
        assert sum(f.size for f in buys) == Decimal("1000")
        assert sum(f.size for f in sells) == Decimal("1000")
        # Per-fill realized_pnl is authoritative (R-011): sums to +458.61.
        assert sum(f.realized_pnl for f in snap.fills) == Decimal("458.61")
        # Prices parsed as Decimal, never float.
        assert all(isinstance(f.price, Decimal) for f in snap.fills)

    def test_fills_sorted_by_time(self):
        snap = load_trades(FIXTURE)
        times = [f.trade_time for f in snap.fills]
        assert times == sorted(times)

    def test_dedupe_by_trade_id(self, tmp_path):
        path = _write_snapshot(
            tmp_path / "t.json",
            [_valid_fill(), _valid_fill(), _valid_fill(trade_id="t2")],
        )
        snap = load_trades(path)
        assert [f.trade_id for f in snap.fills] == ["t1", "t2"]
        assert snap.duplicate_trade_ids == ["t1"]

    def test_overlapping_pulls_identical_output(self, tmp_path):
        """A-007: the same fills pulled twice produce identical fills."""
        fills = [_valid_fill(), _valid_fill(trade_id="t2", side="SELL")]
        single = _write_snapshot(tmp_path / "one.json", fills)
        doubled = _write_snapshot(tmp_path / "two.json", fills + fills)
        assert load_trades(single).fills == load_trades(doubled).fills

    def test_missing_file_fails(self, tmp_path):
        with pytest.raises(TradesError):
            load_trades(tmp_path / "absent.json")

    def test_invalid_json_fails(self, tmp_path):
        path = tmp_path / "t.json"
        path.write_text("{oops", encoding="utf-8")
        with pytest.raises(TradesError):
            load_trades(path)

    @pytest.mark.parametrize(
        "payload",
        [
            {"schema": "bsl-trades-2", "as_of": "2026-07-01T19:00:00Z", "trades": []},
            {"as_of": "2026-07-01T19:00:00Z", "trades": []},  # no schema
            {"schema": "bsl-trades-1", "trades": []},  # no as_of
            {"schema": "bsl-trades-1", "as_of": "2026-07-01T19:00:00", "trades": []},
            {"schema": "bsl-trades-1", "as_of": "2026-07-01T19:00:00Z", "trades": {}},
            {"schema": "bsl-trades-1", "as_of": "2026-07-01T19:00:00Z"},  # no trades
            [],
        ],
    )
    def test_malformed_snapshot_fails(self, tmp_path, payload):
        path = tmp_path / "t.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        with pytest.raises(TradesError):
            load_trades(path)

    def test_staleness_at_threshold(self, tmp_path):
        path = _write_snapshot(tmp_path / "t.json", [], as_of="2026-07-01T18:00:00Z")
        snap = load_trades(path)
        now = datetime(2026, 7, 1, 19, 0, tzinfo=timezone.utc)  # exactly 60 min
        assert snap.is_stale(now=now, stale_after=timedelta(minutes=60))
        assert not snap.is_stale(
            now=now - timedelta(seconds=1), stale_after=timedelta(minutes=60)
        )
