# GEAR vs Reality: did South African investment follow confidence or demand?

An empirical test of the bet at the centre of South Africa's 1996 macroeconomic
policy debate, using thirty years of outcomes.

## The question

In 1996 Nicoli Nattrass described the South African policy debate as a wager.
Two camps disagreed about almost everything but staked their strategies on the
same unknown: how would private investors respond?

- **SAF/GEAR** held that investment follows **confidence**, signalled by fiscal
  consolidation. Get the deficit and inflation down, and investment follows.
- **LABOUR/ILO** held that investment follows **demand**. Cut spending and you
  cut the very thing investment responds to.

Nattrass declined to pick a winner, because the profession knew too little about
how investors actually behave. This project revisits the question with data
through 2024.

## What was found

**GEAR delivered the stability it promised and almost none of the growth.**
Scoring each indicator against GEAR's own target for that year (or, after 2000,
its final 2000 target as a steady-state benchmark):

| Indicator | Targets met |
|---|---|
| CPI inflation | 27 of 29 years |
| Real bank/repo rate | 18 of 29 years |
| Budget deficit (% GDP) | 12 of 29 years |
| Real GDP growth | 1 of 29 years (1996) |
| Non-agric. formal employment growth | 1 of 12 years with data (2006) |
| Real private investment growth | **never**, in 29 years |

The three stabilisation targets were met in most years. The three growth targets
almost never were.

**The regression result is not the obvious one.** Estimating real private
investment growth on lagged GDP growth, the real interest rate and the deficit
(annual, 1994–2024, N = 31, Newey–West standard errors):

| Specification | Lagged GDP growth (demand) | Deficit/GDP (signal) |
|---|---|---|
| Full sample | 0.52 (p = 0.18) | **−1.83 (p = 0.002)** |
| Pre-2008 | 0.87 (p = 0.11) | **+1.67 (p = 0.008)** |
| 2008 onwards | 0.30 (p = 0.32) | **−2.31 (p < 0.001)** |
| Excl. 2009 & 2020 | **0.94 (p = 0.004)** | −0.70 (p = 0.15) |
| 2008 on, excl. 2009 & 2020 | **0.75 (p < 0.001)** | −0.14 (p = 0.83) |

Read the first row alone and GEAR wins: the deficit carries exactly the sign the
confidence argument predicts. That reading does not survive two checks.

1. A Chow test rejects parameter stability at 2008 (F = 4.01, p = 0.013), and the
   deficit coefficient **flips sign** while staying significant in both
   directions. A coefficient that reverses is not a stable behavioural parameter.
2. In 2009 and 2020 the deficit exploded and investment collapsed, but the
   recession caused both. Automatic stabilisers widen deficits in downturns by
   construction. Dropping those two years of 31 reverses the conclusion: the
   signal channel loses significance and the demand channel becomes strong.

On balance the evidence favours the demand channel, though the firmer finding is
the negative one: there is no reliable evidence for the confidence channel GEAR
was built on. That fits the descriptive result, where the consolidation arrived
and the investment never did.

**Reported honestly:** the demand result does not survive switching to Boshoff &
Fourie's factor-cost GDP series (0.26, p = 0.77), nothing here is identified
causally, and the employment series has a nine-year hole. The conclusion is that
the evidence is mixed, and the mixing has a traceable source.

## Repository layout

```
.
├── resources/              source material (read-only)
│   ├── data/               SARB and StatsSA series
│   └── python scripts/     the supplied data dictionary and starter notebook
└── output/
    ├── data/               generated datasets
    ├── figures/            7 charts
    ├── notebooks/          3 Jupyter notebooks, the main analysis
    ├── report/             the write-up and supporting drafts
    └── scripts/            12 Python scripts (same analysis, plus doc builders)
```

The notebooks and the scripts implement the same analysis and produce
byte-identical data and figures. The notebooks are the readable version; the
scripts additionally build the .docx report and the .pdf disclosure.

## Reproducing the analysis

```bash
git clone https://github.com/Lengoasa03/Putting-numbers-to-the-Nattrass-Story.git
cd Putting-numbers-to-the-Nattrass-Story
pip install -r requirements.txt
```

Then run the notebooks in order:

1. `output/notebooks/01_part1_gear_table.ipynb` — rebuilds the GEAR vs reality
   table for 1996–2000 and writes the corrected dataset the others depend on.
2. `output/notebooks/02_part2_extend_series.ipynb` — extends every series to 2024
   and produces the charts.
3. `output/notebooks/03_part3_regression.ipynb` — the regression, diagnostics,
   sample splits and sensitivity checks.

The notebooks locate the project folder by walking up from the working
directory, so they run from either the repository root or their own folder.

## Data sources

- South African Reserve Bank, *Quarterly Bulletin* and *Annual Economic Report*
  (GDP, gross fixed capital formation by private business enterprises, the Bank
  and repo rate, the national government balance).
- Statistics South Africa, P0141 Consumer Price Index; QES and LFS/QLFS for
  employment.
- Boshoff, W.H. and Fourie, J. (2020) 'The South African economy in the
  twentieth century', in Boshoff, W.H. (ed.) *Business Cycles and Structural
  Change in South Africa*. Cham: Springer.
- Nattrass, N. (1996) 'Gambling on investment: competing economic strategies in
  South Africa', *Transformation*, 31, pp. 25–42.
- Nattrass, N. (2001) 'High productivity now: a critical review of South Africa's
  growth strategy', *Transformation*, 45.
- South Africa (1996) *Growth, Employment and Redistribution: A Macroeconomic
  Strategy*. Pretoria: Department of Finance.

## Not included here

Two PDFs the analysis cites are excluded, because they are not mine to
redistribute: the Nattrass (2001) journal article and the course assignment
brief. Everything needed to run the code is present.

## A note on data handling

Three decisions are worth knowing about, because each could have been made
differently:

- **An error was found in the supplied data.** The GEAR inflation targets given
  for 1996–98 (8.4 / 10.9 / 9.6) come from the discarded Base Scenario, not the
  Integrated Scenario that government adopted and that every other row uses. The
  verified figures are 8.0 / 9.7 / 8.1. The same mistake appears in Nattrass's
  own 2001 table, so it is inherited from the published source.
- **Vintages are not blended silently.** The descriptive series deliberately
  chains three data vintages so GEAR is judged against the data of its own day,
  with the join marked on every chart. The regression holds one vintage fixed
  instead, so a change in definition is not estimated into the coefficients.
- **Gaps are left as gaps.** Formal employment is only observable for 12 of 29
  years, and nothing in the available data covers 2016–2024. No value is
  interpolated across that hole, and no 2000 employment figure is invented.

## AI use

Claude (Anthropic) was used for code, for locating figures inside long primary
sources, and for editing. Every number in the report comes from running the
included code on the cited data. The interpretation and the conclusions are
mine. `output/report/AI_use_disclosure.pdf` sets this out in full.
