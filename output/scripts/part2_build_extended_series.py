"""
ECOH621 Weeks 6-7 assignment -- Part 2: extend the actual series from 2000 to the
most recent complete year.

This assembles, for each of the six Part 1 indicators, one 1996-2024 series built
from THREE vintages/sources in sequence, and says exactly where every splice is:

  1996-1999 : Nattrass (2001) Table 1, citing SARB Quarterly Bulletin, March 2000
              (the same figures used in Part 1; "actual_to_1999" column of the
              corrected GEAR csv).
  2000      : SARB Annual Economic Report 2001 (real GDP growth, private
              investment growth, CPI, deficit) and SARB monthly Bank rate data
              cross-checked against AER 2001 (real bank rate) -- see
              part1_rebuild_table.py docstring for the full derivation.
  2001-2024 : resources/data/Additional data/*.csv --
              current-vintage SARB and StatsSA series (see verification notes
              below and in the accompanying chat transcript).

WHY THIS MATTERS (trap #6, data vintage): every one of these three blocks is a
different data vintage. This script does NOT smooth that over. It keeps a
`source` tag on every cell and marks every vintage change with `splice=True` so
the plotting script can mark it, and so the write-up can discuss it honestly
rather than presenting one continuous line as if it were one consistent series.

Verification of the Additional data folder before use (done interactively, see
chat log): CPI 2000 (5.3%) and Bank rate 2000 (11.81% nominal, averaged by hand
from the monthly file: (11.75*9 + 12.00*3)/12 = 11.81) both independently
reproduce the AER 2001 narrative figures already used in Part 1. The deficit
series reconciles internally (cash_flow_balance / nominal_gdp matches
deficit_pct_gdp_FINAL.csv almost exactly for every year spot-checked). Three
files (sarb_gdp_marketprices_RAW, sarb_nominal_gdp_RAW, sarb_private_investment_RAW)
carry no source/series-code column and are used with that caveat flagged.

KNOWN, UNFILLED GAP (trap #1, employment discontinuity): non-agric formal
employment growth cannot be built as a continuous 1996-2024 series. The source
survey changes underneath it (OHS -> LFS -> QLFS-household -> QES) at several
points, and the supplied "Additional data" extract has no coverage at all for
2016-2024. Rather than splice across incompatible surveys or interpolate over
a nine-year hole, this script leaves those years as NaN and the employment_series
column names which survey (or "GAP") applies to whatever is there. This gap is
itself a Part 2 finding, not a bug to route around.
"""

import pandas as pd

from pathlib import Path

# Paths resolve from this file's own location, so the project folder can be moved
# or copied anywhere (including onto a marker's machine) and still run.
PROJECT = Path(__file__).resolve().parents[2]   # .../Development project
RES = PROJECT / "resources"
BASE = PROJECT / "output"
ADDITIONAL_DIR = RES / "data" / "Additional data"
GEAR_CSV = BASE / "data" / "gear_target_vs_actual_1996_2000_CORRECTED.csv"
OUT_CSV = BASE / "data" / "part2_extended_series_1996_2024.csv"

YEARS = list(range(1996, 2025))

REQUIRED_INDICATORS = [
    "real_gdp_growth_pct",
    "real_private_investment_growth_pct",
    "nonagric_formal_employment_growth_pct",
    "inflation_cpi_pct",
    "deficit_pct_gdp",
    "real_bank_rate_pct",
]


def load_gear_actuals() -> pd.DataFrame:
    """1996-2000 actuals, already corrected/filled in Part 1."""
    gear = pd.read_csv(GEAR_CSV)
    gear = gear[gear["indicator"].isin(REQUIRED_INDICATORS)]
    out = gear[["indicator", "year", "actual_to_1999", "gear_target"]].copy()
    out = out.rename(columns={"actual_to_1999": "actual"})
    out["source"] = "Nattrass (2001) Table 1 / SARB AER 2001"
    out["vintage_block"] = "1996-2000 (Nattrass / SARB AER2001)"
    return out


def build_2001_2024() -> pd.DataFrame:
    """2001-2024 actuals from the Additional data folder."""
    rows = []

    # --- real GDP growth: SARB market-price real GDP, current vintage --------
    gdp = pd.read_csv(ADDITIONAL_DIR / "sarb_gdp_marketprices_1999_2025_RAW.csv")
    for _, r in gdp[(gdp["year"] >= 2001) & (gdp["year"] <= 2024)].iterrows():
        rows.append(("real_gdp_growth_pct", int(r["year"]), r["sarb_growth_pct"],
                      "SARB, current-vintage real GDP at market prices (Additional data; "
                      "no series code given)"))

    # --- real private investment growth: SARB private business enterprises ---
    inv = pd.read_csv(ADDITIONAL_DIR / "sarb_private_investment_1994_2025_RAW.csv")
    for _, r in inv[(inv["year"] >= 2001) & (inv["year"] <= 2024)].iterrows():
        rows.append(("real_private_investment_growth_pct", int(r["year"]), r["growth_pct"],
                      "SARB, real private business enterprise GFCF, current vintage "
                      "(Additional data; no series code given)"))

    # --- CPI: StatsSA headline CPI, annual average -----------------------------
    cpi = pd.read_csv(ADDITIONAL_DIR / "statssa_cpi_1994_2025.csv")
    for _, r in cpi[(cpi["year"] >= 2001) & (cpi["year"] <= 2024)].iterrows():
        rows.append(("inflation_cpi_pct", int(r["year"]), r["cpi_annual_avg_pct"],
                      "StatsSA P0141, headline CPI, annual average (Additional data)"))

    # --- real bank rate: nominal bank rate minus CPI, already computed -------
    real_rate = pd.read_csv(ADDITIONAL_DIR / "real_policy_rate_1994_2025.csv")
    for _, r in real_rate[(real_rate["year"] >= 2001) & (real_rate["year"] <= 2024)].iterrows():
        rows.append(("real_bank_rate_pct", int(r["year"]), r["real_policy_rate_pct"],
                      "SARB Bank rate annual average minus StatsSA CPI (Additional data)"))

    # --- deficit: fiscal-year-ending-March, sign-flipped, mapped to calendar --
    # ASSUMPTION (stated explicitly, per CLAUDE.md workflow rule): fiscal year
    # ending March Y is mapped to calendar year Y-1, since 8 of its 12 months
    # (April Y-1 - March Y-1 -> Dec Y-1, i.e. Apr-Dec) fall in calendar year Y-1.
    # This is a judgement call, not a fact -- flagged for the write-up.
    deficit = pd.read_csv(ADDITIONAL_DIR / "deficit_pct_gdp_1994_2025_FINAL.csv")
    deficit["calendar_year"] = deficit["fiscal_year_ending_march"] - 1
    deficit["deficit_positive"] = -deficit["deficit_pct_gdp"]  # flip sign: + = deficit
    for _, r in deficit[(deficit["calendar_year"] >= 2001) & (deficit["calendar_year"] <= 2024)].iterrows():
        rows.append(("deficit_pct_gdp", int(r["calendar_year"]), r["deficit_positive"],
                      f"SARB cash-flow balance / nominal GDP, FY ending March "
                      f"{int(r['fiscal_year_ending_march'])} mapped to calendar year "
                      f"{int(r['calendar_year'])} (Additional data; assumption stated in script)"))

    # --- employment: patchy LFS/QES coverage, huge 2016-2024 gap --------------
    # NOTE: row 2 of this csv ("OHS,1996,,,Nattrass 1996 GEAR table (actual,
    # own units - ...)") has an unescaped comma inside its unquoted source
    # field, which throws off pandas' column-count inference for the whole
    # file if read naively. Read with the python engine and cap the number of
    # splits per line instead.
    with open(ADDITIONAL_DIR / "employment_series_SEGMENTED.csv", encoding="utf-8") as f:
        lines = [line.rstrip("\n") for line in f]
    header = lines[0].split(",")
    emp_rows = [line.split(",", maxsplit=len(header) - 1) for line in lines[1:] if line]
    emp = pd.DataFrame(emp_rows, columns=header)
    emp["growth_pct"] = pd.to_numeric(emp["growth_pct"], errors="coerce")
    # Map each dated LFS/QES observation with a growth_pct to an approximate
    # calendar year (the March-dated survey round approximates the prior
    # calendar year's average employment level).
    emp_growth = emp.dropna(subset=["growth_pct"]).copy()
    for _, r in emp_growth.iterrows():
        date = str(r["date"])
        if "-03" in date:
            cal_year = int(date.split("-")[0]) - 1
        elif "-12" in date:
            cal_year = int(date.split("-")[0])
        else:
            continue
        if 2001 <= cal_year <= 2024:
            rows.append(("nonagric_formal_employment_growth_pct", cal_year, r["growth_pct"],
                         f"StatsSA {r['regime']}, {r['source']}"))

    return pd.DataFrame(rows, columns=["indicator", "year", "actual", "source"])


def assemble() -> pd.DataFrame:
    gear_block = load_gear_actuals()
    ext_block = build_2001_2024()
    ext_block["gear_target"] = pd.NA
    ext_block["vintage_block"] = "2001-2024 (Additional data / current vintage)"

    combined = pd.concat([gear_block, ext_block], ignore_index=True, sort=False)

    # Full indicator x year grid so gaps are visible as NaN, not missing rows.
    full_index = pd.MultiIndex.from_product([REQUIRED_INDICATORS, YEARS], names=["indicator", "year"])
    combined = (
        combined.set_index(["indicator", "year"])
        .reindex(full_index)
        .reset_index()
    )
    return combined


if __name__ == "__main__":
    df = assemble()
    df.to_csv(OUT_CSV, index=False)
    print(f"Saved extended long-format series to: {OUT_CSV}")

    print("\nCoverage check (non-missing 'actual' years per indicator, 1996-2024):")
    for ind in REQUIRED_INDICATORS:
        sub = df[df["indicator"] == ind]
        present = sub.dropna(subset=["actual"])["year"].tolist()
        missing = sorted(set(YEARS) - set(present))
        print(f"  {ind:42s}: {len(present)}/{len(YEARS)} years present. "
              f"Missing: {missing if missing else 'none'}")
