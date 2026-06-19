from dataclasses import dataclass, field
from enum import Enum


class AssetClass(str, Enum):
    EQUITY_STT = "equity_stt"
    GENERAL = "general"
    LAND_BUILDING = "land_building"
    VDA = "vda"


@dataclass(frozen=True)
class CapitalGainEntry:
    asset_class: AssetClass
    is_long_term: bool
    gain: float
    acquired_before_2024_07_23: bool = False
    indexed_gain: float | None = None


@dataclass(frozen=True)
class HouseProperty:
    is_self_occupied: bool
    annual_rent_received: float = 0.0
    municipal_taxes_paid: float = 0.0
    interest_paid: float = 0.0
    loan_post_1999_for_acquisition: bool = True
    carried_forward_loss: float = 0.0


@dataclass(frozen=True)
class TaxInput:
    salary_gross: float
    other_income: float
    capital_gains: list[CapitalGainEntry] = field(default_factory=list)
    deductions_80c: float = 0.0
    deductions_80d: float = 0.0
    is_senior_citizen: bool = False
    tds_paid: float = 0.0
    house_properties: list[HouseProperty] = field(default_factory=list)
    deductions_nps_self: float = 0.0
    nps_employer_contribution: float = 0.0
    is_government_employer: bool = False


@dataclass(frozen=True)
class RegimeResult:
    regime: str
    taxable_income_at_slab: float
    slab_tax: float
    capital_gains_tax: float
    rebate: float
    surcharge: float
    cess: float
    total_tax: float
    tds_paid: float
    balance_payable: float
    house_property_income: float = 0.0
    nps_deduction: float = 0.0
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ComparisonResult:
    old: RegimeResult
    new: RegimeResult
    recommended: str
