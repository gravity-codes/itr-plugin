from tax_engine.models import AssetClass, CapitalGainEntry


def compute_capital_gains_tax(
    entries: list[CapitalGainEntry], rules: dict
) -> tuple[float, float, float, list[str]]:
    """Returns (special_rate_tax, special_rate_income, slab_taxable_gains, warnings).

    `special_rate_tax`/`special_rate_income` cover gains that have a dedicated
    rate under the Act (equity STT STCG/LTCG, general/land-building LTCG, VDA).
    `slab_taxable_gains` covers short-term gains on non-equity-STT assets
    (debt funds, unlisted shares, land/building held under 24 months), which
    the Act gives no special rate for -- they're ordinary income taxed at
    slab rates, so the caller must add this into taxable income rather than
    treating it as part of the capital-gains tax liability.
    """
    warnings: list[str] = []
    special_rate_tax = 0.0
    special_rate_income = 0.0
    slab_taxable_gains = 0.0

    for asset_class in AssetClass:
        for is_long_term in (True, False):
            bucket = [
                e
                for e in entries
                if e.asset_class == asset_class and e.is_long_term == is_long_term
            ]
            if not bucket:
                continue

            if asset_class == AssetClass.VDA:
                for entry in bucket:
                    if entry.gain < 0:
                        warnings.append(
                            "VDA loss of "
                            f"{abs(entry.gain):.2f} cannot be set off against any income "
                            "and cannot be carried forward (Income-tax Act 2025, s.194 Table Sl.No.4)."
                        )
                        continue
                    special_rate_income += entry.gain
                    special_rate_tax += entry.gain * rules["vda_rate"]
                continue

            net_gain = sum(e.gain for e in bucket)
            if net_gain <= 0:
                if net_gain < 0:
                    warnings.append(
                        f"Net loss of {abs(net_gain):.2f} in {asset_class.value} "
                        f"({'long' if is_long_term else 'short'}-term) bucket is not set off "
                        "against other gains in this v1 computation."
                    )
                continue

            if asset_class == AssetClass.EQUITY_STT and is_long_term:
                taxable = max(0.0, net_gain - rules["equity_stt_ltcg_exemption"])
                special_rate_income += net_gain
                special_rate_tax += taxable * rules["equity_stt_ltcg_rate"]
            elif asset_class == AssetClass.EQUITY_STT and not is_long_term:
                special_rate_income += net_gain
                special_rate_tax += net_gain * rules["equity_stt_stcg_rate"]
            elif asset_class == AssetClass.LAND_BUILDING and is_long_term:
                special_rate_income += net_gain
                special_rate_tax += _land_building_tax(bucket, rules)
            elif is_long_term:
                # GENERAL long-term (debt funds, unlisted shares held 24+ months): s.197.
                special_rate_income += net_gain
                special_rate_tax += net_gain * rules["general_ltcg_rate"]
            else:
                # GENERAL or LAND_BUILDING short-term: no special rate in the Act --
                # ordinary income taxed at slab rates.
                slab_taxable_gains += net_gain

    return special_rate_tax, special_rate_income, slab_taxable_gains, warnings


def _land_building_tax(bucket: list[CapitalGainEntry], rules: dict) -> float:
    tax = 0.0
    for entry in bucket:
        non_indexed_tax = entry.gain * rules["general_ltcg_rate"]
        if entry.acquired_before_2024_07_23 and entry.indexed_gain is not None:
            indexed_tax = entry.indexed_gain * rules["land_building_grandfather_indexed_rate"]
            tax += min(non_indexed_tax, indexed_tax)
        else:
            tax += non_indexed_tax
    return tax
