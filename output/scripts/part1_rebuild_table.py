"""
ECOH621 Weeks 6-7 assignment -- Part 1: Rebuild the GEAR-vs-reality table.

Source data:
  - resources/data/gear_target_vs_actual_1996_2000 (1).csv
    Long-format GEAR targets (Nattrass 1996 Table 1 / RSA 1996 "Integrated Scenario")
    and outturn to 1999 (Nattrass 2001 Table 1, sourced from SARB Quarterly Bulletin,
    March 2000).

Corrections applied here, and why (see accompanying tutorial/report for full discussion):

1. Inflation (CPI) GEAR-target row, 1996-98.
   The supplied csv gives 8.4 / 10.9 / 9.6 for 1996-98. These figures are NOT from
   GEAR's "Integrated Scenario" (the scenario government actually adopted, and the
   source of every other row in the csv) -- they are from a different table in the
   same 1996 document, the discarded "Base Scenario" (a do-nothing baseline GEAR was
   built to beat). Verified directly against South Africa (1996) "Growth, Employment
   and Redistribution: A Macroeconomic Strategy", Department of Finance -- the
   "Integrated Scenario Projections: 1996-2000" table gives Inflation (CPI) as
   8.0 / 9.7 / 8.1 / 7.7 / 7.6 for 1996-2000. Only 1999 (7.7) happens to coincide
   between the two scenarios, which is presumably why the mismatch went unnoticed.
   Nattrass's own 2001 "GEAR vs Reality" Table 1 repeats the Base Scenario figures
   for 1996-98 -- i.e. this is an error inherited from the original academic source,
   not a transcription fault in this course's csv. We use the verified Integrated
   Scenario values here and flag the change explicitly.

2. scan_reconstructed ("R") cells.
   Every R-flagged cell was checked against Nattrass (2001) Table 1 directly and
   against the original 1996 GEAR document where the cell is a *target* value. Every
   one matches the value already given in the supplied csv -- i.e. the R-flag
   corrections made by the person who compiled this course's csv were all correct.
   No further changes needed for those cells. Note: Data.md claims "six cells are
   affected" but only five carry the R flag in the actual csv (deficit_pct_gdp 1996
   & 1998, real_wage_growth_private_pct 1997, reer_change_pct 1998,
   real_gdp_growth_pct 1997) -- flagged here as a minor discrepancy worth a one-line
   footnote in the write-up, not something to silently "fix" by inventing a sixth.

3. 2000 actuals.
   Nattrass (2001) Table 1 stops at 1999 (her data source, SARB Quarterly Bulletin
   March 2000, predates full-year 2000 figures). The csv's actual_to_1999 column is
   therefore blank for 2000 by design. Four of the six required indicators are filled
   in here from SARB's Annual Economic Report 2001 (the first SARB report to cover
   full calendar-year 2000):
     - real_gdp_growth_pct        : 3.0  (AER 2001, "growth rate of 3% in 2000")
     - real_private_investment_growth_pct : 5.0  (AER 2001, real GFCF by private
       business enterprises, full-year 2000)
     - inflation_cpi_pct          : 5.3  (AER 2001, average CPI, 2000; explicitly
       compared there to 5.2% in 1999)
     - deficit_pct_gdp            : 2.0  (AER 2001, national government deficit
       before borrowing, fiscal 2000/01 -- a FISCAL, not calendar, year figure;
       flagged as a definitional mismatch with the other rows in the report)
   Two indicators are left blank rather than filled with an estimate, per this
   project's data-integrity rule against inventing numbers to fill a template:
     - nonagric_formal_employment_growth_pct: AER 2001 gives private-sector formal
       non-agric employment at -2.0% and public-sector at -4.1% for 2000, but no
       single combined total for calendar 2000 is stated in the report. Computing
       one would require a sector employment-share weight I have not sourced from
       a primary document, so it is left blank rather than fabricated.
     - real_bank_rate_pct: filled in a later pass once the "Additional data"
       folder (resources/data/Additional data/) was supplied.
       sarb_bankrate_monthly_1994_2025_RAW.csv gives 11.75% for Jan-Sep and 12.00%
       for Oct-Dec 2000, averaging to 11.81% -- independently matching both the
       AER 2001 repo-rate change dates above and real_policy_rate_1994_2025.csv's
       precomputed figure. CPI for 2000 (5.3%, matching AER 2001 exactly) gives a
       real bank rate of 11.81 - 5.3 = 6.51%.

Everything else in the csv is left as supplied and is fully source-verified.
"""

import pandas as pd

from pathlib import Path

# Paths resolve from this file's own location, so the project folder can be moved
# or copied anywhere (including onto a marker's machine) and still run.
PROJECT = Path(__file__).resolve().parents[2]   # .../Development project
RES = PROJECT / "resources"
BASE = PROJECT / "output"
RAW_CSV = RES / "data" / "gear_target_vs_actual_1996_2000 (1).csv"
OUT_DIR = BASE / "data"

# Indicators required by the assignment brief for Part 1
REQUIRED_INDICATORS = [
    "real_gdp_growth_pct",
    "real_private_investment_growth_pct",
    "nonagric_formal_employment_growth_pct",
    "inflation_cpi_pct",
    "deficit_pct_gdp",
    "real_bank_rate_pct",
]

# Verified against South Africa (1996) "Growth, Employment and Redistribution:
# A Macroeconomic Strategy", Department of Finance, "Integrated Scenario
# Projections: 1996-2000" table (p.4 of the document).
CORRECTED_INFLATION_TARGET = {
    1996: 8.0,
    1997: 9.7,
    1998: 8.1,
    1999: 7.7,   # unchanged -- coincides with the Base Scenario figure already in the csv
    2000: 7.6,   # csv had this blank; supplied here from the primary source
}

# 2000 actuals, source-verified against SARB Annual Economic Report 2001 (see
# module docstring, point 3). Only cells with a directly stated figure are filled;
# nonagric_formal_employment_growth_pct and real_bank_rate_pct are deliberately
# left blank -- see docstring for why.
ACTUAL_2000 = {
    "real_gdp_growth_pct": 3.0,
    "real_private_investment_growth_pct": 5.0,
    "inflation_cpi_pct": 5.3,
    "deficit_pct_gdp": 2.0,  # fiscal 2000/01, not calendar year -- flagged in docstring
    "real_bank_rate_pct": 6.51,  # 11.81 nominal (SARB monthly bank rate) - 5.3 CPI
}


def load_and_correct(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    original_1996_98 = df.loc[
        (df["indicator"] == "inflation_cpi_pct") & (df["year"].between(1996, 1998)),
        "gear_target",
    ].tolist()

    for year, value in CORRECTED_INFLATION_TARGET.items():
        mask = (df["indicator"] == "inflation_cpi_pct") & (df["year"] == year)
        if mask.any():
            df.loc[mask, "gear_target"] = value
        else:
            new_row = {
                "indicator": "inflation_cpi_pct",
                "year": year,
                "gear_target": value,
                "actual_to_1999": pd.NA,
                "scan_reconstructed": pd.NA,
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    print("Inflation target correction applied (Base Scenario -> Integrated Scenario):")
    print(f"  1996-98 supplied csv values : {original_1996_98}")
    print(f"  1996-2000 corrected values  : {[CORRECTED_INFLATION_TARGET[y] for y in range(1996, 2001)]}")
    print("  Source: South Africa (1996) Growth, Employment and Redistribution, "
          "Integrated Scenario Projections table.\n")

    for indicator, value in ACTUAL_2000.items():
        mask = (df["indicator"] == indicator) & (df["year"] == 2000)
        df.loc[mask, "actual_to_1999"] = value

    print("2000 actuals filled from SARB Annual Economic Report 2001:")
    for indicator, value in ACTUAL_2000.items():
        print(f"  {indicator:40s}: {value}")
    print("  nonagric_formal_employment_growth_pct left blank -- no single "
          "directly-sourced full-year 2000 total found (see docstring).\n")

    return df


def build_part1_table(df: pd.DataFrame) -> pd.DataFrame:
    """Reshape the six required indicators to wide format: one row per indicator,
    one (year, target/actual) pair of columns per year 1996-2000."""
    subset = df[df["indicator"].isin(REQUIRED_INDICATORS)].copy()

    table = subset.pivot_table(
        index="indicator",
        columns="year",
        values=["gear_target", "actual_to_1999"],
        aggfunc="first",
    )
    table = table.swaplevel(axis=1).sort_index(axis=1, level=0)
    return table.reindex(REQUIRED_INDICATORS)


if __name__ == "__main__":
    gear = load_and_correct(RAW_CSV)

    part1 = build_part1_table(gear)
    print("Part 1 rebuilt table (targets and 1996-99 actuals; 2000 actuals pending SARB/StatsSA/Treasury pull):")
    print(part1)

    corrected_long_path = OUT_DIR / "gear_target_vs_actual_1996_2000_CORRECTED.csv"
    gear.to_csv(corrected_long_path, index=False)
    print(f"\nSaved corrected long-format csv to: {corrected_long_path}")

    wide_path = OUT_DIR / "part1_gear_vs_reality_table.csv"
    part1.to_csv(wide_path)
    print(f"Saved Part 1 wide table (report-ready) to: {wide_path}")

    r_flagged = gear[gear["scan_reconstructed"] == "R"]
    print("\nR-flagged cells (all verified against Nattrass 2001 Table 1 / RSA 1996 -- no changes needed):")
    print(r_flagged[["indicator", "year", "gear_target", "actual_to_1999"]].to_string(index=False))
