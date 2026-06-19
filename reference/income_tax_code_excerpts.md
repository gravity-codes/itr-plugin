# Income-tax Act 2025 — Excerpts Relevant to Salary + Capital Gains Filing

Source file: `Income-tax-Act-2025_2026_2026-06-10_03-46-08_691051_en.txt`
(repo root). This Act comes into force 1 April 2026 (s.1(3)) and governs
Tax Year 2026-27.

## Standard deduction (s.19(1) Table Sl.No.2)
- New regime (s.202(1) chargeable): Rs. 75,000 or salary, whichever is less.
- Old regime: Rs. 50,000 or salary, whichever is less.

## Rebates (Chapter IX)
- s.156(1) (old regime): resident individuals with total income <=
  Rs. 5,00,000 get a rebate of 100% of tax or Rs. 12,500, whichever is less.
  **There is no marginal-relief clause for the old regime** — above
  Rs. 5,00,000 the rebate is exactly zero, a hard cliff, not a phase-out.
- s.156(2) (new regime only, s.202(1)): resident individuals with total
  income <= Rs. 12,00,000 get a rebate of 100% of tax or Rs. 60,000,
  whichever is less; above that, marginal relief caps the net tax at the
  amount by which income exceeds Rs. 12,00,000. This marginal-relief clause
  exists only in s.156(2), not s.156(1) — `rebate_has_marginal_relief` in
  the rules JSON encodes this difference.

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
- s.2(101): long-term holding-period thresholds differ by asset type —
  listed securities/equity-oriented fund units/UTI units/zero-coupon bonds:
  more than 12 months; everything else (unlisted shares, land/building,
  most debt instruments): more than 24 months.
- s.76: debt mutual funds ("Specified Mutual Fund," >65% debt/money-market
  instruments) acquired on or after 1 April 2023, and unlisted
  bonds/debentures transferred on or after 23 July 2024, are **always**
  treated as short-term regardless of actual holding period.
- s.196(1): equity/equity-fund/business-trust-unit STCG with STT paid: 20%.
- s.198(2): equity/equity-fund/business-trust-unit LTCG with STT paid: 12.5%
  on gains exceeding Rs. 1,25,000 in the year.
- s.197(1): other long-term capital gains (debt funds, unlisted shares,
  etc.): 12.5%, no indexation.
- s.197(3): land/building acquired before 23 July 2024 — taxpayer gets the
  lower of (a) 12.5% on the gain without indexation, or (b) 20% on the gain
  computed with indexation.
- Short-term gains on non-equity-STT assets (debt funds, unlisted shares,
  land/building held under 24 months) have **no special rate** in the Act —
  there is no equivalent to s.196 for them. They are ordinary income, added
  to the slab-taxed total and charged at whatever bracket the taxpayer falls
  into (0%-30%), not a flat rate.
- s.194 Table Sl.No.4: virtual digital assets (crypto): flat 30%, only cost
  of acquisition is deductible, losses cannot be set off against any other
  income and cannot be carried forward.
- s.72(7)/(8): equity/equity-fund/business-trust-unit LTCG assets acquired
  before 1 Feb 2018 get a grandfathered *cost basis* — higher of actual
  cost, or the lower of (fair market value as of 31 Jan 2018, sale value).
  This changes the `gain` figure that must be extracted from the PnL
  statement *before* it reaches `tax_engine` (which never recomputes cost
  basis); it is a distinct mechanism from the land/building rate-choice
  grandfathering in s.197(3) above.

## House property income (ss.20-25)
- s.20, s.21: house property income head = annual value minus deductions.
- s.21(6), s.21(7)(a): self-occupied annual value is nil, for up to 2
  properties; a 3rd+ self-occupied property is excluded from `tax_engine`
  with a warning rather than guessing a notional rent for it.
- s.22(1)(a): let-out standard deduction is 30% of (rent minus municipal
  taxes).
- s.22(1)(b)/(c): let-out interest deduction is uncapped.
- s.22(2)(a)/(b): self-occupied interest deduction is capped at Rs. 2,00,000
  (loan taken after 1 April 1999 for acquisition/construction completed
  within 5 years) or Rs. 30,000 otherwise.
- s.109(1)(b): old regime caps cross-head set-off of a house-property loss
  at Rs. 2,00,000 per year; any excess is carried forward (s.110(1)) to
  offset future house-property income only. `tax_engine` is stateless
  year-to-year, so the user supplies last year's carried-forward figure as
  an input (`HouseProperty.carried_forward_loss`) and this year's unabsorbed
  amount is reported back as a warning to carry forward next year.
- s.202(2)(a)(v): new regime disallows the self-occupied interest deduction
  entirely.
- s.202(2)(b)(ii): new regime blocks house-property loss from cross-head
  set-off entirely — any loss is fully carried forward, none of it usable
  in the year it arises.
- Not modeled in v1: the s.21(1) "higher of expected-to-let value or actual
  rent" test for let-out annual value (the user supplies actual rent
  received directly), and vacancy/unrealised-rent adjustments (ss.21(2),
  23).

## NPS deductions (s.124)
- s.124(3)/(4): the individual's own additional NPS contribution (the
  "80CCD(1B)" equivalent) is deductible up to Rs. 50,000, old regime only.
- s.124(1)/(2): employer NPS contribution is deductible in both regimes,
  capped at 14% of salary for a government employer, 10% for a private
  employer in the old regime, and 14% for a private employer in the new
  regime (the new regime's higher private-employer cap is itself part of
  s.124(2)).
- s.202(2)(a)(xii): the new regime's general disallowance of Chapter VIII
  deductions carves out an exception preserving the employer NPS deduction
  above.

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

## Surcharge (relevant above Rs. 50 lakh total income)
- Not specified in the Act text — s.7974 only says tax "shall be increased
  by a surcharge, if any, levied by any Central Act," deferring the rate to
  the annual Finance Act, the same pattern as old-regime slabs/cess above.
  `tax_engine.surcharge` implements the established Finance Act convention
  (FY2023-24 onward): 10%/15%/25% bands at Rs. 50L/1Cr/2Cr total income, a
  further 37% band above Rs. 5Cr in the old regime only (the new regime caps
  surcharge at 25%, with no 37% band), and a 15% cap on the surcharge rate
  applied to equity STT STCG/LTCG and general/land-building LTCG tax (ss.
  196/198/197) even when the slab-income rate is higher. VDA/crypto tax (s.
  194 Table Sl.No.4) is *not* covered by that 15% cap. Reconfirm all rates
  against the actual Finance Act for TY2026-27 before relying on this.
- Marginal relief is applied at each bracket boundary by reducing the
  slab-taxed portion of income first. If capital-gains tax alone exceeds the
  slab-taxed tax near a threshold (e.g. near-zero salary, large LTCG just
  over Rs. 50L), `tax_engine` can't fully verify relief and returns a
  warning instead of guessing — flag this to the user and recommend a CA
  check in that band.

## Known v1 simplifications
- No cross-bucket capital-loss set-off (e.g. a short-term equity loss is not
  applied against a long-term equity gain). Each asset-class/term bucket is
  netted independently; an unset-off loss is reported as a warning.
- The s.87A-equivalent rebate (ss.156(1)/(2)) is applied only against
  slab-taxed income tax, never against capital-gains tax, even though the
  threshold check uses total income (slab income + capital gains, with
  equity LTCG counted net of the Rs. 1,25,000 exemption since that exemption
  reduces income chargeable to tax under the Act) per the literal text. This
  is a conservative simplification given genuine ambiguity in how the rebate
  interacts with special-rate capital gains.
- Government-employee pension-scheme contributions deductible under
  s.125(2) and s.146 (distinct from the s.124 NPS contributions
  `tax_engine` does model) have no `TaxInput` field — they're omitted from
  both regimes' computations equally, rather than skewing the old-vs-new
  comparison; flag it to affected users rather than silently omitting it.
