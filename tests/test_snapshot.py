"""Snapshot loading: missing / stale / malformed handling (Sprint 002)."""

import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from bsl_coach.snapshot import (
    DEFAULT_STALE_AFTER,
    SCHEMA,
    SnapshotError,
    load_snapshot,
)

D = Decimal


def write_snapshot(path, *, schema=SCHEMA, as_of=None, nlv=3890000, positions=None):
    payload = {
        "schema": schema,
        "as_of": as_of
        if as_of is not None
        else datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "nlv": nlv,
        "positions": positions if positions is not None else {"NOW": 105570.0},
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


class TestFreshSnapshot:
    def test_loads_values_as_decimal(self, tmp_path):
        p = write_snapshot(tmp_path / "snap.json")
        snap = load_snapshot(p)
        assert snap.nlv == D("3890000")
        assert isinstance(snap.nlv, Decimal)
        assert snap.positions["NOW"] == D("105570.0")
        assert isinstance(snap.positions["NOW"], Decimal)
        assert not snap.is_stale()

    def test_symbols_normalized_upper(self, tmp_path):
        p = write_snapshot(tmp_path / "snap.json", positions={"now": 1000})
        snap = load_snapshot(p)
        assert "NOW" in snap.positions

    def test_positions_optional(self, tmp_path):
        p = tmp_path / "snap.json"
        p.write_text(
            json.dumps(
                {"schema": SCHEMA, "as_of": "2100-01-01T00:00:00Z", "nlv": 1000}
            )
        )
        snap = load_snapshot(p)
        assert snap.positions == {}


class TestStaleness:
    def test_stale_beyond_threshold(self, tmp_path):
        old = (datetime.now(timezone.utc) - timedelta(hours=2)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        snap = load_snapshot(write_snapshot(tmp_path / "snap.json", as_of=old))
        assert snap.is_stale()
        assert snap.age() >= timedelta(hours=2)

    def test_stale_fires_exactly_at_threshold(self, tmp_path):
        """Blueprint: the staleness warning fires AT the threshold."""
        as_of = datetime(2026, 7, 1, 12, 0, 0, tzinfo=timezone.utc)
        snap = load_snapshot(
            write_snapshot(
                tmp_path / "snap.json", as_of=as_of.strftime("%Y-%m-%dT%H:%M:%SZ")
            )
        )
        exactly_at = as_of + DEFAULT_STALE_AFTER
        assert snap.is_stale(now=exactly_at)
        just_before = exactly_at - timedelta(seconds=1)
        assert not snap.is_stale(now=just_before)

    def test_custom_threshold(self, tmp_path):
        old = (datetime.now(timezone.utc) - timedelta(minutes=10)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        snap = load_snapshot(write_snapshot(tmp_path / "snap.json", as_of=old))
        assert snap.is_stale(stale_after=timedelta(minutes=5))
        assert not snap.is_stale(stale_after=timedelta(minutes=30))


class TestMalformed:
    def test_missing_file(self, tmp_path):
        with pytest.raises(SnapshotError):
            load_snapshot(tmp_path / "nope.json")

    def test_invalid_json(self, tmp_path):
        p = tmp_path / "snap.json"
        p.write_text("{not json", encoding="utf-8")
        with pytest.raises(SnapshotError):
            load_snapshot(p)

    def test_not_an_object(self, tmp_path):
        p = tmp_path / "snap.json"
        p.write_text("[1, 2, 3]", encoding="utf-8")
        with pytest.raises(SnapshotError):
            load_snapshot(p)

    def test_wrong_schema(self, tmp_path):
        p = write_snapshot(tmp_path / "snap.json", schema="bsl-snapshot-99")
        with pytest.raises(SnapshotError, match="schema"):
            load_snapshot(p)

    def test_missing_schema(self, tmp_path):
        p = tmp_path / "snap.json"
        p.write_text(json.dumps({"as_of": "2026-07-01T00:00:00Z", "nlv": 1}))
        with pytest.raises(SnapshotError):
            load_snapshot(p)

    def test_missing_as_of(self, tmp_path):
        p = tmp_path / "snap.json"
        p.write_text(json.dumps({"schema": SCHEMA, "nlv": 1}))
        with pytest.raises(SnapshotError, match="as_of"):
            load_snapshot(p)

    def test_bad_as_of(self, tmp_path):
        p = write_snapshot(tmp_path / "snap.json", as_of="yesterday-ish")
        with pytest.raises(SnapshotError, match="as_of"):
            load_snapshot(p)

    def test_naive_as_of_rejected(self, tmp_path):
        p = write_snapshot(tmp_path / "snap.json", as_of="2026-07-01T12:00:00")
        with pytest.raises(SnapshotError, match="timezone"):
            load_snapshot(p)

    def test_missing_nlv(self, tmp_path):
        p = tmp_path / "snap.json"
        p.write_text(json.dumps({"schema": SCHEMA, "as_of": "2026-07-01T00:00:00Z"}))
        with pytest.raises(SnapshotError, match="nlv"):
            load_snapshot(p)

    def test_zero_nlv(self, tmp_path):
        p = write_snapshot(tmp_path / "snap.json", nlv=0)
        with pytest.raises(SnapshotError, match="nlv"):
            load_snapshot(p)

    def test_non_numeric_nlv(self, tmp_path):
        p = write_snapshot(tmp_path / "snap.json", nlv="lots")
        with pytest.raises(SnapshotError):
            load_snapshot(p)

    def test_positions_not_object(self, tmp_path):
        p = tmp_path / "snap.json"
        p.write_text(
            json.dumps(
                {
                    "schema": SCHEMA,
                    "as_of": "2026-07-01T00:00:00Z",
                    "nlv": 1000,
                    "positions": [1, 2],
                }
            )
        )
        with pytest.raises(SnapshotError, match="positions"):
            load_snapshot(p)

    def test_non_numeric_position_value(self, tmp_path):
        p = write_snapshot(tmp_path / "snap.json", positions={"NOW": "many"})
        with pytest.raises(SnapshotError):
            load_snapshot(p)
