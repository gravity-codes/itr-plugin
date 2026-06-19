import pytest
from conftest import RULES

from tax_engine.compute_tax import compute_regime
from tax_engine.models import TaxInput


def test_nps_self_contribution_capped_at_50000_old_regime():
    tax_input = TaxInput(salary_gross=1500000, other_income=0, deductions_nps_self=80000)
    result = compute_regime(tax_input, "old", RULES)
    assert result.nps_deduction == pytest.approx(50000)


def test_nps_self_contribution_not_allowed_in_new_regime():
    tax_input = TaxInput(salary_gross=1500000, other_income=0, deductions_nps_self=50000)
    result = compute_regime(tax_input, "new", RULES)
    assert result.nps_deduction == pytest.approx(0)


def test_nps_self_contribution_reduces_old_regime_taxable_income():
    base = TaxInput(salary_gross=1500000, other_income=0)
    with_nps = TaxInput(salary_gross=1500000, other_income=0, deductions_nps_self=50000)
    base_result = compute_regime(base, "old", RULES)
    nps_result = compute_regime(with_nps, "old", RULES)
    assert base_result.taxable_income_at_slab - nps_result.taxable_income_at_slab == pytest.approx(
        50000
    )


def test_nps_employer_contribution_capped_at_14_percent_for_government_employer():
    tax_input = TaxInput(
        salary_gross=1000000,
        other_income=0,
        nps_employer_contribution=200000,
        is_government_employer=True,
    )
    result = compute_regime(tax_input, "old", RULES)
    assert result.nps_deduction == pytest.approx(140000)


def test_nps_employer_contribution_capped_at_10_percent_private_old_regime():
    tax_input = TaxInput(
        salary_gross=1000000,
        other_income=0,
        nps_employer_contribution=200000,
        is_government_employer=False,
    )
    result = compute_regime(tax_input, "old", RULES)
    assert result.nps_deduction == pytest.approx(100000)


def test_nps_employer_contribution_capped_at_14_percent_private_new_regime():
    tax_input = TaxInput(
        salary_gross=1000000,
        other_income=0,
        nps_employer_contribution=200000,
        is_government_employer=False,
    )
    result = compute_regime(tax_input, "new", RULES)
    assert result.nps_deduction == pytest.approx(140000)


def test_nps_employer_contribution_below_cap_allowed_in_full():
    tax_input = TaxInput(
        salary_gross=1000000,
        other_income=0,
        nps_employer_contribution=50000,
        is_government_employer=False,
    )
    result = compute_regime(tax_input, "old", RULES)
    assert result.nps_deduction == pytest.approx(50000)
