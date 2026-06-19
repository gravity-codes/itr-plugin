import json
from pathlib import Path

import pytest

from tax_engine.compute_tax import compare_regimes, compute_regime, compute_slab_tax
from tax_engine.models import AssetClass, CapitalGainEntry, TaxInput

RULES = json.loads((Path(__file__).parent.parent / "rules" / "tax_year_2026_27.json").read_text())
NEW_SLABS = RULES["new_regime"]["slabs"]
OLD_SLABS = RULES["old_regime"]["slabs"]


def test_new_regime_slab_tax_at_boundary():
    # 800000 -> 0 on first 400000, 5% on next 400000 = 20000
    assert compute_slab_tax(800000, NEW_SLABS) == pytest.approx(20000)


def test_new_regime_slab_tax_top_bracket():
    # 2500000: 0 + 20000 + 40000 + 60000 + 80000 + 100000 + 30%*100000 = 330000
    assert compute_slab_tax(2500000, NEW_SLABS) == pytest.approx(330000)


def test_old_regime_slab_tax_at_boundary():
    # 1000000: 0 on first 250000, 5% on next 250000 = 12500, 20% on next 500000 = 100000
    assert compute_slab_tax(1000000, OLD_SLABS) == pytest.approx(112500)


def test_new_regime_rebate_full_below_threshold():
    tax_input = TaxInput(salary_gross=1175000, other_income=0)
    result = compute_regime(tax_input, "new", RULES)
    # taxable salary = 1175000 - 75000 std deduction = 1100000 <= 12L -> full rebate up to 60000
    assert result.rebate > 0
    assert result.total_tax == pytest.approx(0)


def test_new_regime_marginal_relief_just_above_threshold():
    tax_input = TaxInput(salary_gross=1280000, other_income=0)
    result = compute_regime(tax_input, "new", RULES)
    # taxable income = 1280000 - 75000 = 1205000, which is 5000 above 12L
    # slab tax on 1205000 = 20000 (5% on 4-8L) + 40000 (10% on 8-12L) + 750 (15% on 5000) = 60750
    # marginal relief caps net slab tax at the 5000 excess over 12L
    assert result.slab_tax == pytest.approx(60750)
    assert result.total_tax == pytest.approx(5000 * 1.04)  # cess on capped tax


def test_old_regime_rebate_below_threshold():
    tax_input = TaxInput(salary_gross=500000, other_income=0, deductions_80c=0)
    result = compute_regime(tax_input, "old", RULES)
    # taxable = 500000 - 50000 std deduction = 450000 <= 5L -> full rebate (tax is 10000, rebate cap 12500)
    assert result.total_tax == pytest.approx(0)


def test_old_regime_80c_and_80d_caps_applied():
    tax_input = TaxInput(
        salary_gross=1500000, other_income=0, deductions_80c=300000, deductions_80d=100000
    )
    result = compute_regime(tax_input, "old", RULES)
    # 80C capped at 150000, 80D capped at 25000 (not senior)
    # taxable = 1500000 - 50000 std ded - 150000 (80C) - 25000 (80D) = 1275000
    assert result.taxable_income_at_slab == pytest.approx(1275000)


def test_capital_gains_tax_added_and_not_rebated():
    tax_input = TaxInput(
        salary_gross=1175000,
        other_income=0,
        capital_gains=[
            CapitalGainEntry(asset_class=AssetClass.EQUITY_STT, is_long_term=False, gain=50000)
        ],
    )
    result = compute_regime(tax_input, "new", RULES)
    # slab tax fully rebated (as in first test); capital gains tax (50000*20%=10000) is not rebated
    assert result.capital_gains_tax == pytest.approx(10000)
    assert result.total_tax == pytest.approx(10000 * 1.04)


def test_compare_regimes_recommends_lower_tax():
    tax_input = TaxInput(
        salary_gross=1800000, other_income=0, deductions_80c=150000, deductions_80d=25000
    )
    comparison = compare_regimes(tax_input, RULES)
    assert comparison.recommended in ("old", "new")
    cheaper = (
        comparison.old if comparison.old.total_tax <= comparison.new.total_tax else comparison.new
    )
    assert comparison.recommended == cheaper.regime


def test_compare_regimes_no_deductions_favors_new():
    tax_input = TaxInput(salary_gross=1500000, other_income=0)
    comparison = compare_regimes(tax_input, RULES)
    # with zero deductions claimed, new regime's lower slabs should win
    assert comparison.recommended == "new"


def test_old_regime_senior_citizen_gets_raised_basic_exemption():
    tax_input = TaxInput(salary_gross=550000, other_income=0, is_senior_citizen=True)
    result = compute_regime(tax_input, "old", RULES)
    # taxable = 550000 - 50000 std deduction = 500000
    # senior slabs: 0 on first 300000, 5% on next 200000 = 10000 (vs 12500 on non-senior slabs)
    assert result.slab_tax == pytest.approx(10000)


def test_old_regime_non_senior_uses_standard_slabs():
    tax_input = TaxInput(salary_gross=550000, other_income=0, is_senior_citizen=False)
    result = compute_regime(tax_input, "old", RULES)
    # taxable = 500000; non-senior slabs: 0 on first 250000, 5% on next 250000 = 12500
    assert result.slab_tax == pytest.approx(12500)


def test_balance_payable_is_positive_when_tds_understates_liability():
    tax_input = TaxInput(salary_gross=1500000, other_income=0, tds_paid=50000)
    result = compute_regime(tax_input, "new", RULES)
    assert result.tds_paid == pytest.approx(50000)
    assert result.balance_payable == pytest.approx(result.total_tax - 50000)
    assert result.balance_payable > 0


def test_balance_payable_is_negative_refund_when_tds_overpays():
    tax_input = TaxInput(salary_gross=1175000, other_income=0, tds_paid=20000)
    result = compute_regime(tax_input, "new", RULES)
    # total_tax is 0 here (fully rebated, see test_new_regime_rebate_full_below_threshold)
    assert result.total_tax == pytest.approx(0)
    assert result.balance_payable == pytest.approx(-20000)


def test_old_regime_rebate_is_a_hard_cliff_with_no_marginal_relief():
    # s.156(1) (old regime) has no marginal-relief clause, unlike s.156(2) (new
    # regime). Just above the 5L threshold, the rebate must drop to zero
    # outright rather than phasing out -- a taxpayer here gets no rebate at all.
    tax_input = TaxInput(salary_gross=560000, other_income=0)
    result = compute_regime(tax_input, "old", RULES)
    assert result.taxable_income_at_slab == pytest.approx(510000)
    assert result.rebate == pytest.approx(0)
    assert result.slab_tax == pytest.approx(14500)
