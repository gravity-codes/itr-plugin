import pytest
from conftest import RULES

from tax_engine.compute_tax import compute_regime
from tax_engine.models import AssetClass, CapitalGainEntry, TaxInput


def test_no_surcharge_below_50l():
    tax_input = TaxInput(salary_gross=4000000, other_income=0)
    result = compute_regime(tax_input, "new", RULES)
    assert result.surcharge == pytest.approx(0)


def test_surcharge_10_percent_between_50l_and_1cr():
    # well clear of the 50L marginal-relief band so relief doesn't apply
    tax_input = TaxInput(salary_gross=7000000, other_income=0)
    result = compute_regime(tax_input, "new", RULES)
    assert result.surcharge == pytest.approx(result.slab_tax * 0.10)


def test_surcharge_25_percent_above_2cr_new_regime_has_no_37_percent_slab():
    tax_input = TaxInput(salary_gross=60000000, other_income=0)
    result = compute_regime(tax_input, "new", RULES)
    assert result.surcharge == pytest.approx(result.slab_tax * 0.25)


def test_surcharge_37_percent_above_5cr_old_regime():
    tax_input = TaxInput(salary_gross=60000000, other_income=0)
    result = compute_regime(tax_input, "old", RULES)
    assert result.surcharge == pytest.approx(result.slab_tax * 0.37)


def test_equity_ltcg_surcharge_capped_at_15_percent_even_in_37_percent_old_regime_band():
    tax_input = TaxInput(
        salary_gross=60000000,
        other_income=0,
        capital_gains=[
            CapitalGainEntry(asset_class=AssetClass.EQUITY_STT, is_long_term=True, gain=1000000)
        ],
    )
    result = compute_regime(tax_input, "old", RULES)
    ltcg_tax = (1000000 - 125000) * 0.125
    expected_surcharge = result.slab_tax * 0.37 + ltcg_tax * 0.15
    assert result.surcharge == pytest.approx(expected_surcharge)


def test_vda_surcharge_not_capped_at_15_percent():
    tax_input = TaxInput(
        salary_gross=60000000,
        other_income=0,
        capital_gains=[
            CapitalGainEntry(asset_class=AssetClass.VDA, is_long_term=False, gain=1000000)
        ],
    )
    result = compute_regime(tax_input, "old", RULES)
    vda_tax = 1000000 * 0.30
    expected_surcharge = result.slab_tax * 0.37 + vda_tax * 0.37
    assert result.surcharge == pytest.approx(expected_surcharge)


def test_marginal_relief_just_above_50l_caps_incremental_tax_to_incremental_income():
    at_threshold = compute_regime(TaxInput(salary_gross=5075000, other_income=0), "new", RULES)
    just_above = compute_regime(TaxInput(salary_gross=5085000, other_income=0), "new", RULES)
    # the 10000 extra salary should add at most 10000 to slab_tax+surcharge
    # (before cess), since marginal relief caps it there
    increase = (just_above.slab_tax + just_above.surcharge) - (
        at_threshold.slab_tax + at_threshold.surcharge
    )
    assert increase <= 10000 + 1e-6


def test_marginal_relief_warns_when_capital_gains_exceed_slab_tax_near_threshold():
    # near-zero salary, large equity LTCG pushing just past the 50L threshold --
    # slab tax can't absorb the relief reduction, so v1 surfaces a warning
    # instead of guessing how to reduce capital-gains tax for relief.
    tax_input = TaxInput(
        salary_gross=100000,
        other_income=0,
        capital_gains=[
            CapitalGainEntry(asset_class=AssetClass.EQUITY_STT, is_long_term=True, gain=5500000)
        ],
    )
    result = compute_regime(tax_input, "new", RULES)
    assert any("marginal relief" in w.lower() for w in result.warnings)
