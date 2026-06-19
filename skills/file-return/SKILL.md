---
name: file-return
description: Walks an Indian taxpayer through computing income tax (salary + capital gains, old vs new regime) from Form 16, AIS, and PnL statements, and produces a portal-entry checklist. Use when the user wants help filing their ITR.
---

# File ITR Return

You help the user compute their income tax and prepare to file ITR-2
manually on the income tax e-filing portal. You never submit anything to the
portal yourself — every entry is done by the human.

All tax arithmetic MUST go through the `tax_engine` Python package
(`tax_engine/src/tax_engine/`). Never compute tax figures yourself by
reasoning — always call `compare_regimes` from `tax_engine.compute_tax`.

Read `reference/income_tax_code_excerpts.md` for the rules and their
statutory citations, and `reference/portal_navigation_guide.md` for where
each figure goes on the portal.

### How to actually invoke tax_engine

`tax_engine` is its own `uv`-managed package, separate from the repo root.
You don't have a persistent Python REPL, so from the repo root run a script
through that package's environment with:

```bash
uv run --project tax_engine python <script.py>
```

Write the script to a temp file under `./itr-filing/TY2026-27/` (e.g.
`compute.py`), have it read the confirmed `extracted-data.json`, build the
`TaxInput`/`CapitalGainEntry` objects, call `compare_regimes`, and print the
result as JSON (`dataclasses.asdict` works for this) so you can read the
output back from the Bash tool result and use it to write
`tax-computation.md`. Do not leave stray throwaway scripts lying around —
delete the temp script (or overwrite it each run) once you've captured its
output.

## Flow

1. **Collect documents.** Ask the user for file paths to their Form 16
   (PDF), AIS (PDF or Excel), and one or more broker PnL statements (Excel or
   CSV). Read each file directly. Also ask directly whether they are a
   resident senior citizen (age 60 or above as of the end of the tax year)
   — this sets `TaxInput.is_senior_citizen` and changes the old-regime basic
   exemption and 80D cap; don't try to infer it from Form 16, since it
   doesn't reliably state date of birth. If they're 80+ (super senior),
   tell them this plugin's v1 doesn't have a separate super-senior tier and
   their actual old-regime exemption may be higher than what gets computed
   here — flag it as a caveat in the final report rather than guessing.

2. **Extract.** Pull out:
   - From Form 16: gross salary (`salary_gross`), any other taxable income
     reported, TDS deducted (`TaxInput.tds_paid` — also check AIS's "Tax
     Deducted" section for TDS from non-salary sources, e.g. on bank
     interest, and add it in), and the Chapter VI-A deductions the employer
     already accounted for (Part B usually itemizes 80C-equivalent and
     80D-equivalent investments the employee declared). Use these as a
     starting point for `deductions_80c` / `deductions_80d`, but always ask
     the user to confirm — actual investments for the full tax year often
     differ from what was declared to the employer mid-year (e.g. ELSS/PPF
     contributed after the declaration, or health insurance bought later).
     These two deduction fields only matter for the old-regime comparison —
     ask even if the user expects the new regime to win, since that's
     exactly the comparison this skill exists to make.
   - From AIS: every income head reported. AIS is the primary source for
     `other_income` (interest, dividends, and any other non-salary,
     non-capital-gains income) — sum these into `TaxInput.other_income`.
     AIS's salary and securities-transaction entries are *not* fed into the
     computation directly (Form 16 and the PnL statements are the
     authoritative sources for those); instead, cross-check AIS's salary and
     securities figures against what you extracted from Form 16/PnL and
     surface any mismatch as a warning in step 4 rather than silently
     reconciling it.
   - From PnL statements: every capital gains transaction, classified into
     `tax_engine.models.AssetClass` (`EQUITY_STT` for listed equity/equity
     funds/business trust units with STT paid, `GENERAL` for debt
     funds/unlisted shares/other capital assets, `LAND_BUILDING` for real
     estate, `VDA` for crypto), with `gain`, and `is_long_term` determined
     by the holding-period threshold for that specific asset type (s.2(101)
     of the Act) — these thresholds differ and getting this wrong directly
     changes the tax rate applied:
     - `EQUITY_STT`: long-term means held **more than 12 months** (not 24 —
       listed securities and equity-oriented fund units get the shorter
       threshold under s.2(101)(b)).
     - `GENERAL` debt mutual funds ("Specified Mutual Fund": >65% debt/money
       market instruments) acquired on or after 1 April 2023, and unlisted
       bonds/debentures transferred on or after 23 July 2024: **always**
       `is_long_term=False` regardless of actual holding period (s.76) — ask
       the user/check the fund factsheet for the >65% debt threshold rather
       than assuming every "debt fund" name qualifies.
     - `GENERAL` for other assets (unlisted shares, etc.) and
       `LAND_BUILDING`: long-term means held **more than 24 months**.

     For `LAND_BUILDING` entries acquired before 2024-07-23, set both
     `acquired_before_2024_07_23=True` and the indexation-adjusted
     `indexed_gain` so `tax_engine` can pick the cheaper of the indexed vs.
     non-indexed rate (s.197(3)).

     For `EQUITY_STT` long-term entries acquired before 1 Feb 2018: the
     `gain` figure itself must already use cost of acquisition = higher of
     (actual cost, lower of [fair market value as of 31 Jan 2018, sale
     value]) per s.72(7)/(8) — this is a different mechanism from the
     land/building rate-grandfathering above (it changes the cost basis, not
     the tax rate) and `tax_engine` does not recompute it. Most Indian
     broker tax P&L reports (Zerodha, Groww, etc.) already apply this when
     they label a line "LTCG" — but ask the user to confirm for any
     pre-2018 holding rather than assuming the broker number is right.
   - House property: ask directly whether they own any house property (Form
     16/AIS won't reliably surface this). For each property, ask
     self-occupied vs let-out (up to 2 self-occupied properties are
     supported per s.21(7)(a); a 3rd+ is excluded with a warning rather than
     guessed), and for let-out properties the annual rent received and
     municipal taxes paid. For every property ask the interest paid on the
     housing loan, whether the loan was taken after 1999 for
     acquisition/construction completed within 5 years (this picks the
     ₹200,000 vs ₹30,000 self-occupied interest cap, s.22(2)(a)/(b)), and
     last year's carried-forward house-property loss if any (the engine is
     stateless year-to-year, so it can't look this up itself). Build
     `tax_engine.models.HouseProperty` entries into `TaxInput.house_properties`.
   - NPS: ask whether the user made an additional NPS self-contribution
     beyond what's routed through Section 80C (`TaxInput.deductions_nps_self`,
     capped at ₹50,000, old regime only — s.124(3)/(4)) and whether their
     employer makes an NPS contribution (`TaxInput.nps_employer_contribution`,
     allowed in both regimes — s.124(1)/(2)). If there's an employer
     contribution, also ask whether the employer is government or private
     (`TaxInput.is_government_employer`) since this changes the deduction
     cap.

   Write the extracted data to `./itr-filing/TY2026-27/extracted-data.json`
   in this directory's working tree (create the directory if needed).

3. **Confirm.** Print a table of every extracted figure and ask the user to
   confirm or correct it. Do not proceed to computation until confirmed.

4. **Compute.** Build a `tax_engine.models.TaxInput` from the confirmed data
   and call `tax_engine.compute_tax.compare_regimes(tax_input, rules)` where
   `rules` is `json.loads(Path("tax_engine/rules/tax_year_2026_27.json").read_text())`.
   Write `./itr-filing/TY2026-27/tax-computation.md` containing:
   - Total income, deductions applied, and tax under each regime.
   - The recommended regime and why (lower `total_tax`).
   - For the recommended regime: `tds_paid` against `total_tax`, and the
     resulting `balance_payable` stated plainly as either "additional tax of
     ₹X is due" (positive) or "refund of ₹X expected" (negative) — this is
     the number the user actually cares about, not just the gross liability.
   - The surcharge amount for the recommended regime (`RegimeResult.surcharge`),
     stated as a separate line from the base slab/capital-gains tax so the
     user can see it — it only applies above Rs. 50 lakh total income.
   - Every warning returned in `RegimeResult.warnings` (e.g. unset-off
     capital losses, or an unverifiable surcharge marginal-relief case near a
     Rs. 50L/1Cr/2Cr/5Cr threshold) presented clearly to the user.
   - Any AIS-vs-Form16/PnL mismatches you noticed during extraction, listed
     explicitly — never silently reconcile these; ask the user to resolve
     them.
   - House property income/loss for the recommended regime
     (`RegimeResult.house_property_income`) and the NPS deduction actually
     allowed (`RegimeResult.nps_deduction`) — show the user what was claimed
     vs what was allowed if either got capped.
   - If Form 16 shows an Agniveer Corpus Fund contribution, flag explicitly
     that `tax_engine` v1 doesn't model this (no `TaxInput` field exists for
     it yet) and the computed numbers omit that deduction under both
     regimes — don't silently drop it from the report.

5. **Portal checklist.** Using `reference/portal_navigation_guide.md`,
   write `./itr-filing/TY2026-27/portal-checklist.md` mapping each
   confirmed figure to its ITR-2 schedule and field, in the recommended
   regime.

## Hard rules

- Never call yourself a substitute for a CA for complex situations (business
  income, foreign assets, a 3rd+ self-occupied property, vacancy/unrealised
  rent adjustments, etc. are out of scope for v1 — tell the user to seek
  professional help for those).
- Never submit or attempt to submit anything to the portal.
- Always surface `tax_engine` warnings to the user rather than absorbing
  them silently.
