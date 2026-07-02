"""Registry tests — D-018 tagging system (FR-1..FR-3)."""

import json
from datetime import date, datetime, timezone
from decimal import Decimal

import pytest

from bsl_coach.registry import (
    Registry,
    RegistryEntry,
    RegistryError,
    add_entry,
    load_registry,
    next_id,
    save_registry,
    tag,
    untag,
)


def _write(path, payload):
    path.write_text(json.dumps(payload), encoding="utf-8")


VALID_ENTRY = {
    "id": "2026-07-01-NOW-1",
    "symbol": "NOW",
    "direction": "long",
    "registered_at": "2026-07-01T14:55:00Z",
    "entry": "105.57",
    "stop": "104.59",
    "tier": "base",
    "shares_sized": 1602,
    "status": "active",
    "note": "",
}


class TestLoad:
    def test_missing_file_is_empty_registry(self, tmp_path):
        reg = load_registry(tmp_path / "bsl_registry.json")
        assert reg.entries == []

    def test_round_trip(self, tmp_path):
        path = tmp_path / "bsl_registry.json"
        _write(path, {"schema": "bsl-registry-1", "entries": [VALID_ENTRY]})
        reg = load_registry(path)
        assert len(reg.entries) == 1
        e = reg.entries[0]
        assert e.id == "2026-07-01-NOW-1"
        assert e.symbol == "NOW"
        assert e.entry == Decimal("105.57")
        assert e.stop == Decimal("104.59")
        assert e.shares_sized == 1602
        assert e.registered_at == datetime(2026, 7, 1, 14, 55, tzinfo=timezone.utc)
        save_registry(reg)
        again = load_registry(path)
        assert again.entries == reg.entries

    def test_registered_et_date(self, tmp_path):
        # 2026-07-02T01:30Z is still ET 2026-07-01 (D-021).
        entry = dict(VALID_ENTRY, registered_at="2026-07-02T01:30:00Z")
        path = tmp_path / "r.json"
        _write(path, {"schema": "bsl-registry-1", "entries": [entry]})
        assert load_registry(path).entries[0].registered_et_date == date(2026, 7, 1)

    def test_manual_entry_null_sizing_fields_ok(self, tmp_path):
        entry = {
            "id": "2026-07-01-ABC-1",
            "symbol": "ABC",
            "direction": "long",
            "registered_at": "2026-07-01T14:55:00Z",
            "status": "active",
        }
        path = tmp_path / "r.json"
        _write(path, {"schema": "bsl-registry-1", "entries": [entry]})
        e = load_registry(path).entries[0]
        assert e.entry is None and e.stop is None
        assert e.tier is None and e.shares_sized is None

    @pytest.mark.parametrize(
        "mutation",
        [
            {"direction": "sideways"},
            {"status": "wat"},
            {"registered_at": "not-a-date"},
            {"registered_at": "2026-07-01T14:55:00"},  # naive
            {"shares_sized": "1602"},
            {"entry": "abc"},
            {"id": ""},
            {"symbol": ""},
        ],
    )
    def test_malformed_entry_fails_loudly(self, tmp_path, mutation):
        entry = dict(VALID_ENTRY, **mutation)
        path = tmp_path / "r.json"
        _write(path, {"schema": "bsl-registry-1", "entries": [entry]})
        with pytest.raises(RegistryError):
            load_registry(path)

    def test_wrong_schema_fails(self, tmp_path):
        path = tmp_path / "r.json"
        _write(path, {"schema": "bsl-registry-2", "entries": []})
        with pytest.raises(RegistryError):
            load_registry(path)

    def test_invalid_json_fails(self, tmp_path):
        path = tmp_path / "r.json"
        path.write_text("{not json", encoding="utf-8")
        with pytest.raises(RegistryError):
            load_registry(path)

    def test_duplicate_ids_fail(self, tmp_path):
        path = tmp_path / "r.json"
        _write(path, {"schema": "bsl-registry-1", "entries": [VALID_ENTRY, VALID_ENTRY]})
        with pytest.raises(RegistryError):
            load_registry(path)


class TestAddTagUntag:
    def test_add_entry_persists_and_ids_by_et_date(self, tmp_path):
        reg = Registry(entries=[], path=tmp_path / "r.json")
        created = add_entry(
            reg,
            symbol="now",
            direction="long",
            registered_at=datetime(2026, 7, 2, 1, 30, tzinfo=timezone.utc),  # ET 07-01
            entry=Decimal("105.57"),
            stop=Decimal("104.59"),
            tier="base",
            shares_sized=1602,
        )
        assert created.id == "2026-07-01-NOW-1"
        assert created.symbol == "NOW"
        assert load_registry(reg.path).entries == [created]

    def test_next_id_increments(self, tmp_path):
        reg = Registry(entries=[], path=tmp_path / "r.json")
        day = date(2026, 7, 1)
        add_entry(reg, symbol="NOW", direction="long",
                  registered_at=datetime(2026, 7, 1, 14, 55, tzinfo=timezone.utc))
        assert next_id(reg, "NOW", day) == "2026-07-01-NOW-2"

    def test_tag_with_date_registers_at_et_midnight(self, tmp_path):
        reg = Registry(entries=[], path=tmp_path / "r.json")
        created = tag(reg, "NOW", et_date=date(2026, 7, 1), note="backfill")
        assert created.registered_et_date == date(2026, 7, 1)
        # 00:00 ET on 2026-07-01 (EDT, UTC-4) == 04:00Z
        assert created.registered_at == datetime(2026, 7, 1, 4, 0, tzinfo=timezone.utc)
        assert created.entry is None and created.shares_sized is None
        assert created.note == "backfill"

    def test_tag_without_date_uses_now(self, tmp_path):
        reg = Registry(entries=[], path=tmp_path / "r.json")
        now = datetime(2026, 7, 1, 18, 0, tzinfo=timezone.utc)
        created = tag(reg, "NOW", now=now)
        assert created.registered_at == now
        assert created.note == "manual tag"

    def test_untag_removes_and_persists(self, tmp_path):
        reg = Registry(entries=[], path=tmp_path / "r.json")
        created = tag(reg, "NOW", et_date=date(2026, 7, 1))
        removed = untag(reg, created.id)
        assert removed.id == created.id
        assert load_registry(reg.path).entries == []

    def test_untag_unknown_id_fails_loudly(self, tmp_path):
        reg = Registry(entries=[], path=tmp_path / "r.json")
        with pytest.raises(RegistryError):
            untag(reg, "nope")

    def test_add_entry_rejects_bad_direction(self, tmp_path):
        reg = Registry(entries=[], path=tmp_path / "r.json")
        with pytest.raises(RegistryError):
            add_entry(reg, symbol="NOW", direction="up")

    def test_add_entry_rejects_naive_datetime(self, tmp_path):
        reg = Registry(entries=[], path=tmp_path / "r.json")
        with pytest.raises(RegistryError):
            add_entry(
                reg, symbol="NOW", direction="long",
                registered_at=datetime(2026, 7, 1, 14, 55),
            )
