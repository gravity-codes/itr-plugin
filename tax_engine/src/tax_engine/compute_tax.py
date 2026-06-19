from tax_engine.capital_gains import compute_capital_gains_tax
from tax_engine.house_property import compute_house_property_income
from tax_engine.models import ComparisonResult, RegimeResult, TaxInput
from tax_engine.slabs import compute_slab_tax
from tax_engine.surcharge import compute_surcharge


def compute_regime(
    tax_input: TaxInput,
    regime: str,
    rules: dict,
    cg_result: tuple[float, float, float, float, list[str]] | None = None,
) -> RegimeResult:
    regime_rules = rules[f"{regime}_regime"]
    if cg_result is None:
        cg_result = compute_capital_gains_tax(tax_input.capital_gains, rules["capital_gains"])
    cg_tax, cg_income, slab_taxable_gains, vda_tax, warnings = cg_result
    capped_cg_tax = cg_tax - vda_tax

    house_property_income, hp_warnings = compute_house_property_income(
        tax_input.house_properties, regime, rules
    )
    warnings = warnings + hp_warnings

    standard_deduction = min(regime_rules["standard_deduction"], tax_input.salary_gross)
    taxable_income = max(
        0.0,
        tax_input.salary_gross
        - standard_deduction
        + tax_input.other_income
        + slab_taxable_gains
        + house_property_income,
    )

    nps_employer_cap_rate = (
        rules["nps"]["employer_contribution_cap_govt"]
        if tax_input.is_government_employer
        else rules["nps"][
            f"employer_contribution_cap_{'private_old_regime' if regime == 'old' else 'new_regime'}"
        ]
    )
    nps_employer_deduction = min(
        tax_input.nps_employer_contribution, nps_employer_cap_rate * tax_input.salary_gross
    )
    nps_deduction = nps_employer_deduction
    taxable_income = max(0.0, taxable_income - nps_employer_deduction)

    if regime == "old":
        deduction_80c = min(tax_input.deductions_80c, regime_rules["deduction_80c_limit"])
        d80d_limit = (
            regime_rules["deduction_80d_senior_limit"]
            if tax_input.is_senior_citizen
            else regime_rules["deduction_80d_self_limit"]
        )
        deduction_80d = min(tax_input.deductions_80d, d80d_limit)
        nps_self_deduction = min(
            tax_input.deductions_nps_self, rules["nps"]["self_contribution_limit"]
        )
        nps_deduction += nps_self_deduction
        taxable_income = max(
            0.0, taxable_income - deduction_80c - deduction_80d - nps_self_deduction
        )

    if regime == "old" and tax_input.is_senior_citizen:
        slabs = regime_rules["slabs_senior_citizen"]
    else:
        slabs = regime_rules["slabs"]
    slab_tax = compute_slab_tax(taxable_income, slabs)

    total_income_for_rebate_check = taxable_income + cg_income
    rebate = _compute_rebate(slab_tax, total_income_for_rebate_check, regime_rules)

    slab_tax_after_rebate = max(0.0, slab_tax - rebate)
    surcharge, surcharge_warnings = compute_surcharge(
        slab_tax_after_rebate,
        taxable_income,
        vda_tax,
        capped_cg_tax,
        total_income_for_rebate_check,
        slabs,
        rules["surcharge"],
        regime,
    )
    tax_before_cess = slab_tax_after_rebate + cg_tax + surcharge
    cess = tax_before_cess * rules["cess_rate"]
    total_tax = tax_before_cess + cess

    return RegimeResult(
        regime=regime,
        taxable_income_at_slab=taxable_income,
        slab_tax=slab_tax,
        capital_gains_tax=cg_tax,
        rebate=rebate,
        surcharge=surcharge,
        cess=cess,
        total_tax=total_tax,
        tds_paid=tax_input.tds_paid,
        balance_payable=total_tax - tax_input.tds_paid,
        house_property_income=house_property_income,
        nps_deduction=nps_deduction,
        warnings=warnings + surcharge_warnings,
    )


def _compute_rebate(slab_tax: float, total_income: float, regime_rules: dict) -> float:
    threshold = regime_rules["rebate_threshold"]
    max_rebate = regime_rules["rebate_max"]

    if total_income <= threshold:
        return min(slab_tax, max_rebate)

    if not regime_rules["rebate_has_marginal_relief"]:
        # e.g. old regime (s.156(1)): hard cliff, no rebate at all above the threshold.
        return 0.0

    excess_income = total_income - threshold
    if slab_tax > excess_income:
        return slab_tax - excess_income
    return 0.0


def compare_regimes(tax_input: TaxInput, rules: dict) -> ComparisonResult:
    cg_result = compute_capital_gains_tax(tax_input.capital_gains, rules["capital_gains"])
    old_result = compute_regime(tax_input, "old", rules, cg_result)
    new_result = compute_regime(tax_input, "new", rules, cg_result)
    recommended = "old" if old_result.total_tax < new_result.total_tax else "new"
    return ComparisonResult(old=old_result, new=new_result, recommended=recommended)
