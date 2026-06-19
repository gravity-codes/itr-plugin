from tax_engine.slabs import compute_slab_tax


def _bracket_index(total_income: float, brackets: list[dict]) -> int:
    for i, bracket in enumerate(brackets):
        upto = bracket["upto"] if bracket["upto"] is not None else float("inf")
        if total_income <= upto:
            return i
    return len(brackets) - 1


def compute_surcharge(
    slab_tax_after_rebate: float,
    taxable_income_at_slab: float,
    vda_tax: float,
    capped_cg_tax: float,
    total_income: float,
    slabs: list[dict],
    surcharge_rules: dict,
    regime: str,
) -> tuple[float, list[str]]:
    """Surcharge on income-tax (s.7974: rate set by the annual Finance Act,
    not the Act text itself -- see rules['surcharge']['note']).

    `capped_cg_tax` is tax on capital gains taxed under the equity STT
    STCG/LTCG and general/land-building LTCG rates (ss.196/198/197), which
    carry a surcharge cap of `surcharge_rules['special_rate_cap']` even when
    the ordinary-income surcharge rate is higher. `vda_tax` (crypto, s.194
    Table Sl.No.4) is not covered by that cap and is surcharged at the
    ordinary bracket rate.

    Applies marginal relief at the bracket boundary by reducing the
    slab-taxed portion of income first. If capital-gains tax alone exceeds
    the slab-taxed tax near a threshold, full relief can't be computed here
    (a v1 simplification) and a warning is returned instead of guessing.
    """
    brackets = surcharge_rules[f"{regime}_regime_brackets"]
    idx = _bracket_index(total_income, brackets)
    if idx == 0:
        return 0.0, []

    current_rate = brackets[idx]["rate"]
    previous = brackets[idx - 1]
    threshold = previous["upto"]
    previous_rate = previous["rate"]
    special_cap = surcharge_rules["special_rate_cap"]

    capped_rate = min(current_rate, special_cap)
    surcharge = (
        slab_tax_after_rebate * current_rate + vda_tax * current_rate + capped_cg_tax * capped_rate
    )

    warnings: list[str] = []
    excess = total_income - threshold

    if taxable_income_at_slab >= excess:
        reduced_slab_income = taxable_income_at_slab - excess
        slab_tax_at_threshold = compute_slab_tax(reduced_slab_income, slabs)
        previous_capped_rate = min(previous_rate, special_cap)
        surcharge_at_threshold = (
            slab_tax_at_threshold * previous_rate
            + vda_tax * previous_rate
            + capped_cg_tax * previous_capped_rate
        )

        tax_no_surcharge_actual = slab_tax_after_rebate + vda_tax + capped_cg_tax
        tax_no_surcharge_at_threshold = slab_tax_at_threshold + vda_tax + capped_cg_tax

        relief_capped_total = tax_no_surcharge_at_threshold + surcharge_at_threshold + excess
        actual_total = tax_no_surcharge_actual + surcharge

        if actual_total > relief_capped_total:
            surcharge = relief_capped_total - tax_no_surcharge_actual
    else:
        warnings.append(
            f"Marginal relief near the Rs.{threshold:,.0f} surcharge threshold could "
            "not be fully verified because capital-gains tax exceeds the slab-taxed "
            "portion of your income -- this v1 only reduces slab-taxed income when "
            "checking for relief. Consult a CA to confirm whether marginal relief "
            "reduces your surcharge further."
        )

    return surcharge, warnings
