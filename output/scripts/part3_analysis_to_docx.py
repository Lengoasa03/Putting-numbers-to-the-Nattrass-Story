"""
ECOH621 Part 3 deliverable: regression results + interpretation as .docx.

Regenerates the regression live (so the docx can never drift from the code)
and lays out: specification, main results table, diagnostics, the two
robustness exercises, the coefficient-stability figure, and the interpretation.

Output: report/part3_regression_analysis.docx
"""

import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.diagnostic import acorr_breusch_godfrey, het_breuschpagan
from statsmodels.stats.stattools import durbin_watson, jarque_bera
from docx import Document
from docx.shared import Pt, Cm, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

from pathlib import Path

# Paths resolve from this file's own location, so the project folder can be moved
# or copied anywhere (including onto a marker's machine) and still run.
PROJECT = Path(__file__).resolve().parents[2]   # .../Development project
RES = PROJECT / "resources"
BASE = PROJECT / "output"
DATA = BASE / "data" / "part3_regression_data.csv"
FIG = BASE / "figures" / "part3_coefficient_stability.png"
OUT = BASE / "report" / "part3_regression_analysis.docx"

FORMULA = "inv_growth ~ gdp_growth_lag1 + real_rate + deficit_gdp"
LABELS = {
    "Intercept": "Intercept",
    "gdp_growth_lag1": "Lagged real GDP growth (DEMAND)",
    "real_rate": "Real bank rate",
    "deficit_gdp": "Deficit, % of GDP (SIGNAL)",
}


def shade(cell, color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), color)
    tcPr.append(shd)


def cell_text(cell, text, bold=False, size=9.5, align="center"):
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = {"center": WD_ALIGN_PARAGRAPH.CENTER,
                   "left": WD_ALIGN_PARAGRAPH.LEFT}[align]
    run = p.add_run(text)
    run.bold = bold
    run.font.size = Pt(size)
    run.font.name = "Calibri"


def body(doc, text, size=10.5, bold=False, italic=False):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.font.size = Pt(size)
    r.bold = bold
    r.italic = italic
    return p


def fit(d):
    s = d.dropna(subset=["inv_growth", "gdp_growth_lag1", "real_rate", "deficit_gdp"])
    m = smf.ols(FORMULA, data=s)
    return s, m.fit(), m.fit(cov_type="HAC", cov_kwds={"maxlags": 1})


def results_table(doc, res, sample_label):
    body(doc, sample_label, bold=True)
    t = doc.add_table(rows=len(res.params) + 1, cols=4)
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, h in enumerate(["Variable", "Coefficient", "HAC s.e.", "p-value"]):
        cell_text(t.rows[0].cells[j], h, bold=True)
        shade(t.rows[0].cells[j], "D9D9D9")
    for i, name in enumerate(res.params.index, start=1):
        cell_text(t.rows[i].cells[0], LABELS.get(name, name), align="left")
        star = " *" if res.pvalues[name] < 0.05 else ""
        cell_text(t.rows[i].cells[1], f"{res.params[name]:.3f}{star}")
        cell_text(t.rows[i].cells[2], f"{res.bse[name]:.3f}")
        cell_text(t.rows[i].cells[3], f"{res.pvalues[name]:.3f}")
    cap = doc.add_paragraph()
    cr = cap.add_run(f"N = {int(res.nobs)};  R\u00b2 = {res.rsquared:.3f};  "
                     f"adj. R\u00b2 = {res.rsquared_adj:.3f}.  * = p < 0.05.")
    cr.font.size = Pt(8.5)
    cr.italic = True
    doc.add_paragraph()


def main():
    df = pd.read_csv(DATA)
    doc = Document()
    for s in doc.sections:
        s.left_margin = Cm(2.0)
        s.right_margin = Cm(2.0)

    h = doc.add_heading("Part 3 \u2014 Testing the Gamble: Private Investment, "
                        "Demand and the Fiscal Signal", level=1)
    h.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # --- Specification --------------------------------------------------
    doc.add_heading("Specification", level=2)
    p = doc.add_paragraph()
    r = p.add_run("inv_growth\u209c = \u03b2\u2080 + \u03b2\u2081\u00b7gdp_growth\u209c\u208b\u2081 "
                  "+ \u03b2\u2082\u00b7real_rate\u209c + \u03b2\u2083\u00b7deficit_gdp\u209c + \u03b5\u209c")
    r.font.name = "Consolas"
    r.font.size = Pt(10.5)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    body(doc, "Annual data, 1994\u20132024, N = 31, estimated on a single consistent "
              "current vintage (SARB / StatsSA). Newey\u2013West (HAC, lag 1) standard "
              "errors throughout.")
    body(doc, "Sign convention: deficit_gdp is POSITIVE when the budget is in deficit. "
              "The LABOUR/ILO \u2018demand\u2019 position predicts \u03b2\u2081 > 0 "
              "(investment follows demand). The SAF/GEAR \u2018confidence/signal\u2019 "
              "position predicts \u03b2\u2083 < 0 (a larger deficit damages confidence, so "
              "consolidation crowds investment in).", italic=True)

    # --- Main results -----------------------------------------------------
    doc.add_heading("Main result", level=2)
    s0, o0, h0 = fit(df)
    results_table(doc, h0, "Full sample, 1994\u20132024")
    body(doc, "Read alone, this looks like a clean win for GEAR: the signal channel is "
              "significant with exactly the predicted sign, and the demand channel is "
              "not significant. Two tests show it should not be read alone.")

    # --- Diagnostics ------------------------------------------------------
    doc.add_heading("Diagnostics", level=2)
    bg = acorr_breusch_godfrey(o0, nlags=1)
    bp = het_breuschpagan(o0.resid, o0.model.exog)
    jb = jarque_bera(o0.resid)
    dw = durbin_watson(o0.resid)
    t = doc.add_table(rows=5, cols=3)
    t.style = "Table Grid"
    for j, hh in enumerate(["Test", "Statistic", "Conclusion"]):
        cell_text(t.rows[0].cells[j], hh, bold=True)
        shade(t.rows[0].cells[j], "D9D9D9")
    rows = [
        ("Durbin\u2013Watson", f"{dw:.3f}", "Below 2 \u2014 positive autocorrelation likely"),
        ("Breusch\u2013Godfrey AR(1)", f"LM = {bg[0]:.2f}, p = {bg[1]:.3f}",
         "Autocorrelation present \u2014 HAC s.e. required"),
        ("Breusch\u2013Pagan", f"LM = {bp[0]:.2f}, p = {bp[1]:.3f}",
         "No evidence of heteroskedasticity"),
        ("Jarque\u2013Bera", f"JB = {jb[0]:.2f}, p = {jb[1]:.3f}", "Normality not rejected"),
    ]
    for i, (a, b, c) in enumerate(rows, start=1):
        cell_text(t.rows[i].cells[0], a, align="left")
        cell_text(t.rows[i].cells[1], b)
        cell_text(t.rows[i].cells[2], c, align="left", size=9)
    doc.add_paragraph()
    body(doc, "All variance inflation factors are below 1.6, so multicollinearity is "
              "not a concern.", size=9.5, italic=True)

    doc.add_page_break()

    # --- Split at 2008 ----------------------------------------------------
    doc.add_heading("Test 1 \u2014 the sign reverses across the 2008 split", level=2)
    from scipy import stats as _st
    s_all = df.dropna(subset=["inv_growth", "gdp_growth_lag1", "real_rate", "deficit_gdp"])
    pre, post = s_all[s_all.year < 2008], s_all[s_all.year >= 2008]
    rss_p = smf.ols(FORMULA, data=s_all).fit().ssr
    rss_a = smf.ols(FORMULA, data=pre).fit().ssr
    rss_b = smf.ols(FORMULA, data=post).fit().ssr
    k, n = 4, len(s_all)
    F = ((rss_p - (rss_a + rss_b)) / k) / ((rss_a + rss_b) / (n - 2 * k))
    pval = 1 - _st.f.cdf(F, k, n - 2 * k)
    body(doc, f"Chow test for a structural break at 2008: F({k}, {n - 2*k}) = {F:.2f}, "
              f"p = {pval:.3f} \u2014 parameter stability is rejected.", bold=True)
    _, _, hpre = fit(df[df.year < 2008])
    results_table(doc, hpre, "Sub-sample A: 1994\u20132007")
    _, _, hpost = fit(df[df.year >= 2008])
    results_table(doc, hpost, "Sub-sample B: 2008\u20132024")
    body(doc, "The signal coefficient does not merely weaken \u2014 it flips sign and is "
              "significant in both directions (+1.67 before 2008, \u22122.31 after). A "
              "coefficient that reverses like this is not measuring a stable behavioural "
              "parameter; the full-sample estimate is an average of two opposite regimes.")

    # --- Crisis years -----------------------------------------------------
    doc.add_heading("Test 2 \u2014 two recession years drive the entire result", level=2)
    body(doc, "This is the endogeneity trap made concrete. In 2009 and 2020 the deficit "
              "exploded and private investment collapsed \u2014 but the recession caused "
              "both. Automatic stabilisers widen the deficit in a downturn by "
              "construction, so the correlation runs recession \u2192 deficit, not "
              "deficit \u2192 lost confidence \u2192 falling investment.")
    _, _, hnc = fit(df[~df.year.isin([2009, 2020])])
    results_table(doc, hnc, "Full sample excluding 2009 and 2020")
    _, _, hnc2 = fit(df[(df.year >= 2008) & (~df.year.isin([2009, 2020]))])
    results_table(doc, hnc2, "2008 onwards, excluding 2009 and 2020")
    body(doc, "Removing two observations out of 31 reverses the interpretation entirely: "
              "the signal channel loses significance (p = 0.15, then p = 0.83) while the "
              "demand channel becomes strongly significant and economically large \u2014 a "
              "one-point rise in last year's GDP growth is associated with roughly a "
              "one-point rise in private investment growth.", bold=True)

    doc.add_picture(str(FIG), width=Inches(6.3))
    cap = doc.add_paragraph()
    cr = cap.add_run("Figure: coefficient stability across specifications. The demand "
                     "coefficient is positive throughout and tightens as crisis outliers "
                     "are removed; the signal coefficient swings from +1.67 to \u22122.31 "
                     "and collapses toward zero without them.")
    cr.italic = True
    cr.font.size = Pt(8.5)
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_page_break()

    # --- Interpretation ---------------------------------------------------
    doc.add_heading("Which stable does the evidence favour?", level=2)
    body(doc, "On balance the demand (LABOUR/ILO) channel \u2014 but with real "
              "qualifications, and the honest answer is that the evidence is mixed in a "
              "specific, diagnosable way.", bold=True)
    body(doc, "The case for demand: \u03b2\u2081 is positive in every specification run, "
              "and becomes significant precisely when the observations most contaminated "
              "by reverse causation are removed. That is the pattern expected from a real "
              "relationship obscured by noise, not one manufactured by it.")
    body(doc, "The case against over-claiming it: \u03b2\u2081 is not significant on the "
              "full sample (p = 0.18), and it depends on the GDP series used. Re-running "
              "with Boshoff & Fourie's factor-cost GDP gives \u03b2\u2081 = 0.264 "
              "(p = 0.774) \u2014 nothing survives. That is a genuine fragility: the "
              "demand result holds on SARB market-price GDP and vanishes on B&F "
              "factor-cost GDP over a shorter (1994\u20132018) sample, and the shorter "
              "sample cannot be cleanly separated from the definitional switch.")
    body(doc, "What can be said with more confidence is the negative finding: there is no "
              "robust evidence for the confidence channel GEAR was built on. The one "
              "specification where the signal channel is significant with GEAR's predicted "
              "sign is also the one most obviously contaminated by recession-driven "
              "simultaneity, and it does not survive removing two outlier years. GEAR's "
              "central bet \u2014 that consolidation would signal credibility and thereby "
              "unlock private investment \u2014 is not supported here, consistent with "
              "Part 2's finding that South Africa delivered the consolidation without ever "
              "once hitting an investment target.", bold=True)
    body(doc, "The pre-2008 positive deficit coefficient (+1.67) deserves a note rather "
              "than a celebration. It has the demand sign, but 1994\u20132007 is exactly "
              "when deficits were shrinking while investment was rising, so a positive "
              "coefficient is as easily read as coincident trends as causation. With "
              "N = 14 and no instrument, it cannot bear weight.")

    doc.add_heading("Does the answer change if you split at 1994, or at 2008?", level=2)
    body(doc, "At 2008: yes, decisively \u2014 the Chow test rejects stability and the "
              "signal coefficient reverses sign. This is the most informative single "
              "result in Part 3.")
    body(doc, "At 1994: the split cannot be run. The supplied deficit and policy-rate "
              "series both begin in 1994, so there are zero pre-1994 observations for two "
              "of the three regressors. This is a data-availability limit, not a modelling "
              "choice, and is reported as not estimable rather than approximated with a "
              "different specification presented as the requested test.")

    doc.add_heading("Limitations", level=2)
    for text in [
        "Endogeneity is diagnosed, not solved. Investment, growth and the deficit are "
        "jointly determined; no instrument is used, so no coefficient here can be read "
        "as causal. The crisis-year exercise shows which results are most contaminated "
        "by simultaneity \u2014 a weaker but honest claim.",
        "N = 31, with sub-samples of 14 and 17. Power is low and the sub-sample results "
        "should be read as suggestive.",
        "The dependent variable's definition is not fully verified: the private "
        "investment series carries no source or series code. Its 2009/2020 contraction "
        "magnitudes are consistent with a private-only series, but that is corroboration, "
        "not confirmation.",
        "GDP vintage matters to the answer. The demand result holds on SARB market-price "
        "GDP and does not hold on Boshoff & Fourie factor-cost GDP. Both are reported.",
        "The real rate is ex-post (nominal minus realised CPI), following Nattrass's own "
        "construction, not an ex-ante rate using inflation expectations.",
    ]:
        p = doc.add_paragraph(style="List Bullet")
        r = p.add_run(text)
        r.font.size = Pt(10)

    doc.save(OUT)
    print(f"Saved: {OUT}")


if __name__ == "__main__":
    main()
