# Annual Information Statement (AIS)

**Income Tax Department, Government of India**
*(Mock document for testing purposes only — not a real AIS export)*

---

## Taxpayer Information

| Field | Value |
|---|---|
| Name | Aarav Sharma |
| PAN | ABCDE1234F |
| Assessment Year | 2027-28 |
| Financial Year | 2026-27 |
| Date of Birth | 14-Mar-1989 |
| Mobile | XXXXXX7890 |
| Email | a.sharma.sample@example.com |

---

## Part A: Salary & TDS Information

### TDS on Salary (Section 192)

| Information Source | Employer (Deductor) | TAN | Gross Salary Paid (Rs.) | TDS Deducted (Rs.) |
|---|---|---|---|---|
| Form 24Q (Q4) | Nimbus Technologies Pvt Ltd | BLRN12345E | 12,00,000 | 1,18,560 |

> Note: Salary figure above is reported by the employer for cross-check only.
> Authoritative salary figure for computation should be taken from Form 16
> Part B, not from this AIS entry.

---

## Part B: Interest, Dividend & Other Income Information

### SFT-016 / TDS 194A — Interest Income

| Information Source | Reporting Entity | Description | Amount Reported (Rs.) | TDS Deducted (Rs.) |
|---|---|---|---|---|
| SB Account Interest | HDFC Bank Ltd | Savings account interest credited | 8,200 | 0 |
| Term Deposit Interest | ICICI Bank Ltd | Interest on fixed deposit (FD), gross | 25,400 | 2,540 |

**Total Interest Income Reported: Rs. 33,600**

### SFT-015 / TDS 194 — Dividend Income

| Information Source | Reporting Entity | Description | Amount Reported (Rs.) | TDS Deducted (Rs.) |
|---|---|---|---|---|
| Dividend Distribution | Reliance Industries Ltd (Registrar: KFin Technologies) | Equity dividend | 9,500 | 0 |
| Dividend Distribution | HDFC Bank Ltd (Registrar: KFin Technologies) | Equity dividend | 5,800 | 0 |

**Total Dividend Income Reported: Rs. 15,300**

---

## Part C: Securities Market / Mutual Fund Transactions (SFT Summary)

> The following entries are reported by stock exchanges, depositories
> (NSDL/CDSL), and mutual fund RTAs under various SFT codes. These are
> provided for cross-verification against your broker capital-gains (PnL)
> statement. Do not feed these figures directly into the tax computation —
> reconcile against the PnL statement instead.

| SFT Code | Information Source | Description | Transaction Type | Gross Amount Reported (Rs.) |
|---|---|---|---|---|
| SFT-018 | Zerodha Broking Ltd (Depository: CDSL) | Purchase/sale of listed equity shares | Purchase + Sale (aggregated) | 18,45,000 |
| SFT-018 | Zerodha Broking Ltd (Depository: CDSL) | Purchase/sale of equity-oriented mutual fund units | Purchase + Sale (aggregated) | 6,20,000 |
| SFT-018 | Zerodha Broking Ltd (Depository: CDSL) | Purchase/sale of debt-oriented mutual fund units | Purchase + Sale (aggregated) | 3,10,000 |
| SFT-021 | RBI / Exchange-reported VDA intermediary | Transfer of Virtual Digital Assets (crypto) | Purchase + Sale (aggregated) | 1,85,000 |
| SFT-011 | Sub-Registrar Office, Pune | Purchase/sale of immovable property (land) | Sale | 95,00,000 |

**Note:** Securities/property transaction values above are gross transaction
values (not gains) and are intentionally aggregated/summarized, as they
would appear in a real AIS Part B/SFT summary. Actual per-trade gain/loss
must be taken from the broker's capital-gains PnL statement
(see `pnl_sample.csv`), and the unlisted-land transaction above corresponds
to the `LAND_BUILDING` row in that file.

---

## Part D: Tax Deducted at Source (TDS) — Summary

| Section | Description | Amount (Rs.) |
|---|---|---|
| 192 | TDS on Salary | 1,18,560 |
| 194A | TDS on FD Interest | 2,540 |

**Total TDS as per AIS: Rs. 1,21,100**

---

*This is a system-generated mock statement created solely for testing the
itr-filing plugin's extraction and computation pipeline. It does not
represent any real taxpayer's data.*
