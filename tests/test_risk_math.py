"""D-009 test matrix for the pure risk math (Sprint 002 blueprint).

Every edge case listed in the blueprint has at least one test; the worked
reference examples are encoded exactly.
"""

from decimal import Decimal

import pytest

from bsl_coach.risk_math import (
    CHECK_CONCENTRATION,
    CHECK_HARD_CAP,
    CONCENTRATION_LIMIT,
    HARD_CAP_DOLLARS,
    InvalidInputError,
    InvalidStopError,
    NoViableSizeError,
    STATUS_CAPPED,
    STATUS_PASS,
    TIER_PCT,
    compute_size,
)

D = Decimal
NLV_4M = D("4000000")


# ---------------------------------------------------------------------------
# Worked reference examples (blueprint — encoded exactly)
# ---------------------------------------------------------------------------


class TestWorkedExamples:
    def test_now_long_base_tier_concentration_binds(self):
        """A-002: NLV $4M, base, NOW long 105.57/104.59 -> 1,894 shares,
        concentration binding."""
        r = compute_size("long", D("105.57"), D("104.59"), "base", NLV_4M, D("0"))
        assert r.stop_distance == D("0.98")
        assert r.tier_risk_dollars == D("4000.000")  # 0.10% of 4M
        assert r.risk_budget_dollars == r.tier_risk_dollars  # hard cap not hit
        assert r.shares_uncapped == 4081  # floor(4000 / 0.98)
        assert r.shares == 1894  # floor(200000 / 105.57)
        assert r.position_value == D("1894") * D("105.57")  # 199,949.58
        assert r.position_value == D("199949.58")
        assert r.binding_constraint == CHECK_CONCENTRATION
        assert r.checks[CHECK_CONCENTRATION] == STATUS_CAPPED
        assert r.checks[CHECK_HARD_CAP] == STATUS_PASS

    def test_max_tier_30m_hard_cap_binds(self):
        """A-003: max tier at NLV $30M -> tier risk $75,000 trimmed to $50,000."""
        r = compute_size("long", D("100"), D("90"), "max", D("30000000"), D("0"))
        assert r.tier_risk_dollars == D("75000.0000")
        assert r.risk_budget_dollars == HARD_CAP_DOLLARS
        assert r.shares == 5000  # floor(50000 / 10); concentration 500k < 1.5M
        assert r.binding_constraint == CHECK_HARD_CAP
        assert r.checks[CHECK_HARD_CAP] == STATUS_CAPPED
        assert r.checks[CHECK_CONCENTRATION] == STATUS_PASS

    def test_tiny_stop_distance_expensive_stock_floors_fine(self):
        """Risk $4,000, stop distance $0.005 on a $1,400 stock -> floor fine
        (800,000 uncapped; concentration then caps hard)."""
        r = compute_size("long", D("1400"), D("1399.995"), "base", NLV_4M, D("0"))
        assert r.shares_uncapped == 800000  # floor(4000 / 0.005)
        assert r.shares == 142  # floor(200000 / 1400)
        assert r.binding_constraint == CHECK_CONCENTRATION

    def test_wide_stop_expensive_stock_five_shares(self):
        """Risk $4,000, entry $1,400, stop distance $800 -> 5 shares."""
        r = compute_size("long", D("1400"), D("600"), "base", NLV_4M, D("0"))
        assert r.shares_uncapped == 5  # floor(4000 / 800)
        assert r.shares == 5  # 5 * 1400 = 7,000 << 200,000 cap
        assert r.binding_constraint is None

    def test_existing_position_leaves_partial_headroom(self):
        """Existing NOW value $150,000 at 5% cap $200,000 -> only $50,000 of
        new position value allowed."""
        r = compute_size("long", D("100"), D("99.50"), "base", NLV_4M, D("150000"))
        assert r.shares_uncapped == 8000  # floor(4000 / 0.50)
        assert r.shares == 500  # floor(50000 / 100)
        assert r.position_value == D("50000")
        assert r.binding_constraint == CHECK_CONCENTRATION


# ---------------------------------------------------------------------------
# FR-4 direction safety: stop must sit strictly on the protective side
# ---------------------------------------------------------------------------


class TestStopValidation:
    def test_long_stop_equal_entry_zero_distance(self):
        with pytest.raises(InvalidStopError):
            compute_size("long", D("100"), D("100"), "base", NLV_4M)

    def test_long_stop_above_entry(self):
        with pytest.raises(InvalidStopError):
            compute_size("long", D("100"), D("101"), "base", NLV_4M)

    def test_short_stop_equal_entry_zero_distance(self):
        with pytest.raises(InvalidStopError):
            compute_size("short", D("100"), D("100"), "base", NLV_4M)

    def test_short_stop_below_entry(self):
        with pytest.raises(InvalidStopError):
            compute_size("short", D("100"), D("99"), "base", NLV_4M)

    def test_short_happy_path(self):
        r = compute_size("short", D("100"), D("102"), "base", NLV_4M, D("0"))
        assert r.stop_distance == D("2")
        assert r.shares == 2000  # floor(4000 / 2)


# ---------------------------------------------------------------------------
# NLV and other input validation
# ---------------------------------------------------------------------------


class TestInputValidation:
    def test_zero_nlv(self):
        with pytest.raises(InvalidInputError):
            compute_size("long", D("100"), D("99"), "base", D("0"))

    def test_negative_nlv(self):
        with pytest.raises(InvalidInputError):
            compute_size("long", D("100"), D("99"), "base", D("-1000"))

    def test_absent_nlv(self):
        with pytest.raises(InvalidInputError):
            compute_size("long", D("100"), D("99"), "base", None)

    def test_float_rejected(self):
        with pytest.raises(InvalidInputError):
            compute_size("long", 105.57, D("104.59"), "base", NLV_4M)

    def test_negative_entry(self):
        with pytest.raises(InvalidInputError):
            compute_size("long", D("-100"), D("99"), "base", NLV_4M)

    def test_zero_entry(self):
        with pytest.raises(InvalidInputError):
            compute_size("long", D("0"), D("-1"), "base", NLV_4M)

    def test_negative_existing_value(self):
        with pytest.raises(InvalidInputError):
            compute_size("long", D("100"), D("99"), "base", NLV_4M, D("-1"))

    def test_unknown_tier(self):
        with pytest.raises(InvalidInputError):
            compute_size("long", D("100"), D("99"), "ultra", NLV_4M)

    def test_unknown_direction(self):
        with pytest.raises(InvalidInputError):
            compute_size("sideways", D("100"), D("99"), "base", NLV_4M)

    def test_nonfinite_rejected(self):
        with pytest.raises(InvalidInputError):
            compute_size("long", D("Infinity"), D("99"), "base", NLV_4M)


# ---------------------------------------------------------------------------
# FR-1/FR-2: tier mapping and hard cap
# ---------------------------------------------------------------------------


class TestTiersAndHardCap:
    @pytest.mark.parametrize(
        "tier,expected_risk",
        [
            ("base", D("4000.000")),  # 0.10%
            ("medium", D("6000.000")),  # 0.15%
            ("high", D("8000.000")),  # 0.20%
            ("max", D("10000.000")),  # 0.25%
        ],
    )
    def test_tier_mapping_at_4m(self, tier, expected_risk):
        r = compute_size("long", D("100"), D("99"), tier, NLV_4M, D("0"))
        assert r.tier_risk_dollars == expected_risk
        assert r.risk_budget_dollars == expected_risk

    def test_hard_cap_exactly_at_tier_boundary_not_capped(self):
        """Max tier at NLV $20M -> tier risk exactly $50,000: cap does not bind."""
        r = compute_size("long", D("100"), D("90"), "max", D("20000000"), D("0"))
        assert r.tier_risk_dollars == HARD_CAP_DOLLARS
        assert r.risk_budget_dollars == HARD_CAP_DOLLARS
        assert r.checks[CHECK_HARD_CAP] == STATUS_PASS
        assert r.binding_constraint is None

    def test_hard_cap_one_dollar_past_boundary_capped(self):
        """A hair past the boundary the cap binds and is named."""
        r = compute_size("long", D("100"), D("90"), "max", D("20000400"), D("0"))
        assert r.tier_risk_dollars > HARD_CAP_DOLLARS
        assert r.risk_budget_dollars == HARD_CAP_DOLLARS
        assert r.checks[CHECK_HARD_CAP] == STATUS_CAPPED
        assert r.binding_constraint == CHECK_HARD_CAP
        assert any("hard cap" in w for w in r.warnings)


# ---------------------------------------------------------------------------
# FR-3: floor boundaries — no float wobble
# ---------------------------------------------------------------------------


class TestFloorBoundaries:
    def test_risk_exactly_divisible(self):
        """$4,000 / $0.80 = exactly 5,000 shares."""
        r = compute_size("long", D("20"), D("19.20"), "base", NLV_4M, D("0"))
        assert r.shares_uncapped == 5000

    def test_off_by_a_hair_floors_down(self):
        """Distance a hair over $0.80 must floor to 4,999 — Decimal exactness."""
        r = compute_size("long", D("20"), D("19.1999999999"), "base", NLV_4M, D("0"))
        assert r.stop_distance == D("0.8000000001")
        assert r.shares_uncapped == 4999

    def test_blueprint_wobble_pair(self):
        """Distance 0.98 vs 0.9800000001 (blueprint's example) -> both 4081."""
        r1 = compute_size("long", D("105.57"), D("104.59"), "base", NLV_4M, D("0"))
        r2 = compute_size(
            "long", D("105.57"), D("104.5899999999"), "base", NLV_4M, D("0")
        )
        assert r1.shares_uncapped == 4081
        assert r2.shares_uncapped == 4081

    def test_off_by_a_penny(self):
        """$4,000 / $0.81 = 4,938.27 -> 4,938."""
        r = compute_size("long", D("20"), D("19.19"), "base", NLV_4M, D("0"))
        assert r.shares_uncapped == 4938


# ---------------------------------------------------------------------------
# FR-5: concentration
# ---------------------------------------------------------------------------


class TestConcentration:
    def test_exactly_at_five_percent_passes(self):
        """Position value landing exactly on 5% of NLV is allowed (not exceed)."""
        # base risk 4000, distance 2 -> 2000 shares; 2000 * 100 = 200,000 = 5%
        r = compute_size("long", D("100"), D("98"), "base", NLV_4M, D("0"))
        assert r.shares == 2000
        assert r.position_value == NLV_4M * CONCENTRATION_LIMIT
        assert r.checks[CHECK_CONCENTRATION] == STATUS_PASS
        assert r.binding_constraint is None
        assert r.concentration_pct == D("5.0000")

    def test_one_share_past_five_percent_capped(self):
        """A slightly tighter stop pushes uncapped past 5% -> capped back."""
        r = compute_size("long", D("100"), D("98.05"), "base", NLV_4M, D("0"))
        assert r.shares_uncapped == 2051  # floor(4000 / 1.95)
        assert r.shares == 2000  # floor(200000 / 100)
        assert r.checks[CHECK_CONCENTRATION] == STATUS_CAPPED
        assert r.binding_constraint == CHECK_CONCENTRATION

    def test_existing_position_exactly_at_cap_no_viable(self):
        """Existing value alone == 5% cap -> no new shares (FR-6 loud)."""
        with pytest.raises(NoViableSizeError) as exc_info:
            compute_size("long", D("100"), D("99"), "base", NLV_4M, D("200000"))
        assert "concentration" in str(exc_info.value)

    def test_existing_position_above_cap_no_viable(self):
        with pytest.raises(NoViableSizeError):
            compute_size("long", D("100"), D("99"), "base", NLV_4M, D("210000"))

    def test_concentration_counts_existing_in_pct(self):
        r = compute_size("long", D("100"), D("99.50"), "base", NLV_4M, D("150000"))
        # (50,000 new + 150,000 existing) / 4M = 5.0000%
        assert r.concentration_pct == D("5.0000")

    def test_concentration_wins_when_both_caps_bind(self):
        """Hard cap trims risk first, concentration trims shares after —
        the tighter (concentration) is named binding."""
        # NLV 30M max tier: risk 75k -> 50k (hard cap). Entry 100, stop 99.
        # uncapped = 50,000 shares -> value 5,000,000 > 5% (1,500,000).
        r = compute_size("long", D("100"), D("99"), "max", D("30000000"), D("0"))
        assert r.checks[CHECK_HARD_CAP] == STATUS_CAPPED
        assert r.checks[CHECK_CONCENTRATION] == STATUS_CAPPED
        assert r.shares == 15000  # floor(1,500,000 / 100)
        assert r.binding_constraint == CHECK_CONCENTRATION

    def test_concentration_headroom_below_one_share_no_viable(self):
        """Headroom > 0 but less than one share's cost -> no viable size."""
        # cap 200,000; existing 199,950 -> headroom 50 < entry 100
        with pytest.raises(NoViableSizeError):
            compute_size("long", D("100"), D("99"), "base", NLV_4M, D("199950"))


# ---------------------------------------------------------------------------
# FR-6: zero computed shares is loud, never a silent 0
# ---------------------------------------------------------------------------


class TestNoViableSize:
    def test_stop_too_wide_for_budget(self):
        """Risk $4,000 vs $5,000 stop distance -> zero shares -> raises."""
        with pytest.raises(NoViableSizeError) as exc_info:
            compute_size("long", D("6000"), D("1000"), "base", NLV_4M, D("0"))
        assert "NO VIABLE SIZE" in str(exc_info.value)

    def test_never_returns_zero_shares(self):
        """Any successful result has shares >= 1 by construction."""
        r = compute_size("long", D("100"), D("99"), "base", NLV_4M, D("0"))
        assert r.shares >= 1


# ---------------------------------------------------------------------------
# Result integrity
# ---------------------------------------------------------------------------


class TestResultFigures:
    def test_actual_risk_reflects_final_shares(self):
        """After concentration capping, reported risk is the actual risk."""
        r = compute_size("long", D("105.57"), D("104.59"), "base", NLV_4M, D("0"))
        assert r.risk_dollars == D("1894") * D("0.98")  # 1,856.12
        assert r.risk_pct_of_nlv == D("0.0464")

    def test_types(self):
        r = compute_size("long", D("100"), D("99"), "base", NLV_4M, D("0"))
        assert isinstance(r.shares, int)
        assert isinstance(r.position_value, Decimal)
        assert isinstance(r.risk_dollars, Decimal)

    def test_tier_table_matches_domain_doc(self):
        assert TIER_PCT["base"] == D("0.0010")
        assert TIER_PCT["medium"] == D("0.0015")
        assert TIER_PCT["high"] == D("0.0020")
        assert TIER_PCT["max"] == D("0.0025")
        assert HARD_CAP_DOLLARS == D("50000")
        assert CONCENTRATION_LIMIT == D("0.05")
