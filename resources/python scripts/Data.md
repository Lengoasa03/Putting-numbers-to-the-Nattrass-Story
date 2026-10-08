# Starter data â€” ECOH621 Weeks 6â€“7 assignment

Three files. Read this before you use any of them.

| File | What it is | Status |
|---|---|---|
| `sa_gdp_1911_2017.csv` | Boshoff & Fourie's 106-year GDP series | **Complete and verified** |
| `gear_target_vs_actual_1996_2000.csv` | GEAR's projections and the outturn to 1999 | **Complete**, with flagged cells |
| `macro_series_1994_2024_TEMPLATE.csv` | The extension frame for Part 2 | **Partly filled â€” you complete it** |

---

## 1. `sa_gdp_1911_2017.csv`

**Source:** Boshoff, W.H. & Fourie, J. (2020), "The South African economy in the twentieth century", Appendix 1. Transcribed from the PDF in this folder.

| Column | Meaning |
|---|---|
| `year` | 1911â€“2017, no gaps |
| `gdp_current_prices_Rm` | GDP at factor cost, current prices, R millions |
| `gdp_deflator_2010eq100` | GDP deflator, 2010 = 100 |
| `gdp_constant_2010_prices_Rm` | GDP at factor cost, constant 2010 prices, R millions |
| `real_gdp_growth_pct` | Annual real growth, % (blank for 1911) |

**Checks I ran, so you don't have to repeat them:** all 107 years present; the growth column reconciles exactly against the real GDP column in every year. The deflator is printed to two decimals in the source, so `current Ã· deflator Ã— 100` differs from the stated real column by up to ~0.7% in the early years. That is rounding in the published table, not a transcription error â€” use the real column as given rather than recomputing it.

**What you still have to worry about:** this series is spliced. Boshoff & Fourie join a 1911â€“68 series (Botha 1968) to a 1946â€“2017 SARB series, adjusting the earlier 90 years by the average difference over the 14 overlapping years (1946â€“59). It is GDP at **factor cost**, not market prices. Both facts matter if you compare it to anything else.

---

## 2. `gear_target_vs_actual_1996_2000.csv`

Long format â€” one row per indicator-year.

| Column | Meaning |
|---|---|
| `indicator` | The variable |
| `year` | 1996â€“2000 |
| `gear_target` | GEAR's Integrated Scenario projection |
| `actual_to_1999` | The outturn as Nattrass reported it (blank after 1999) |
| `scan_reconstructed` | `R` = see the warning below |

**Sources:** targets from Nattrass (1996) Table 1; outturn from Nattrass (2001) Table 1, which cites the SARB *Quarterly Bulletin*, March 2000.

**The `R` flag matters.** Our PDFs of both Nattrass papers are scans, and some digits came through the OCR corrupted. Where a value was unambiguous from context or from cross-checking the two papers against each other, I reconstructed it and marked it `R`. Six cells are affected. Two examples of how the cross-check works:

- 1998 private investment appears as `0.3` in the 1996 paper and `9.3` in the 2001 paper. The surrounding path (9.3, 9.1, ?, 13.9) and the 2001 reprint both say 9.3.
- 1998 predicted deficit appears as `-35` in the 2001 scan; the 1996 table gives 3.5. Decimal point lost.

**If a figure carries `R` and it matters to your argument, verify it against a clean copy of the paper before you rely on it.** Do not treat the flag as decoration.

**One value I could not resolve:** GEAR's predicted CPI inflation path reads 8.4 â†’ 10.9 â†’ 9.6 â†’ 7.7. A predicted *rise* to 10.9% in 1997 under a disinflationary strategy is odd, and I suspect the 1997 cell is an OCR artefact. Treat that single number with suspicion.

---

## 3. `macro_series_1994_2024_TEMPLATE.csv` â€” read this carefully

**This file is deliberately incomplete, and you need to know exactly how.**

`real_gdp_growth_pct` is filled for **1994â€“2017** from Boshoff & Fourie, with the source named in the adjacent column. Every other cell is empty.

I have not filled the investment, employment, inflation, deficit or interest rate series, and **you should be suspicious of any teaching dataset that hands you macro figures without a traceable source.** Those series have to come from SARB and StatsSA, be pulled on a single consistent vintage and definition, and be labelled as such. Numbers invented to fill a template would be worse than no numbers, because they would look usable.

### What to pull, and from where

| Column | Source | Note |
|---|---|---|
| `real_gdp_growth_pct` (2018â€“24) | SARB QB, GDP at constant prices | See the vintage warning below |
| `real_private_investment_growth_pct` | SARB QB â€” gross fixed capital formation, private business enterprises, constant prices | Not total GFCF. Private only. |
| `nonagric_formal_employment_growth_pct` | StatsSA QES for the formal non-agricultural count; QLFS for the household-side series | **Record which one you used in `employment_series_name`** |
| `inflation_cpi_pct` | StatsSA P0141, headline CPI, annual average | Say whether annual average or Dec/Dec |
| `deficit_pct_gdp` | National Treasury Budget Review, main budget balance | Sign convention: record deficits as positive or negative, and be consistent |
| `nominal_policy_rate_pct` | SARB repo rate | Bank rate before 1998, repo after â€” a definitional break |
| `real_policy_rate_pct` | Nominal rate minus CPI inflation | This is how Nattrass constructed hers |

Boshoff & Fourie cite two SARB codes directly: **KBP6006J** (GDP at current prices) and **KBP6006Y** (GDP at constant 2010 prices). Other series codes I have deliberately not guessed â€” look them up rather than trusting a code you cannot verify.

### The vintage trap, made concrete

Compare 1996â€“99 real GDP growth from the two sources already in this folder:

| Year | Boshoff & Fourie (2020) | Nattrass (2001), SARB QB March 2000 |
|---|---|---|
| 1996 | 4.59 | 4.2 |
| 1997 | 2.28 | 2.5 |
| 1998 | âˆ’0.10 | 0.6 |
| 1999 | 1.97 | 1.2 |

Same country, same years, different numbers â€” because the definitions differ (factor cost versus market prices) and because national accounts get revised for decades after the fact. Nattrass was marking GEAR against the data available in 2000; you will be marking it against data revised many times since.

**This is not a nuisance to be smoothed over. It is a finding.** Decide which vintage you are judging GEAR by, justify the choice, and do not mix the two inside a single series. A submission that notices this and handles it deliberately is already most of the way to a good mark.

---

## Suggested first steps

1. Open `gear_target_vs_actual_1996_2000.csv` and reshape it wide. That is your Part 1 table, nearly done.
2. Fill the template for the years and columns you need. Start with GDP and private investment â€” those carry Part 3.
3. Only then start modelling. If your regression runs before you have looked at the series, you have gone too fast.

---

## Notes for me â€” not for students

- **The access question is only half solved.** The GDP spine and the GEAR table are real and complete; the rest still needs one clean pull from SARB/StatsSA. Two options: (a) leave it as a skill to be assessed, since the trap list rewards handling it well, or (b) do one authoritative pull, drop it into the template, and redistribute â€” which removes the access barrier entirely but also removes the data-handling assessment. If you want (b) and can export from Econdata or hand me a file, I can merge and validate it.
- If access turns out to be patchy across the class, (b) is the fairer call â€” otherwise Part 2 marks connectivity rather than economics.
- Consider walking through the vintage table in class. It is the single most useful thing in this folder and students will not find it on their own.