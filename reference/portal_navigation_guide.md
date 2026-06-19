# ITR-2 Portal Navigation Guide

Maps computed figures to where they're entered on the income tax e-filing
portal (incometax.gov.in) for ITR-2. This plugin never submits anything —
use this guide to manually enter values yourself.

## Salary
- Schedule Salary -> "Gross Salary" -> enter `salary_gross` from Form 16
  Part B.
- Schedule Salary -> "Less: Standard deduction u/s 19" -> auto-populated by
  the portal based on regime; cross-check against this plugin's
  `taxable_income_at_slab` calculation.

## Chapter VIII deductions (old regime only)
- Schedule VI-A -> "80C" (or equivalent renamed section) -> enter the
  `deductions_80c` amount, capped at Rs. 1,50,000.
- Schedule VI-A -> "80D" (or equivalent renamed section) -> enter the
  `deductions_80d` amount, observing the self/parent/senior-citizen caps.

## Capital gains (Schedule CG)
- Schedule CG -> "Equity/equity-fund STT-paid, short-term" -> sum of
  `EQUITY_STT` entries with `is_long_term=False`.
- Schedule CG -> "Equity/equity-fund STT-paid, long-term" -> sum of
  `EQUITY_STT` entries with `is_long_term=True`; the portal applies the
  Rs. 1,25,000 exemption automatically.
- Schedule CG -> "Other long-term assets (debt funds, unlisted shares)" ->
  sum of `GENERAL` entries with `is_long_term=True`.
- Schedule CG -> "Land or building" -> sum of `LAND_BUILDING` entries; if any
  were acquired before 23 July 2024, the portal will ask whether you want
  indexed or non-indexed computation — use whichever this plugin's
  `capital_gains_tax` output selected as cheaper for that entry.
- Schedule VDA -> enter each `VDA` gain entry separately; the portal does not
  allow netting VDA losses against gains or other income — enter losses for
  disclosure only, expect no tax benefit from them.

## AIS cross-check
- Before finalizing, open the AIS (Annual Information Statement) on the
  portal and compare every income head against what you entered. If the
  plugin flagged a mismatch warning, resolve it (correct your entry, or file
  an AIS feedback) before submitting.
