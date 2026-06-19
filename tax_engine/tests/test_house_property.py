import pytest
from conftest import RULES

from tax_engine.house_property import compute_house_property_income
from tax_engine.models import HouseProperty

HP_RULES = RULES["house_property"]


def test_self_occupied_interest_capped_at_200000_post_1999_loan_old_regime():
    properties = [
        HouseProperty(
            is_self_occupied=True, interest_paid=250000, loan_post_1999_for_acquisition=True
        )
    ]
    income, warnings = compute_house_property_income(properties, "old", RULES)
    assert income == pytest.approx(-200000)
    assert warnings == []


def test_self_occupied_interest_capped_at_30000_other_loan_old_regime():
    properties = [
        HouseProperty(
            is_self_occupied=True, interest_paid=50000, loan_post_1999_for_acquisition=False
        )
    ]
    income, warnings = compute_house_property_income(properties, "old", RULES)
    assert income == pytest.approx(-30000)


def test_self_occupied_interest_disallowed_in_new_regime():
    properties = [
        HouseProperty(
            is_self_occupied=True, interest_paid=250000, loan_post_1999_for_acquisition=True
        )
    ]
    income, warnings = compute_house_property_income(properties, "new", RULES)
    assert income == pytest.approx(0)


def test_let_out_income_computed_with_standard_deduction_and_interest():
    properties = [
        HouseProperty(
            is_self_occupied=False,
            annual_rent_received=600000,
            municipal_taxes_paid=20000,
            interest_paid=100000,
        )
    ]
    income, warnings = compute_house_property_income(properties, "old", RULES)
    # net annual value = 580000, standard deduction 30% = 174000, minus interest 100000
    assert income == pytest.approx(306000)


def test_let_out_loss_below_cap_allowed_in_old_regime_but_blocked_in_new():
    properties = [
        HouseProperty(
            is_self_occupied=False,
            annual_rent_received=100000,
            municipal_taxes_paid=0,
            interest_paid=150000,
        )
    ]
    old_income, _ = compute_house_property_income(properties, "old", RULES)
    new_income, _ = compute_house_property_income(properties, "new", RULES)
    # net annual value 100000, std deduction 30000, interest 150000 -> -80000,
    # under the 200000 old-regime cap so fully allowed; new regime blocks any set-off
    assert old_income == pytest.approx(-80000)
    assert new_income == pytest.approx(0)


def test_old_regime_loss_set_off_capped_at_200000_with_carry_forward_warning():
    properties = [
        HouseProperty(
            is_self_occupied=False,
            annual_rent_received=0,
            municipal_taxes_paid=0,
            interest_paid=300000,
        )
    ]
    income, warnings = compute_house_property_income(properties, "old", RULES)
    # net = -300000; set-off capped at -200000, 100000 carried forward
    assert income == pytest.approx(-200000)
    assert len(warnings) == 1
    assert "100000" in warnings[0] or "100,000" in warnings[0]


def test_new_regime_blocks_cross_head_set_off_entirely():
    properties = [
        HouseProperty(
            is_self_occupied=False,
            annual_rent_received=0,
            municipal_taxes_paid=0,
            interest_paid=300000,
        )
    ]
    income, warnings = compute_house_property_income(properties, "new", RULES)
    assert income == pytest.approx(0)
    assert len(warnings) == 1


def test_carried_forward_loss_from_prior_year_offsets_this_years_income():
    properties = [
        HouseProperty(
            is_self_occupied=False,
            annual_rent_received=600000,
            municipal_taxes_paid=20000,
            interest_paid=100000,
            carried_forward_loss=50000,
        )
    ]
    income, warnings = compute_house_property_income(properties, "old", RULES)
    # this year's net 306000, minus prior year's carried-forward loss 50000
    assert income == pytest.approx(256000)


def test_third_self_occupied_property_excluded_with_warning():
    properties = [
        HouseProperty(is_self_occupied=True, interest_paid=50000),
        HouseProperty(is_self_occupied=True, interest_paid=50000),
        HouseProperty(is_self_occupied=True, interest_paid=50000),
    ]
    income, warnings = compute_house_property_income(properties, "old", RULES)
    # only first 2 counted: -50000 + -50000 = -100000
    assert income == pytest.approx(-100000)
    assert len(warnings) == 1
    assert "excluded" in warnings[0]


def test_positive_total_income_added_in_full_in_both_regimes():
    properties = [
        HouseProperty(
            is_self_occupied=False,
            annual_rent_received=600000,
            municipal_taxes_paid=20000,
            interest_paid=0,
        )
    ]
    old_income, _ = compute_house_property_income(properties, "old", RULES)
    new_income, _ = compute_house_property_income(properties, "new", RULES)
    assert old_income == pytest.approx(406000)
    assert new_income == pytest.approx(406000)
