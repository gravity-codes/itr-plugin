# Income-tax Act 2025 — Excerpts Relevant to Salary + Capital Gains Filing

Source file: `Income-tax-Act-2025_2026_2026-06-10_03-46-08_691051_en.txt`
(repo root). This Act comes into force 1 April 2026 (s.1(3)) and governs
Tax Year 2026-27.

## Standard deduction (s.19(1) Table Sl.No.2)
- New regime (s.202(1) chargeable): Rs. 75,000 or salary, whichever is less.
- Old regime: Rs. 50,000 or salary, whichever is less.

## Rebates (Chapter IX)
- s.156(1): resident individuals with total income <= Rs. 5,00,000 get a
  rebate of 100% of tax or Rs. 12,500, whichever is less.
- s.156(2): resident individuals taxed under the new regime (s.202(1)) with
  total income <= Rs. 12,00,000 get a rebate of 100% of tax or Rs. 60,000,
  whichever is less; above that, marginal relief caps the net tax at the
  amount by which income exceeds Rs. 12,00,000.

## New regime slabs (s.202(1))
0-4L: nil, 4-8L: 5%, 8-12L: 10%, 12-16L: 15%, 16-20L: 20%, 20-24L: 25%,
above 24L: 30%.

## Chapter VIII deductions (old regime only)
- s.123: life insurance/PF/etc. (80C-equivalent), capped at Rs. 1,50,000.
- s.126: health insurance premia (80D-equivalent) — Rs. 25,000 self/family,
  Rs. 25,000 parents, raised to Rs. 50,000 where the insured person is a
  senior citizen; medical expenditure (no insurance) capped separately at
  Rs. 50,000 each.

## Capital gains
- s.196(1): equity/equity-fund/business-trust-unit STCG with STT paid: 20%.
- s.198(2): equity/equity-fund/business-trust-unit LTCG with STT paid: 12.5%
  on gains exceeding Rs. 1,25,000 in the year.
- s.197(1): other long-term capital gains (debt funds, unlisted shares,
  etc.): 12.5%, no indexation.
- s.197(3): land/building acquired before 23 July 2024 — taxpayer gets the
  lower of (a) 12.5% on the gain without indexation, or (b) 20% on the gain
  computed with indexation.
- s.194 Table Sl.No.4: virtual digital assets (crypto): flat 30%, only cost
  of acquisition is deductible, losses cannot be set off against any other
  income and cannot be carried forward.

## Old-regime basic exemption and slab rates
Not specified in the Act text — it defers these to the annual Finance Act.
This plugin uses the established-convention figures (Rs. 2,50,000 basic
exemption; 5%/20%/30% slabs at Rs. 5L/Rs. 10L breakpoints) recorded in
`tax_engine/rules/tax_year_2026_27.json`. Resident senior citizens (60+) get
a raised Rs. 3,00,000 basic exemption under the old regime
(`slabs_senior_citizen` in the rules file) — selected automatically when
`TaxInput.is_senior_citizen=True`. Super-senior citizens (80+) get a further
raise in real practice but that age tier is out of scope for v1 — there's no
separate flag for it. Reconfirm all of these against the actual Finance Act
for the filing year before relying on this for a real filing.

## Known v1 simplifications
- No cross-bucket capital-loss set-off (e.g. a short-term equity loss is not
  applied against a long-term equity gain). Each asset-class/term bucket is
  netted independently; an unset-off loss is reported as a warning.
- The s.87A-equivalent rebate (ss.156(1)/(2)) is applied only against
  slab-taxed income tax, never against capital-gains tax, even though the
  threshold check uses total income (slab income + capital gains) per the
  literal text. This is a conservative simplification given genuine
  ambiguity in how the rebate interacts with special-rate capital gains.
- No surcharge computation (relevant only above Rs. 50 lakh total income).
  Flag to the user if their income exceeds that threshold.
