def compute_slab_tax(taxable_income: float, slabs: list[dict]) -> float:
    tax = 0.0
    lower_bound = 0.0
    for slab in slabs:
        upper_bound = slab["upto"] if slab["upto"] is not None else float("inf")
        if taxable_income <= lower_bound:
            break
        slab_amount = min(taxable_income, upper_bound) - lower_bound
        tax += slab_amount * slab["rate"]
        lower_bound = upper_bound
    return tax
