from tax_engine.models import HouseProperty


def compute_house_property_income(
    properties: list[HouseProperty], regime: str, rules: dict
) -> tuple[float, list[str]]:
    """Returns (taxable contribution, warnings).

    Self-occupied properties beyond the first 2 (s.21(7)(a)) are excluded
    with a warning rather than guessing a notional rent. Net loss across all
    properties is subject to the old-regime cross-head set-off cap (s.109(1)(b))
    or fully blocked in the new regime (s.202(2)(b)(ii)); any unabsorbed amount
    is reported as a carry-forward warning (s.110(1)).
    """
    hp_rules = rules["house_property"]
    warnings: list[str] = []

    self_occupied = [p for p in properties if p.is_self_occupied]
    let_out = [p for p in properties if not p.is_self_occupied]

    max_self_occupied = hp_rules["max_self_occupied_properties"]
    if len(self_occupied) > max_self_occupied:
        excess = len(self_occupied) - max_self_occupied
        warnings.append(
            f"{excess} self-occupied propert{'y' if excess == 1 else 'ies'} beyond the "
            f"{max_self_occupied} allowed (s.21(7)(a)) excluded from this computation -- "
            "treat as deemed-let-out manually or consult a CA."
        )
        self_occupied = self_occupied[:max_self_occupied]

    total = 0.0
    for prop in self_occupied:
        total += _self_occupied_net(prop, regime, hp_rules) - prop.carried_forward_loss
    for prop in let_out:
        total += _let_out_net(prop, hp_rules) - prop.carried_forward_loss

    if total >= 0:
        return total, warnings

    loss = -total
    if regime == "old":
        cap = hp_rules["loss_set_off_cap_old_regime"]
        allowed = min(loss, cap)
        carry_forward = loss - allowed
        if carry_forward > 0:
            warnings.append(
                f"House-property loss of {carry_forward:.2f} beyond the Rs. {cap} "
                "old-regime set-off cap (s.109(1)(b)) is carried forward to next "
                "year (s.110(1))."
            )
        return -allowed, warnings

    warnings.append(
        f"House-property loss of {loss:.2f} cannot be set off against other income "
        "in the new regime (s.202(2)(b)(ii)) and is fully carried forward to next year."
    )
    return 0.0, warnings


def _self_occupied_net(prop: HouseProperty, regime: str, hp_rules: dict) -> float:
    if regime == "new":
        return 0.0
    cap = (
        hp_rules["self_occupied_interest_cap_post_1999"]
        if prop.loan_post_1999_for_acquisition
        else hp_rules["self_occupied_interest_cap_other"]
    )
    return -min(prop.interest_paid, cap)


def _let_out_net(prop: HouseProperty, hp_rules: dict) -> float:
    net_annual_value = max(0.0, prop.annual_rent_received - prop.municipal_taxes_paid)
    standard_deduction = hp_rules["let_out_standard_deduction_rate"] * net_annual_value
    return net_annual_value - standard_deduction - prop.interest_paid
