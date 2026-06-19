import json
from pathlib import Path

import pytest

from tax_engine.capital_gains import compute_capital_gains_tax
from tax_engine.models import AssetClass, CapitalGainEntry

RULES = json.loads(
    (Path(__file__).parent.parent / "rules" / "tax_year_2026_27.json").read_text()
)["capital_gains"]


def test_equity_stcg_taxed_at_20_percent():
    entries = [CapitalGainEntry(asset_class=AssetClass.EQUITY_STT, is_long_term=False, gain=100000)]
    tax, income, warnings = compute_capital_gains_tax(entries, RULES)
    assert tax == pytest.approx(20000)
    assert income == pytest.approx(100000)
    assert warnings == []


def test_equity_ltcg_exemption_applied_before_tax():
    entries = [CapitalGainEntry(asset_class=AssetClass.EQUITY_STT, is_long_term=True, gain=200000)]
    tax, income, warnings = compute_capital_gains_tax(entries, RULES)
    # (200000 - 125000) * 12.5%
    assert tax == pytest.approx(9375)
    assert income == pytest.approx(200000)


def test_equity_ltcg_under_exemption_is_tax_free():
    entries = [CapitalGainEntry(asset_class=AssetClass.EQUITY_STT, is_long_term=True, gain=100000)]
    tax, income, warnings = compute_capital_gains_tax(entries, RULES)
    assert tax == pytest.approx(0)
    assert income == pytest.approx(100000)


def test_general_ltcg_taxed_at_12_5_percent_no_exemption():
    entries = [CapitalGainEntry(asset_class=AssetClass.GENERAL, is_long_term=True, gain=50000)]
    tax, income, warnings = compute_capital_gains_tax(entries, RULES)
    assert tax == pytest.approx(6250)


def test_land_building_uses_lower_of_indexed_and_non_indexed():
    entries = [
        CapitalGainEntry(
            asset_class=AssetClass.LAND_BUILDING,
            is_long_term=True,
            gain=1000000,
            acquired_before_2024_07_23=True,
            indexed_gain=700000,
        )
    ]
    tax, income, _ = compute_capital_gains_tax(entries, RULES)
    # non-indexed: 1000000 * 12.5% = 125000; indexed: 700000 * 20% = 140000 -> take lower
    assert tax == pytest.approx(125000)


def test_vda_flat_30_percent_and_losses_not_set_off():
    entries = [
        CapitalGainEntry(asset_class=AssetClass.VDA, is_long_term=False, gain=100000),
        CapitalGainEntry(asset_class=AssetClass.VDA, is_long_term=False, gain=-40000),
    ]
    tax, income, warnings = compute_capital_gains_tax(entries, RULES)
    # VDA gains and losses are never netted against each other
    assert tax == pytest.approx(30000)
    assert income == pytest.approx(100000)
    assert any("loss" in w.lower() for w in warnings)


def test_net_loss_in_a_bucket_yields_zero_tax_and_warning():
    entries = [CapitalGainEntry(asset_class=AssetClass.GENERAL, is_long_term=True, gain=-50000)]
    tax, income, warnings = compute_capital_gains_tax(entries, RULES)
    assert tax == pytest.approx(0)
    assert income == pytest.approx(0)
    assert len(warnings) == 1
