"""
ECOH621 Weeks 6-7 assignment -- Part 3, step 1: build the regression dataset.

DESIGN DECISION (trap #6, data vintage -- made explicitly):
The Part 2 display series deliberately chains three vintages so the reader can
see GEAR marked against the data of its own day. That is right for a *table*,
but wrong for a *regression*: estimating on a series whose definition changes
mid-sample builds the break into the coefficients.

So Part 3 estimates on ONE consistent vintage throughout -- the current-vintage
SARB/StatsSA series in the "Additional data" folder, 1994-2024. Boshoff & Fourie's
factor-cost GDP series is retained as a SENSITIVITY check (trap #4), not as the
main specification.

Variables (all annual, 1994-2024):
  inv_growth      real private business enterprise GFCF growth, %   (dependent)
  gdp_growth_lag1 real GDP growth lagged one year, %                (DEMAND channel)
  real_rate       real bank rate = nominal Bank rate - CPI, %       (cost of capital)
  deficit_gdp     main budget balance as % of GDP, deficit POSITIVE (SIGNAL channel)

SIGN CONVENTION, stated once and used throughout: deficit_gdp is POSITIVE when
the budget is in deficit. So the GEAR/"confidence" hypothesis predicts a
NEGATIVE coefficient (a bigger deficit damages confidence and so depresses
investment); the LABOUR/ILO "demand" hypothesis predicts a POSITIVE coefficient
on gdp_growth_lag1 (investment follows demand) and is agnostic-to-positive on
the deficit (fiscal expansion supports demand).

GDP GROWTH SOURCE for the main sample: SARB market-price real GDP is only
supplied from 1999 in the Additional data folder, so for 1994-1998 the lagged
GDP growth term is taken from Boshoff & Fourie. This is itself a splice and is
flagged in the output; the sensitivity specifications below test whether it
matters.
"""

import pandas as pd

from pathlib import Path

# Paths resolve from this file's own location, so the project folder can be moved
# or copied anywhere (including onto a marker's machine) and still run.
PROJECT = Path(__file__).resolve().parents[2]   # .../Development project
RES = PROJECT / "resources"
BASE = PROJECT / "output"
ADD = RES / "data" / "Additional data"
BF_CSV = RES / "data" / "sa_gdp_1911_2017.csv"
OUT = BASE / "data" / "part3_regression_data.csv"


def build() -> pd.DataFrame:
    # Dependent: real private investment growth (current vintage)
    inv = pd.read_csv(ADD / "sarb_private_investment_1994_2025_RAW.csv")
    inv = inv[["year", "growth_pct"]].rename(columns={"growth_pct": "inv_growth"})

    # Real GDP growth, current vintage (SARB market prices, 2000-2025)
    gdp_sarb = pd.read_csv(ADD / "sarb_gdp_marketprices_1999_2025_RAW.csv")
    gdp_sarb = gdp_sarb[["year", "sarb_growth_pct"]].rename(
        columns={"sarb_growth_pct": "gdp_growth_sarb"})

    # Real GDP growth, Boshoff & Fourie factor-cost vintage (for 1994-98 and sensitivity)
    bf = pd.read_csv(BF_CSV)
    bf = bf[["year", "real_gdp_growth_pct"]].rename(
        columns={"real_gdp_growth_pct": "gdp_growth_bf"})

    # Real bank rate (nominal Bank rate annual avg - CPI annual avg)
    rate = pd.read_csv(ADD / "real_policy_rate_1994_2025.csv")
    rate = rate[["year", "real_policy_rate_pct"]].rename(
        columns={"real_policy_rate_pct": "real_rate"})

    # Deficit: fiscal year ending March Y -> calendar year Y-1; sign flipped so
    # a deficit is POSITIVE.
    def_ = pd.read_csv(ADD / "deficit_pct_gdp_1994_2025_FINAL.csv")
    def_["year"] = def_["fiscal_year_ending_march"] - 1
    def_["deficit_gdp"] = -def_["deficit_pct_gdp"]
    def_ = def_[["year", "deficit_gdp"]]

    df = inv.merge(gdp_sarb, on="year", how="outer") \
            .merge(bf, on="year", how="outer") \
            .merge(rate, on="year", how="outer") \
            .merge(def_, on="year", how="outer")
    df = df.sort_values("year").reset_index(drop=True)

    # Preferred GDP growth: SARB current vintage where available, B&F before that.
    df["gdp_growth"] = df["gdp_growth_sarb"].fillna(df["gdp_growth_bf"])
    df["gdp_growth_source"] = df["gdp_growth_sarb"].notna().map(
        {True: "SARB market prices", False: "Boshoff & Fourie factor cost"})
    df.loc[df["gdp_growth"].isna(), "gdp_growth_source"] = None

    # Lags (the demand channel is LAGGED -- investment responds to last year's demand)
    df["gdp_growth_lag1"] = df["gdp_growth"].shift(1)
    df["gdp_growth_bf_lag1"] = df["gdp_growth_bf"].shift(1)

    return df


if __name__ == "__main__":
    df = build()
    df.to_csv(OUT, index=False)
    print(f"Saved regression dataset to: {OUT}\n")

    cols = ["year", "inv_growth", "gdp_growth_lag1", "real_rate", "deficit_gdp"]
    est = df[cols].dropna()
    print(f"Estimation sample (complete cases): {int(est['year'].min())}-{int(est['year'].max())}, N = {len(est)}\n")
    print(df[["year", "inv_growth", "gdp_growth", "gdp_growth_source", "real_rate", "deficit_gdp"]].to_string(index=False))
