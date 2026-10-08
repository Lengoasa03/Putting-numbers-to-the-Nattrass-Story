"""
ECOH621 Weeks 6-7 assignment -- Part 3: estimate the investment model.

MODEL
  inv_growth_t = b0 + b1*gdp_growth_{t-1} + b2*real_rate_t + b3*deficit_gdp_t + e_t

WHAT EACH COEFFICIENT TESTS (this is the whole point of Part 3):
  b1 (lagged GDP growth)  -- the LABOUR/ILO "demand" channel. Their position
                             implies b1 > 0 and economically large: investment
                             follows demand.
  b3 (deficit, % of GDP)  -- the SAF/GEAR "confidence/signal" channel. GEAR's
                             position implies b3 < 0: a larger deficit damages
                             investor confidence and depresses private
                             investment, so fiscal consolidation should crowd
                             investment IN.
  b2 (real interest rate) -- the conventional cost-of-capital channel, expected
                             b2 < 0. Not the contested one, but included because
                             omitting it would bias the other two.

SIGN CONVENTION: deficit_gdp is POSITIVE when in deficit (see the data-build
script). Keep this in mind reading b3.

INFERENCE: annual macro time series, N ~ 31. Reported with Newey-West (HAC)
standard errors (lag 1, ~ N^(1/4)) because residual autocorrelation and
heteroskedasticity are both live risks here and OLS standard errors would
overstate precision. Classical OLS SEs are printed alongside for comparison.

Outputs: report/part3_results.txt (full numeric record) and console summary.
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.diagnostic import acorr_breusch_godfrey, het_breuschpagan
from statsmodels.stats.stattools import durbin_watson, jarque_bera
from statsmodels.stats.outliers_influence import variance_inflation_factor

from pathlib import Path

# Paths resolve from this file's own location, so the project folder can be moved
# or copied anywhere (including onto a marker's machine) and still run.
PROJECT = Path(__file__).resolve().parents[2]   # .../Development project
RES = PROJECT / "resources"
BASE = PROJECT / "output"
DATA = BASE / "data" / "part3_regression_data.csv"
OUT_TXT = BASE / "report" / "part3_results.txt"

FORMULA = "inv_growth ~ gdp_growth_lag1 + real_rate + deficit_gdp"
HAC_LAGS = 1

lines = []


def emit(text=""):
    print(text)
    lines.append(str(text))


def fit(df, formula=FORMULA, label=""):
    """OLS with HAC (Newey-West) covariance."""
    sub = df.dropna(subset=["inv_growth", "gdp_growth_lag1", "real_rate", "deficit_gdp"])
    model = smf.ols(formula, data=sub)
    res_ols = model.fit()
    res_hac = model.fit(cov_type="HAC", cov_kwds={"maxlags": HAC_LAGS})
    return sub, res_ols, res_hac


def report(sub, res_ols, res_hac, label):
    emit("=" * 78)
    emit(label)
    emit("=" * 78)
    emit(f"Sample: {int(sub['year'].min())}-{int(sub['year'].max())}   N = {int(res_hac.nobs)}")
    emit(f"R-squared: {res_hac.rsquared:.4f}   Adj R-squared: {res_hac.rsquared_adj:.4f}")
    emit("")
    emit(f"{'variable':<20}{'coef':>10}{'HAC s.e.':>11}{'t':>8}{'p':>9}{'OLS s.e.':>11}")
    emit("-" * 69)
    for name in res_hac.params.index:
        emit(f"{name:<20}{res_hac.params[name]:>10.4f}{res_hac.bse[name]:>11.4f}"
             f"{res_hac.tvalues[name]:>8.2f}{res_hac.pvalues[name]:>9.4f}"
             f"{res_ols.bse[name]:>11.4f}")
    emit("")
    return res_hac


def diagnostics(res_ols, sub):
    emit("-" * 78)
    emit("DIAGNOSTICS (on the OLS fit)")
    emit("-" * 78)

    dw = durbin_watson(res_ols.resid)
    emit(f"Durbin-Watson                : {dw:.3f}   (2 = no first-order autocorrelation)")

    try:
        bg = acorr_breusch_godfrey(res_ols, nlags=1)
        emit(f"Breusch-Godfrey AR(1)        : LM = {bg[0]:.3f}, p = {bg[1]:.4f}"
             f"   {'-> autocorrelation' if bg[1] < 0.05 else '-> no evidence of autocorrelation'}")
    except Exception as e:
        emit(f"Breusch-Godfrey failed: {e}")

    bp = het_breuschpagan(res_ols.resid, res_ols.model.exog)
    emit(f"Breusch-Pagan heteroskedast. : LM = {bp[0]:.3f}, p = {bp[1]:.4f}"
         f"   {'-> heteroskedastic' if bp[1] < 0.05 else '-> no evidence of heteroskedasticity'}")

    jb = jarque_bera(res_ols.resid)
    emit(f"Jarque-Bera normality        : JB = {jb[0]:.3f}, p = {jb[1]:.4f}"
         f"   {'-> non-normal residuals' if jb[1] < 0.05 else '-> normality not rejected'}")

    emit("")
    emit("Variance inflation factors (multicollinearity; >10 is a concern):")
    X = sub[["gdp_growth_lag1", "real_rate", "deficit_gdp"]].copy()
    X.insert(0, "const", 1.0)
    for i, name in enumerate(X.columns):
        if name == "const":
            continue
        emit(f"   {name:<20}: {variance_inflation_factor(X.values, i):.2f}")
    emit("")


def chow_test(df, break_year):
    """Chow test for a structural break at `break_year` (break_year starts the 2nd regime)."""
    sub = df.dropna(subset=["inv_growth", "gdp_growth_lag1", "real_rate", "deficit_gdp"])
    pre = sub[sub["year"] < break_year]
    post = sub[sub["year"] >= break_year]
    k = 4  # params incl. intercept
    if len(pre) <= k or len(post) <= k:
        return None, len(pre), len(post)

    rss_pooled = smf.ols(FORMULA, data=sub).fit().ssr
    rss_pre = smf.ols(FORMULA, data=pre).fit().ssr
    rss_post = smf.ols(FORMULA, data=post).fit().ssr
    n = len(sub)
    num = (rss_pooled - (rss_pre + rss_post)) / k
    den = (rss_pre + rss_post) / (n - 2 * k)
    F = num / den
    from scipy import stats
    p = 1 - stats.f.cdf(F, k, n - 2 * k)
    return (F, p), len(pre), len(post)


if __name__ == "__main__":
    df = pd.read_csv(DATA)

    emit("ECOH621 Part 3 -- Real private investment growth: regression results")
    emit(f"Model: {FORMULA}")
    emit(f"HAC (Newey-West) standard errors, maxlags = {HAC_LAGS}")
    emit("deficit_gdp is POSITIVE when the budget is in deficit.")
    emit("")

    # ---------------- Main specification --------------------------------
    sub, res_ols, res_hac = fit(df)
    report(sub, res_ols, res_hac, "MAIN SPECIFICATION -- full available sample, single current vintage")
    diagnostics(res_ols, sub)

    # ---------------- Sample splits -------------------------------------
    emit("=" * 78)
    emit("SAMPLE SPLITS")
    emit("=" * 78)

    emit("")
    emit("Split at 1994 (requested in the brief):")
    result, n_pre, n_post = chow_test(df, 1994)
    emit(f"   Observations before 1994: {n_pre}; from 1994: {n_post}")
    emit("   NOT ESTIMABLE. The supplied deficit and policy-rate series both begin in")
    emit("   1994, so there are zero pre-1994 observations for two of the three")
    emit("   regressors. A pre/post-1994 split cannot be run on this data at all -- this")
    emit("   is a data-availability limit, not a modelling choice, and is reported as")
    emit("   such rather than approximated with a shorter or different specification.")
    emit("")

    emit("Split at 2008 (requested in the brief):")
    result, n_pre, n_post = chow_test(df, 2008)
    if result:
        F, p = result
        emit(f"   Chow F({4}, {len(sub) - 8}) = {F:.3f}, p = {p:.4f}"
             f"   {'-> structural break' if p < 0.05 else '-> no significant structural break'}")
    emit(f"   N before 2008 = {n_pre}, N from 2008 = {n_post}")
    emit("")

    pre = df[df["year"] < 2008]
    post = df[df["year"] >= 2008]
    s1, o1, h1 = fit(pre)
    report(s1, o1, h1, "SUB-SAMPLE A -- pre-2008")
    s2, o2, h2 = fit(post)
    report(s2, o2, h2, "SUB-SAMPLE B -- 2008 onwards")

    # ---------------- Sensitivity: Boshoff & Fourie GDP (trap #4) --------
    emit("=" * 78)
    emit("SENSITIVITY (trap #4 / trap #6): lagged GDP growth from Boshoff & Fourie's")
    emit("spliced factor-cost series instead of SARB market prices.")
    emit("This tests whether the demand-channel result depends on the GDP vintage and")
    emit("on B&F's choice to link their 1911-68 series to SARB's by the 1946-59 mean")
    emit("difference. B&F ends in 2017, so this sample is shorter.")
    emit("=" * 78)
    alt_formula = "inv_growth ~ gdp_growth_bf_lag1 + real_rate + deficit_gdp"
    sub_alt = df.dropna(subset=["inv_growth", "gdp_growth_bf_lag1", "real_rate", "deficit_gdp"])
    m_alt = smf.ols(alt_formula, data=sub_alt)
    r_alt_ols = m_alt.fit()
    r_alt = m_alt.fit(cov_type="HAC", cov_kwds={"maxlags": HAC_LAGS})
    report(sub_alt, r_alt_ols, r_alt, "SENSITIVITY -- Boshoff & Fourie GDP vintage")

    # ---------------- Robustness: crisis years (trap #7, endogeneity) ----
    emit("=" * 78)
    emit("ROBUSTNESS -- dropping 2009 and 2020 (the GFC and COVID recessions)")
    emit("=" * 78)
    emit("MOTIVATION (trap #7). In 2009 and 2020 the deficit exploded AND private")
    emit("investment collapsed -- but both were caused by the recession, not by each")
    emit("other. Automatic stabilisers widen the deficit in a downturn by construction.")
    emit("So a negative deficit coefficient in a sample containing those years may be")
    emit("measuring reverse causation (recession -> deficit) rather than the")
    emit("confidence channel GEAR posited (deficit -> lost confidence -> investment).")
    emit("These two years are 2 of 31 observations but are by far the largest outliers")
    emit("in both variables. Dropping them is a diagnostic, not a preferred estimate.")
    emit("")
    no_crisis = df[~df["year"].isin([2009, 2020])]
    s3, o3, h3 = fit(no_crisis)
    report(s3, o3, h3, "ROBUSTNESS -- full sample excluding 2009 and 2020")

    post_nc = df[(df["year"] >= 2008) & (~df["year"].isin([2009, 2020]))]
    s4, o4, h4 = fit(post_nc)
    report(s4, o4, h4, "ROBUSTNESS -- 2008 onwards, excluding 2009 and 2020")

    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\nFull results written to: {OUT_TXT}")
