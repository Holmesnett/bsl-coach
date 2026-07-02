"""CLI behavior: flags, exit codes, --json shape, offline + snapshot paths."""

import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from bsl_coach.cli import (
    EXIT_INVALID_INPUT,
    EXIT_NO_VIABLE_SIZE,
    EXIT_OK,
    EXIT_SNAPSHOT_PROBLEM,
    main,
)
from bsl_coach.snapshot import SCHEMA

D = Decimal

WORKED_EXAMPLE = [
    "NOW",
    "--direction", "long",
    "--entry", "105.57",
    "--stop", "104.59",
    "--tier", "base",
    "--nlv", "4000000",
    "--existing-value", "0",
]


def write_snapshot(path, *, as_of=None, nlv=4000000, positions=None):
    payload = {
        "schema": SCHEMA,
        "as_of": as_of
        if as_of is not None
        else datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "nlv": nlv,
        "positions": positions if positions is not None else {},
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# A-006: offline path — fully flagged, no snapshot file, no network
# ---------------------------------------------------------------------------


class TestOfflinePath:
    def test_fully_flagged_no_snapshot_succeeds(self, tmp_path, capsys):
        code = main(WORKED_EXAMPLE + ["--snapshot", str(tmp_path / "absent.json")])
        assert code == EXIT_OK
        out = capsys.readouterr().out
        assert "1,894" in out
        assert "concentration" in out
        assert "source: flags" in out

    def test_worked_example_human_output(self, tmp_path, capsys):
        code = main(WORKED_EXAMPLE + ["--snapshot", str(tmp_path / "absent.json")])
        assert code == EXIT_OK
        out = capsys.readouterr().out
        assert "SHARES: 1,894" in out
        assert "uncapped: 4,081" in out
        assert "$199,949.58" in out
        assert "Binding constraint: concentration" in out


# ---------------------------------------------------------------------------
# A-004: direction safety exits 2 with no sizing output
# ---------------------------------------------------------------------------


class TestInvalidInput:
    def test_long_stop_at_entry_exits_2(self, tmp_path, capsys):
        code = main(
            ["NOW", "--direction", "long", "--entry", "100", "--stop", "100",
             "--tier", "base", "--nlv", "4000000", "--existing-value", "0",
             "--snapshot", str(tmp_path / "absent.json")]
        )
        assert code == EXIT_INVALID_INPUT
        captured = capsys.readouterr()
        assert "SHARES" not in captured.out
        assert captured.out.strip() == ""  # no numbers on stdout
        assert "stop" in captured.err.lower()

    def test_short_stop_below_entry_exits_2(self, tmp_path, capsys):
        code = main(
            ["NOW", "--direction", "short", "--entry", "100", "--stop", "99",
             "--tier", "base", "--nlv", "4000000", "--existing-value", "0",
             "--snapshot", str(tmp_path / "absent.json")]
        )
        assert code == EXIT_INVALID_INPUT
        assert "SHARES" not in capsys.readouterr().out

    def test_zero_nlv_exits_2(self, tmp_path, capsys):
        code = main(
            ["NOW", "--direction", "long", "--entry", "100", "--stop", "99",
             "--tier", "base", "--nlv", "0", "--existing-value", "0",
             "--snapshot", str(tmp_path / "absent.json")]
        )
        assert code == EXIT_INVALID_INPUT

    def test_bad_tier_rejected_by_argparse(self):
        with pytest.raises(SystemExit) as exc_info:
            main(["NOW", "--direction", "long", "--entry", "100", "--stop", "99",
                  "--tier", "ultra", "--nlv", "4000000"])
        assert exc_info.value.code == 2

    def test_non_numeric_entry_rejected_by_argparse(self):
        with pytest.raises(SystemExit) as exc_info:
            main(["NOW", "--direction", "long", "--entry", "abc", "--stop", "99",
                  "--tier", "base", "--nlv", "4000000"])
        assert exc_info.value.code == 2


# ---------------------------------------------------------------------------
# A-005: no viable size exits 3 loudly, never prints 0 shares
# ---------------------------------------------------------------------------


class TestNoViableSize:
    def test_exits_3_with_message(self, tmp_path, capsys):
        code = main(
            ["XYZ", "--direction", "long", "--entry", "6000", "--stop", "1000",
             "--tier", "base", "--nlv", "4000000", "--existing-value", "0",
             "--snapshot", str(tmp_path / "absent.json")]
        )
        assert code == EXIT_NO_VIABLE_SIZE
        captured = capsys.readouterr()
        assert "NO VIABLE SIZE" in captured.err
        assert "SHARES: 0" not in captured.out
        assert captured.out.strip() == ""

    def test_existing_at_cap_exits_3(self, tmp_path, capsys):
        code = main(
            ["NOW", "--direction", "long", "--entry", "100", "--stop", "99",
             "--tier", "base", "--nlv", "4000000", "--existing-value", "200000",
             "--snapshot", str(tmp_path / "absent.json")]
        )
        assert code == EXIT_NO_VIABLE_SIZE
        assert "NO VIABLE SIZE" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# A-007: snapshot path — fresh, stale, malformed
# ---------------------------------------------------------------------------


class TestSnapshotPath:
    def test_fresh_snapshot_supplies_nlv_and_existing(self, tmp_path, capsys):
        snap = write_snapshot(
            tmp_path / "snap.json", nlv=4000000, positions={"NOW": 150000}
        )
        code = main(
            ["NOW", "--direction", "long", "--entry", "100", "--stop", "99.50",
             "--tier", "base", "--snapshot", str(snap)]
        )
        assert code == EXIT_OK
        out = capsys.readouterr().out
        assert "SHARES: 500" in out  # blueprint worked example 5
        assert "snapshot" in out  # NLV source names the snapshot

    def test_stale_snapshot_warns_with_age_still_computes(self, tmp_path, capsys):
        old = (datetime.now(timezone.utc) - timedelta(hours=3)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        snap = write_snapshot(tmp_path / "snap.json", as_of=old, nlv=4000000)
        code = main(
            ["NOW", "--direction", "long", "--entry", "105.57", "--stop", "104.59",
             "--tier", "base", "--snapshot", str(snap)]
        )
        assert code == EXIT_OK
        out = capsys.readouterr().out
        assert "STALE SNAPSHOT" in out
        assert "180 minutes" in out  # names the age
        assert "SHARES: 1,894" in out  # still computes

    def test_malformed_snapshot_exits_4(self, tmp_path, capsys):
        bad = tmp_path / "snap.json"
        bad.write_text("{broken", encoding="utf-8")
        code = main(
            ["NOW", "--direction", "long", "--entry", "100", "--stop", "99",
             "--tier", "base", "--snapshot", str(bad)]
        )
        assert code == EXIT_SNAPSHOT_PROBLEM
        assert "SNAPSHOT ERROR" in capsys.readouterr().err

    def test_missing_snapshot_when_needed_exits_4(self, tmp_path, capsys):
        code = main(
            ["NOW", "--direction", "long", "--entry", "100", "--stop", "99",
             "--tier", "base", "--snapshot", str(tmp_path / "absent.json")]
        )
        assert code == EXIT_SNAPSHOT_PROBLEM

    def test_flags_override_snapshot(self, tmp_path, capsys):
        snap = write_snapshot(
            tmp_path / "snap.json", nlv=1000000, positions={"NOW": 999999}
        )
        code = main(WORKED_EXAMPLE + ["--snapshot", str(snap)])
        assert code == EXIT_OK
        out = capsys.readouterr().out
        assert "source: flags" in out
        assert "SHARES: 1,894" in out  # flag NLV 4M used, not snapshot 1M

    def test_negative_snapshot_position_uses_abs_with_warning(self, tmp_path, capsys):
        snap = write_snapshot(
            tmp_path / "snap.json", nlv=4000000, positions={"NOW": -150000}
        )
        code = main(
            ["NOW", "--direction", "long", "--entry", "100", "--stop", "99.50",
             "--tier", "base", "--snapshot", str(snap)]
        )
        assert code == EXIT_OK
        out = capsys.readouterr().out
        assert "SHARES: 500" in out
        assert "negative" in out

    def test_missing_existing_no_snapshot_warns_assumes_zero(self, tmp_path, capsys):
        code = main(
            ["NOW", "--direction", "long", "--entry", "105.57", "--stop", "104.59",
             "--tier", "base", "--nlv", "4000000",
             "--snapshot", str(tmp_path / "absent.json")]
        )
        assert code == EXIT_OK
        out = capsys.readouterr().out
        assert "assuming $0 existing exposure" in out


# ---------------------------------------------------------------------------
# A-009: --json is valid JSON and semantically matches human output
# ---------------------------------------------------------------------------


class TestJsonOutput:
    def test_json_parses_and_matches_worked_example(self, tmp_path, capsys):
        code = main(
            WORKED_EXAMPLE + ["--json", "--snapshot", str(tmp_path / "absent.json")]
        )
        assert code == EXIT_OK
        payload = json.loads(capsys.readouterr().out)
        assert payload["symbol"] == "NOW"
        assert payload["shares"] == 1894
        assert payload["shares_uncapped"] == 4081
        assert D(payload["position_value"]) == D("199949.58")
        assert D(payload["risk_dollars"]) == D("1856.12")
        assert payload["binding_constraint"] == "concentration"
        assert payload["checks"]["concentration"] == "capped"
        assert payload["checks"]["hard_cap"] == "pass"
        assert payload["nlv_source"] == "flags"

    def test_json_semantically_matches_human(self, tmp_path, capsys):
        args = WORKED_EXAMPLE + ["--snapshot", str(tmp_path / "absent.json")]
        assert main(args + ["--json"]) == EXIT_OK
        payload = json.loads(capsys.readouterr().out)
        assert main(args) == EXIT_OK
        human = capsys.readouterr().out
        # Every headline JSON figure appears in the human rendering.
        assert f"{payload['shares']:,}" in human
        assert f"{payload['shares_uncapped']:,}" in human
        assert f"{D(payload['position_value']):,.2f}" in human
        assert f"{D(payload['risk_dollars']):,.2f}" in human
        assert payload["binding_constraint"] in human
        assert payload["risk_pct_of_nlv"] in human
        assert payload["concentration_pct"] in human
