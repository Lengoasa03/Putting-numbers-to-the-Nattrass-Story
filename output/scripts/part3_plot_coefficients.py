"""
ECOH621 Part 3 -- figure: how the two contested coefficients move across
specifications. This is the visual version of the Part 3 argument: the
"signal" (deficit) coefficient is unstable and collapses once two recession
years are removed, while the "demand" (lagged GDP growth) coefficient
strengthens.

Output: figures/part3_coefficient_stability.png
"""

import pandas as pd
import statsmodels.formula.api as smf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from pathlib import Path

# Paths resolve from this file's own location, so the project folder can be moved
# or copied anywhere (including onto a marker's machine) and still run.
PROJECT = Path(__file__).resolve().parents[2]   # .../Development project
RES = PROJECT / "resources"
BASE = PROJECT / "output"
DATA = BASE / "data" / "part3_regression_data.csv"
FIG = BASE / "figures" / "part3_coefficient_stability.png"
FORMULA = "inv_growth ~ gdp_growth_lag1 + real_rate + deficit_gdp"

df = pd.read_csv(DATA)

SPECS = [
    ("Full sample\n1994-2024", df),
    ("Pre-2008\n1994-2007", df[df["year"] < 2008]),
    ("2008 onwards\n2008-2024", df[df["year"] >= 2008]),
    ("Full sample\nexcl. 2009 & 2020", df[~df["year"].isin([2009, 2020])]),
    ("2008 onwards\nexcl. 2009 & 2020", df[(df["year"] >= 2008) & (~df["year"].isin([2009, 2020]))]),
]

rows = []
for label, d in SPECS:
    s = d.dropna(subset=["inv_growth", "gdp_growth_lag1", "real_rate", "deficit_gdp"])
    r = smf.ols(FORMULA, data=s).fit(cov_type="HAC", cov_kwds={"maxlags": 1})
    for var in ["gdp_growth_lag1", "deficit_gdp"]:
        rows.append({
            "spec": label, "var": var,
            "coef": r.params[var], "se": r.bse[var], "p": r.pvalues[var],
        })
res = pd.DataFrame(rows)

fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), sharey=True)
titles = {
    "gdp_growth_lag1": "DEMAND channel\nlagged real GDP growth",
    "deficit_gdp": "SIGNAL channel\ndeficit (% of GDP)",
}
colors = {"gdp_growth_lag1": "#1a5276", "deficit_gdp": "#c0392b"}

for ax, var in zip(axes, ["gdp_growth_lag1", "deficit_gdp"]):
    sub = res[res["var"] == var].reset_index(drop=True)
    x = range(len(sub))
    ax.errorbar(x, sub["coef"], yerr=1.96 * sub["se"], fmt="o", capsize=5,
                color=colors[var], markersize=7, linewidth=1.6)
    ax.axhline(0, color="black", linewidth=1, linestyle="-")
    for i, r_ in sub.iterrows():
        star = "*" if r_["p"] < 0.05 else ""
        ax.annotate(f"{r_['coef']:.2f}{star}", (i, r_["coef"]),
                    textcoords="offset points", xytext=(9, 4), fontsize=8)
    ax.set_xticks(list(x))
    ax.set_xticklabels(sub["spec"], fontsize=7.5)
    ax.set_title(titles[var], fontsize=10)
    ax.grid(alpha=0.3, axis="y")

axes[0].set_ylabel("Coefficient (95% CI, HAC s.e.)")
fig.suptitle("Part 3: coefficient stability across specifications  (* = p < 0.05)",
             fontsize=11)
fig.tight_layout()
fig.savefig(FIG, dpi=150)
print(f"Saved: {FIG}")
