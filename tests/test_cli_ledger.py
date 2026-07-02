"""CLI tests — bsl-ledger report/tag/untag/list and bsl-size --register."""

import json
from decimal import Decimal
from pathlib import Path

import pytest

from bsl_coach.cli import main as size_main
from bsl_coach.cli_ledger import main as ledger_main

FIXTURE = Path(__file__).parent / "fixtures" / "now_2026_07_01_fills.json"
NLV = "3819828.43"


def write_account(tmp_path, nlv=NLV, available_funds="2100000", positions=None):
    path = tmp_path / "account_snapshot.json"
    payload = {
        "schema": "bsl-snapshot-1",
        "as_of": "2026-07-02T01:30:00Z",
        "nlv": nlv,
        "positions": positions or {},
    }
    if available_funds is not None:
        payload["available_funds"] = available_funds
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def write_registry(tmp_path, symbols=(("NOW", "2026-07-01T14:55:00Z"),)):
    path = tmp_path / "bsl_registry.json"
    entries = [
        {
            "id": f"2026-07-01-{sym}-1",
            "symbol": sym,
            "direction": "long",
            "registered_at": at,
            "entry": None,
            "stop": None,
            "tier": None,
            "shares_sized": None,
            "status": "active",
            "note": "",
        }
        for sym, at in symbols
    ]
    path.write_text(
        json.dumps({"schema": "bsl-registry-1", "entries": entries}), encoding="utf-8"
    )
    return path


def write_trades(tmp_path, trades, as_of="2026-07-02T01:30:00Z", name="trades.json"):
    path = tmp_path / name
    path.write_text(
        json.dumps(
            {"schema": "bsl-trades-1", "as_of": as_of, "period": "DAYS_30", "trades": trades}
        ),
        encoding="utf-8",
    )
    return path


def report_args(trades, account, registry, *extra):
    return [
        "report",
        "--trades-snapshot", str(trades),
        "--account-snapshot", str(account),
        "--registry", str(registry),
        *extra,
    ]


LOSS_FILLS = [
    {
        "trade_id": "L1", "symbol": "NOW", "sec_type": "STK", "side": "BUY",
        "size": 100, "price": "105.57", "trade_time": "2026-07-01T14:59:00Z",
    },
    {
        "trade_id": "L2", "symbol": "NOW", "sec_type": "STK", "side": "SELL",
        "size": 100, "price": "100.00", "trade_time": "2026-07-01T18:55:00Z",
        "realized_pnl": "-38198.28",
    },
]


class TestReportGroundTruth:
    """A-002 end to end through the CLI."""

    def test_now_report_human(self, tmp_path, capsys):
        rc = ledger_main(
            report_args(FIXTURE, write_account(tmp_path), write_registry(tmp_path))
        )
        out = capsys.readouterr().out
        assert rc == 0
        assert "+$458.61" in out
        assert "ET day 2026-07-01" in out  # bucketed to ET 2026-07-01 via as_of
        assert "Closed episodes (1)" in out
        assert "NOW long 1000 sh" in out
        assert "usage 0.0%" in out
        assert "OK" in out

    def test_now_report_json(self, tmp_path, capsys):
        rc = ledger_main(
            report_args(
                FIXTURE, write_account(tmp_path), write_registry(tmp_path), "--json"
            )
        )
        out = capsys.readouterr().out
        assert rc == 0
        payload = json.loads(out)  # A-009: valid JSON
        assert payload["today_et"] == "2026-07-01"
        assert len(payload["closed_episodes"]) == 1
        ep = payload["closed_episodes"][0]
        assert abs(Decimal(ep["realized_pnl"]) - Decimal("458.61")) <= Decimal("0.01")
        assert ep["closed_et"] == "2026-07-01"
        assert ep["symbol"] == "NOW"
        budgets = {b["name"]: b for b in payload["budgets"]}
        assert budgets["daily"]["cap"] == "38198.28"
        assert budgets["daily"]["usage_pct"] == "0.0"
        assert budgets["daily"]["status"] == "OK"
        assert payload["standdown"] is False
        assert payload["review"] == []

    def test_json_semantically_matches_human(self, tmp_path, capsys):
        """A-009: same inputs -> same figures in both renderings."""
        account, registry = write_account(tmp_path), write_registry(tmp_path)
        assert ledger_main(report_args(FIXTURE, account, registry, "--json")) == 0
        payload = json.loads(capsys.readouterr().out)
        assert ledger_main(report_args(FIXTURE, account, registry)) == 0
        human = capsys.readouterr().out
        for b in payload["budgets"]:
            assert f"cap ${Decimal(b['cap']):,.2f}" in human
            assert f"usage {b['usage_pct']}%" in human
            assert b["status"] in human
        for w in payload["warnings"]:
            assert w in human  # every warning verbatim in both


class TestReportExitCodes:
    def test_missing_trades_snapshot_exit_4(self, tmp_path, capsys):
        rc = ledger_main(
            report_args(tmp_path / "absent.json", write_account(tmp_path), write_registry(tmp_path))
        )
        assert rc == 4
        assert "TRADES SNAPSHOT ERROR" in capsys.readouterr().err

    def test_malformed_trades_snapshot_exit_4(self, tmp_path, capsys):
        bad = tmp_path / "bad.json"
        bad.write_text("{oops", encoding="utf-8")
        rc = ledger_main(
            report_args(bad, write_account(tmp_path), write_registry(tmp_path))
        )
        assert rc == 4

    def test_missing_account_snapshot_without_nlv_exit_4(self, tmp_path, capsys):
        rc = ledger_main(
            report_args(FIXTURE, tmp_path / "absent.json", write_registry(tmp_path))
        )
        assert rc == 4
        assert "ACCOUNT SNAPSHOT ERROR" in capsys.readouterr().err

    def test_zero_nlv_in_snapshot_exit_4(self, tmp_path, capsys):
        rc = ledger_main(
            report_args(FIXTURE, write_account(tmp_path, nlv="0"), write_registry(tmp_path))
        )
        assert rc == 4  # never divide-by-zero

    def test_zero_nlv_flag_exit_4(self, tmp_path, capsys):
        rc = ledger_main(
            report_args(
                FIXTURE, tmp_path / "absent.json", write_registry(tmp_path), "--nlv", "0"
            )
        )
        assert rc == 4
        assert "INVALID NLV" in capsys.readouterr().err

    def test_nlv_flag_overrides_missing_account_snapshot(self, tmp_path, capsys):
        rc = ledger_main(
            report_args(
                FIXTURE, tmp_path / "absent.json", write_registry(tmp_path), "--nlv", NLV
            )
        )
        out = capsys.readouterr().out
        assert rc == 0
        assert "source: flags" in out
        assert "available funds n/a" in out  # margin line still informational

    def test_malformed_registry_exit_4(self, tmp_path, capsys):
        bad = tmp_path / "reg.json"
        bad.write_text(json.dumps({"schema": "wrong"}), encoding="utf-8")
        rc = ledger_main(report_args(FIXTURE, write_account(tmp_path), bad))
        assert rc == 4
        assert "REGISTRY ERROR" in capsys.readouterr().err

    def test_standdown_exit_5_report_still_prints(self, tmp_path, capsys):
        """FR-9: exit 5 detects stand-down; nothing is blocked (D-003)."""
        trades = write_trades(tmp_path, LOSS_FILLS)
        rc = ledger_main(
            report_args(trades, write_account(tmp_path), write_registry(tmp_path))
        )
        out = capsys.readouterr().out
        assert rc == 5
        assert "STAND DOWN" in out
        assert "STOP FOR THE DAY" in out
        assert "usage 100.0%" in out

    def test_standdown_json_exit_5(self, tmp_path, capsys):
        trades = write_trades(tmp_path, LOSS_FILLS)
        rc = ledger_main(
            report_args(trades, write_account(tmp_path), write_registry(tmp_path), "--json")
        )
        payload = json.loads(capsys.readouterr().out)
        assert rc == 5
        assert payload["standdown"] is True
        assert any("STOP FOR THE DAY" in w for w in payload["warnings"])


class TestReportBehavior:
    def test_today_override_moves_buckets(self, tmp_path, capsys):
        # With --today on a later date, the NOW P&L leaves TODAY but stays MTD.
        rc = ledger_main(
            report_args(
                FIXTURE, write_account(tmp_path), write_registry(tmp_path),
                "--today", "2026-07-02", "--json",
            )
        )
        payload = json.loads(capsys.readouterr().out)
        assert rc == 0
        budgets = {b["name"]: b for b in payload["budgets"]}
        assert Decimal(budgets["daily"]["realized_pnl"]) == 0
        assert abs(Decimal(budgets["monthly"]["realized_pnl"]) - Decimal("458.61")) <= Decimal("0.01")

    def test_overlapping_pulls_identical_ledger_output(self, tmp_path, capsys):
        """A-007 at the CLI level: same fills twice -> same episodes/budgets."""
        fills = json.loads(FIXTURE.read_text())["trades"]
        once = write_trades(tmp_path, fills, name="once.json")
        twice = write_trades(tmp_path, fills + fills, name="twice.json")
        account, registry = write_account(tmp_path), write_registry(tmp_path)
        assert ledger_main(report_args(once, account, registry, "--json")) == 0
        p1 = json.loads(capsys.readouterr().out)
        assert ledger_main(report_args(twice, account, registry, "--json")) == 0
        p2 = json.loads(capsys.readouterr().out)
        for key in ("budgets", "closed_episodes", "open_positions", "review", "standdown"):
            assert p1[key] == p2[key]

    def test_review_list_in_output(self, tmp_path, capsys):
        """A-006: OPT + pre-registration + unregistered fills surface for review."""
        fills = [
            {
                "trade_id": "r1", "symbol": "NOW", "sec_type": "OPT", "side": "BUY",
                "size": 5, "price": "2.50", "trade_time": "2026-07-01T15:00:00Z",
                "realized_pnl": "1000",
            },
            {
                "trade_id": "r2", "symbol": "NOW", "sec_type": "STK", "side": "BUY",
                "size": 100, "price": "104.00", "trade_time": "2026-06-30T15:00:00Z",
                "realized_pnl": "500",
            },
            {
                "trade_id": "r3", "symbol": "MU", "sec_type": "STK", "side": "SELL",
                "size": 50, "price": "300.00", "trade_time": "2026-07-01T15:00:00Z",
                "realized_pnl": "250",
            },
        ]
        trades = write_trades(tmp_path, fills)
        rc = ledger_main(
            report_args(trades, write_account(tmp_path), write_registry(tmp_path), "--json")
        )
        payload = json.loads(capsys.readouterr().out)
        assert rc == 0
        assert len(payload["review"]) == 3
        # None of it entered P&L (FR-4 / A-006).
        assert all(Decimal(b["realized_pnl"]) == 0 for b in payload["budgets"])
        assert payload["closed_episodes"] == []

    def test_stale_trades_snapshot_warns(self, tmp_path, capsys):
        trades = write_trades(tmp_path, [], as_of="2020-01-01T12:00:00Z")
        rc = ledger_main(
            report_args(
                trades, write_account(tmp_path), write_registry(tmp_path),
                "--today", "2026-07-01",
            )
        )
        out = capsys.readouterr().out
        assert rc == 0
        assert "STALE TRADES SNAPSHOT" in out

    def test_open_position_shown_with_market_value_info(self, tmp_path, capsys):
        fills = [
            {
                "trade_id": "o1", "symbol": "NOW", "sec_type": "STK", "side": "BUY",
                "size": 100, "price": "105.57", "trade_time": "2026-07-01T15:00:00Z",
            }
        ]
        trades = write_trades(tmp_path, fills)
        account = write_account(tmp_path, positions={"NOW": "10557.00"})
        rc = ledger_main(report_args(trades, account, write_registry(tmp_path)))
        out = capsys.readouterr().out
        assert rc == 0
        assert "Open registered positions (1)" in out
        assert "open 100 sh" in out
        assert "unrealized info only, never in caps" in out


class TestTagUntagList:
    """A-003 round trip."""

    def test_tag_list_untag_round_trip(self, tmp_path, capsys):
        registry = tmp_path / "reg.json"
        rc = ledger_main(
            ["tag", "now", "--date", "2026-07-01", "--note", "manual", "--registry", str(registry)]
        )
        out = capsys.readouterr().out
        assert rc == 0
        assert "TAGGED: 2026-07-01-NOW-1" in out

        rc = ledger_main(["list", "--registry", str(registry)])
        out = capsys.readouterr().out
        assert rc == 0
        assert "2026-07-01-NOW-1" in out
        assert "manual tag (no sizing context)" in out

        rc = ledger_main(["untag", "2026-07-01-NOW-1", "--registry", str(registry)])
        out = capsys.readouterr().out
        assert rc == 0
        assert "UNTAGGED" in out

        rc = ledger_main(["list", "--registry", str(registry)])
        assert rc == 0
        assert "(empty)" in capsys.readouterr().out

    def test_untag_unknown_id_exit_4(self, tmp_path, capsys):
        rc = ledger_main(["untag", "nope", "--registry", str(tmp_path / "reg.json")])
        assert rc == 4
        assert "REGISTRY ERROR" in capsys.readouterr().err

    def test_list_json(self, tmp_path, capsys):
        registry = write_registry(tmp_path)
        rc = ledger_main(["list", "--registry", str(registry), "--json"])
        payload = json.loads(capsys.readouterr().out)
        assert rc == 0
        assert payload[0]["symbol"] == "NOW"
        assert payload[0]["registered_et_date"] == "2026-07-01"


class TestSizeRegister:
    """FR-2 / A-003 — --register writes on exit 0 only."""

    SIZE_ARGS = [
        "NOW", "--direction", "long", "--entry", "105.57", "--stop", "104.59",
        "--tier", "base", "--nlv", NLV, "--existing-value", "0",
    ]

    def test_register_appends_entry(self, tmp_path, capsys):
        registry = tmp_path / "reg.json"
        rc = size_main(self.SIZE_ARGS + ["--register", "--registry", str(registry)])
        out = capsys.readouterr().out
        assert rc == 0
        assert "REGISTERED:" in out
        assert registry.exists()
        data = json.loads(registry.read_text())
        assert len(data["entries"]) == 1
        e = data["entries"][0]
        assert e["symbol"] == "NOW"
        assert e["direction"] == "long"
        assert e["entry"] == "105.57"
        assert e["stop"] == "104.59"
        assert e["tier"] == "base"
        assert e["shares_sized"] > 0
        assert e["status"] == "active"
        # And bsl-ledger list sees it (A-003).
        rc = ledger_main(["list", "--registry", str(registry)])
        assert rc == 0
        assert "NOW" in capsys.readouterr().out

    def test_register_json_carries_id(self, tmp_path, capsys):
        registry = tmp_path / "reg.json"
        rc = size_main(
            self.SIZE_ARGS + ["--register", "--registry", str(registry), "--json"]
        )
        payload = json.loads(capsys.readouterr().out)
        assert rc == 0
        assert payload["registered_id"] is not None
        assert payload["registered_id"].endswith("-NOW-1")

    def test_without_register_never_writes(self, tmp_path, capsys):
        registry = tmp_path / "reg.json"
        rc = size_main(self.SIZE_ARGS + ["--registry", str(registry)])
        assert rc == 0
        assert not registry.exists()

    def test_failed_sizing_never_registers(self, tmp_path, capsys):
        registry = tmp_path / "reg.json"
        bad = [
            "NOW", "--direction", "long", "--entry", "105.57", "--stop", "106.00",
            "--tier", "base", "--nlv", NLV, "--existing-value", "0",
            "--register", "--registry", str(registry),
        ]
        rc = size_main(bad)
        assert rc == 2  # invalid stop for a long
        assert not registry.exists()
