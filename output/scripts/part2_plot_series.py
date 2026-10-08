"""
ECOH621 Weeks 6-7 assignment -- Part 2: plot each indicator's actual series
(1996-2024) against GEAR's targets (1996-2000).

For each of the six indicators:
  - the actual series is plotted as a solid line, with a gap wherever data is
    genuinely missing (matplotlib breaks the line across NaN automatically --
    it is not interpolated over);
  - GEAR's year-by-year target path (1996-2000) is plotted as a dashed line;
  - a horizontal dotted reference line is added at GEAR's final (2000) target
    level, extended across the whole chart, per the brief's instruction to
    show "GEAR's target as a horizontal reference line where that makes sense";
  - a vertical grey line marks 2000/2001, the vintage splice point where the
    series switches from Nattrass/SARB-AER2001 data to the "Additional data"
    current-vintage series (trap #6 -- shown, not hidden).

Input : data/part2_extended_series_1996_2024.csv
Output: figures/part2_<indicator>.png (one file per indicator)
"""

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from pathlib import Path

# Paths resolve from this file's own location, so the project folder can be moved
# or copied anywhere (including onto a marker's machine) and still run.
PROJECT = Path(__file__).resolve().parents[2]   # .../Development project
RES = PROJECT / "resources"
BASE = PROJECT / "output"
DATA_CSV = BASE / "data" / "part2_extended_series_1996_2024.csv"
FIG_DIR = BASE / "figures"

TITLES = {
    "real_gdp_growth_pct": "Real GDP growth (%)",
    "real_private_investment_growth_pct": "Real private investment growth (%)",
    "nonagric_formal_employment_growth_pct": "Non-agric. formal employment growth (%)",
    "inflation_cpi_pct": "CPI inflation (%)",
    "deficit_pct_gdp": "Budget deficit (% of GDP)",
    "real_bank_rate_pct": "Real bank/repo rate (%)",
}


def plot_indicator(df: pd.DataFrame, indicator: str) -> None:
    sub = df[df["indicator"] == indicator].sort_values("year")

    fig, ax = plt.subplots(figsize=(8, 4.5))

    ax.plot(sub["year"], sub["actual"], color="#1a5276", marker="o", markersize=3,
             linewidth=1.8, label="Actual")
    target_sub = sub.dropna(subset=["gear_target"])
    ax.plot(target_sub["year"], target_sub["gear_target"], color="#c0392b",
             linestyle="--", marker="s", markersize=3, linewidth=1.5,
             label="GEAR target (1996\u20132000)")

    final_target = target_sub["gear_target"].iloc[-1] if not target_sub.empty else None
    if final_target is not None:
        ax.axhline(final_target, color="#c0392b", linestyle=":", linewidth=1,
                    alpha=0.6, label=f"GEAR 2000 target ({final_target:.1f}) held flat")

    ax.axvline(2000.5, color="grey", linestyle="-", linewidth=0.8, alpha=0.5)
    ax.text(2000.5, ax.get_ylim()[1], " vintage splice", fontsize=7, color="grey",
            va="top", ha="left", rotation=90)

    ax.set_title(TITLES.get(indicator, indicator))
    ax.set_xlabel("Year")
    ax.set_ylabel("%")
    ax.legend(fontsize=8, loc="best")
    ax.grid(alpha=0.3)
    fig.tight_layout()

    out_path = FIG_DIR / f"part2_{indicator}.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    df = pd.read_csv(DATA_CSV)
    for indicator in TITLES:
        plot_indicator(df, indicator)
