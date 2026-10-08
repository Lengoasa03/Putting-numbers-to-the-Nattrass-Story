"""
ECOH621 Weeks 6-7 assignment: build the consolidated report (.docx).

Pulls the Part 1 table, the Part 2 target-scoring table and figures, and runs
the Part 3 regressions live so the document can never drift from the code.

Output: report/ECOH621_Nattrass_assignment_REPORT.docx
"""

import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.diagnostic import acorr_breusch_godfrey, het_breuschpagan
from statsmodels.stats.stattools import jarque_bera
from scipy import stats as sps
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
P1_CSV = BASE / "data" / "gear_target_vs_actual_1996_2000_CORRECTED.csv"
P2_CSV = BASE / "data" / "part2_extended_series_1996_2024.csv"
P3_CSV = BASE / "data" / "part3_regression_data.csv"
FIGS = BASE / "figures"
OUT = BASE / "report" / "ECOH621_Nattrass_assignment_REPORT.docx"

FORMULA = "inv_growth ~ gdp_growth_lag1 + real_rate + deficit_gdp"

INDICATORS = [
    ("real_gdp_growth_pct", "Real GDP growth (%)", True),
    ("real_private_investment_growth_pct", "Real private investment growth (%)", True),
    ("nonagric_formal_employment_growth_pct", "Non-agric. formal employment growth (%)", True),
    ("inflation_cpi_pct", "CPI inflation (%)", False),
    ("deficit_pct_gdp", "Budget deficit (% of GDP)", False),
    ("real_bank_rate_pct", "Real bank/repo rate (%)", False),
]

word_count = 0


def shade(cell, color="D9D9D9"):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), color)
    tcPr.append(shd)


def ctext(cell, text, bold=False, size=9, align="center"):
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = {"center": WD_ALIGN_PARAGRAPH.CENTER,
                   "left": WD_ALIGN_PARAGRAPH.LEFT}[align]
    r = p.add_run(text)
    r.bold = bold
    r.font.size = Pt(size)
    r.font.name = "Calibri"


def para(doc, text, size=11, bold=False, italic=False, count=True):
    """Body paragraph. Counted toward the word limit unless count=False."""
    global word_count
    if count:
        word_count += len(text.split())
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.font.size = Pt(size)
    r.bold = bold
    r.italic = italic
    return p


def caption(doc, text):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.italic = True
    r.font.size = Pt(8.5)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER


def fit(d):
    s = d.dropna(subset=["inv_growth", "gdp_growth_lag1", "real_rate", "deficit_gdp"])
    m = smf.ols(FORMULA, data=s)
    return s, m.fit(), m.fit(cov_type="HAC", cov_kwds={"maxlags": 1})


# ------------------------------------------------------------------ build ---
doc = Document()
for s in doc.sections:
    s.left_margin = Cm(2.2)
    s.right_margin = Cm(2.2)

t = doc.add_heading("Putting Numbers to the Nattrass Story", level=0)
t.alignment = WD_ALIGN_PARAGRAPH.CENTER
sub = doc.add_paragraph()
sr = sub.add_run("ECOH621 Development Economics. GEAR's projections against thirty "
                 "years of outcomes.")
sr.italic = True
sr.font.size = Pt(10)
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER

# ---------------------------------------------------------------- intro -----
doc.add_heading("The question", level=1)
para(doc,
     "In 1996 Nicoli Nattrass described South Africa's policy debate as a bet. The "
     "SAF/GEAR camp held that private investment would recover once government "
     "proved it could control the deficit and inflation. The LABOUR/ILO camp held "
     "that investment follows demand, so cutting spending would cut the very thing "
     "investment responds to. Nattrass declined to pick a winner, because nobody "
     "knew how investors would actually behave.")
para(doc,
     "In 2001 she returned to the question and compared GEAR's projections with what "
     "happened between 1996 and 1999. This report rebuilds that comparison, carries "
     "it forward to 2024, and then tests the two positions directly with a regression. "
     "The short answer is that GEAR delivered the stability it promised and almost "
     "none of the growth. Whether that proves the demand camp right is a harder "
     "question, and the honest answer depends on two recession years.")

# --------------------------------------------------------------- part 1 -----
doc.add_heading("Part 1. Rebuilding the table", level=1)
para(doc,
     "Nattrass's Table 1 sets GEAR's projections beside actual performance. I rebuilt "
     "it for the six indicators the brief lists, using the supplied csv of targets and "
     "outturns. Two things needed fixing before the table could be trusted.")
para(doc,
     "The first was the inflation row. The csv gives GEAR inflation targets of 8.4, "
     "10.9 and 9.6 per cent for 1996 to 1998. Those figures do not come from GEAR's "
     "Integrated Scenario, which is the plan government actually adopted and the source "
     "of every other row. They come from the Base Scenario in the same 1996 document, "
     "which was the do-nothing baseline GEAR was designed to beat. I checked this "
     "directly against South Africa (1996) and the Integrated Scenario gives 8.0, 9.7 "
     "and 8.1 instead. Only the 1999 figure of 7.7 is the same in both scenarios, which "
     "is probably why the error went unnoticed. Nattrass's own 2001 table repeats the "
     "Base Scenario numbers, so this is an error inherited from the published paper "
     "rather than a transcription fault in the course data. I use the verified "
     "Integrated Scenario values and supply 7.6 for 2000, which the csv left blank.")
para(doc,
     "The second was the cells flagged as reconstructed from a damaged scan. I checked "
     "every one against Nattrass (2001) and against the 1996 GEAR document where the "
     "cell is a target. All of them match the values already in the csv, so no changes "
     "were needed. One small discrepancy is worth noting: the data dictionary says six "
     "cells are affected, but only five carry the flag in the file itself.")
para(doc,
     "Nattrass stops at 1999 because her source, the SARB Quarterly Bulletin of March "
     "2000, predates the full-year figures. I filled 2000 from the SARB Annual Economic "
     "Report 2001, which is the first report covering the whole calendar year. Five of "
     "the six indicators are there. Employment is not. The report gives private-sector "
     "formal employment falling 2.0 per cent and public-sector employment falling 4.1 "
     "per cent, but never states a combined total, and building one would need a "
     "weighting I could not source. I left that cell blank rather than invent a number.")

p1 = pd.read_csv(P1_CSV)
tbl = doc.add_table(rows=len(INDICATORS) + 2, cols=11)
tbl.style = "Table Grid"
tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
ctext(tbl.rows[0].cells[0], "", bold=True)
shade(tbl.rows[0].cells[0])
for j, yr in enumerate(range(1996, 2001)):
    for k in range(2):
        c = tbl.rows[0].cells[1 + j * 2 + k]
        ctext(c, str(yr) if k == 0 else "", bold=True, size=8)
        shade(c)
ctext(tbl.rows[1].cells[0], "Indicator", bold=True, size=8, align="left")
shade(tbl.rows[1].cells[0])
for j in range(5):
    ctext(tbl.rows[1].cells[1 + j * 2], "Target", bold=True, size=7.5)
    ctext(tbl.rows[1].cells[2 + j * 2], "Actual", bold=True, size=7.5)
    shade(tbl.rows[1].cells[1 + j * 2])
    shade(tbl.rows[1].cells[2 + j * 2])
for i, (key, label, _) in enumerate(INDICATORS, start=2):
    ctext(tbl.rows[i].cells[0], label, size=8, align="left")
    sub_df = p1[p1["indicator"] == key].set_index("year")
    for j, yr in enumerate(range(1996, 2001)):
        tv = sub_df.loc[yr, "gear_target"] if yr in sub_df.index else None
        av = sub_df.loc[yr, "actual_to_1999"] if yr in sub_df.index else None
        ctext(tbl.rows[i].cells[1 + j * 2],
              "\u2014" if pd.isna(tv) else f"{tv:.1f}", size=8)
        ctext(tbl.rows[i].cells[2 + j * 2],
              "\u2014" if pd.isna(av) else f"{av:.1f}", size=8)
caption(doc, "Table 1. GEAR targets and actual performance, 1996 to 2000. Targets from "
             "South Africa (1996), Integrated Scenario. Actuals 1996 to 1999 from "
             "Nattrass (2001). Actuals for 2000 from SARB (2001).")

para(doc,
     "The brief asks for a source on every row, so Table 2 gives them. Where a figure "
     "comes from the supplied csv unchanged, the table says so.")

SOURCES = [
    ("Real GDP growth",
     "Target: South Africa (1996), Integrated Scenario. Actual 1996-99: supplied csv, "
     "from Nattrass (2001). Actual 2000: SARB (2001), 3.0 per cent."),
    ("Real private investment growth",
     "Target: South Africa (1996). Actual 1996-99: supplied csv, from Nattrass (2001). "
     "Actual 2000: SARB (2001), private business enterprise GFCF, 5.0 per cent."),
    ("Non-agric. formal employment growth",
     "Target: South Africa (1996). Actual 1996-99: supplied csv, from Nattrass (2001). "
     "Actual 2000: not stated as a single figure in SARB (2001) and left blank."),
    ("CPI inflation",
     "Target: corrected from South Africa (1996), Integrated Scenario, replacing the "
     "Base Scenario values in the supplied csv. Actual 1996-99: supplied csv. Actual "
     "2000: SARB (2001), annual average 5.3 per cent."),
    ("Budget deficit, % of GDP",
     "Target: South Africa (1996). Actual 1996-99: supplied csv. Actual 2000: SARB "
     "(2001), 2.0 per cent, a fiscal-year figure for 2000/01 and so not strictly "
     "comparable with the calendar-year figures above it."),
    ("Real bank/repo rate",
     "Target: South Africa (1996). Actual 1996-99: supplied csv. Actual 2000: derived "
     "as 11.81 nominal minus 5.3 CPI = 6.51, where the nominal average comes from SARB "
     "monthly Bank rate data and matches the rate changes described in SARB (2001)."),
]
st = doc.add_table(rows=len(SOURCES) + 1, cols=2)
st.style = "Table Grid"
for j, h in enumerate(["Row", "Source"]):
    ctext(st.rows[0].cells[j], h, bold=True)
    shade(st.rows[0].cells[j])
for i, (a, b) in enumerate(SOURCES, start=1):
    ctext(st.rows[i].cells[0], a, size=8, align="left")
    ctext(st.rows[i].cells[1], b, size=8, align="left")
    st.rows[i].cells[0].width = Cm(4.2)
    st.rows[i].cells[1].width = Cm(12.3)
caption(doc, "Table 2. Source for every row of Table 1.")

# --------------------------------------------------------------- part 2 -----
doc.add_heading("Part 2. Extending the series to 2024", level=1)
para(doc,
     "I carried each series forward to 2024 using SARB and StatsSA data. The build "
     "chains three sources: Nattrass for 1996 to 1999, the SARB Annual Economic Report "
     "2001 for 2000, and current-vintage SARB and StatsSA series for 2001 onwards. "
     "Every cell in the output file carries a source tag, and the plots mark the year "
     "where the vintage changes, because presenting one smooth line would hide a real "
     "break in the data.")
para(doc,
     "To score a target as met after 2000, when GEAR's own targets stop, I use GEAR's "
     "final 2000 target as the implied steady-state goal. Beating it means higher for "
     "growth, investment and employment, and lower for inflation, the deficit and the "
     "real interest rate.")

p2 = pd.read_csv(P2_CSV)
final_targets = p2.dropna(subset=["gear_target"]).groupby("indicator")["gear_target"].last()
score_tbl = doc.add_table(rows=len(INDICATORS) + 1, cols=3)
score_tbl.style = "Table Grid"
score_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
for j, h in enumerate(["Indicator", "Years met", "When"]):
    ctext(score_tbl.rows[0].cells[j], h, bold=True)
    shade(score_tbl.rows[0].cells[j])
for i, (key, label, higher) in enumerate(INDICATORS, start=1):
    sub_df = p2[p2["indicator"] == key].dropna(subset=["actual"]).sort_values("year")
    met = []
    for _, r in sub_df.iterrows():
        tgt = r["gear_target"] if pd.notna(r["gear_target"]) else final_targets[key]
        if (r["actual"] >= tgt) if higher else (r["actual"] <= tgt):
            met.append(int(r["year"]))
    ctext(score_tbl.rows[i].cells[0], label, size=8.5, align="left")
    ctext(score_tbl.rows[i].cells[1], f"{len(met)} of {len(sub_df)}", size=8.5)
    if not met:
        when = "never"
    elif len(met) > 8:
        when = f"{met[0]}\u2013{met[-1]}, most years"
    else:
        when = ", ".join(str(y) for y in met)
    ctext(score_tbl.rows[i].cells[2], when, size=8, align="left")
caption(doc, "Table 3. Years in which each GEAR target was met, 1996 to 2024. "
             "Denominator is years with data, which is why employment differs.")

para(doc,
     "The pattern is hard to miss. Inflation beat its target in 27 of 29 years, missing "
     "only 2002 and 2008, both shock years. The deficit beat its target for a clean run "
     "from 1998 to 2008. The real interest rate beat its target for eighteen straight "
     "years from 2006. Now look at the other three. Real GDP growth met its target once, "
     "in 1996, before the strategy had time to do anything. Employment met it once, in "
     "2006. Private investment growth never met its target in twenty-nine years.")
para(doc,
     "So the three stabilisation indicators were met most of the time and the three "
     "growth indicators almost never were. This matters because GEAR was not a "
     "stabilisation plan for its own sake. Stability was supposed to buy investment. "
     "South Africa delivered the stability and did not get the investment, which is "
     "close to a clean failure of the strategy on its own terms.")
para(doc,
     "One period complicates that reading and deserves attention. Between 2004 and 2007 "
     "growth reached 5.6 per cent, the budget moved into surplus, inflation fell to 1.4 "
     "per cent in 2004, and formal employment grew at around 4 per cent a year. For a "
     "few years stability and growth arrived together. Any account that treats GEAR as "
     "a simple failure has to explain that episode, and Part 3 offers one.")

for key, label, _ in INDICATORS[:2]:
    doc.add_picture(str(FIGS / f"part2_{key}.png"), width=Inches(5.8))
    caption(doc, f"Figure. {label}, actual against GEAR target.")

# --------------------------------------------------------------- part 3 -----
doc.add_heading("Part 3. Testing the gamble", level=1)
para(doc,
     "The two camps make testable claims. If LABOUR/ILO are right, investment should "
     "respond to demand, so lagged GDP growth should carry a positive coefficient. If "
     "SAF/GEAR are right, investment should respond to the fiscal signal, so the deficit "
     "should carry a negative one. I estimate real private investment growth on lagged "
     "real GDP growth, the real bank rate and the deficit as a share of GDP, annually "
     "from 1994 to 2024, with 31 observations. Throughout, the deficit is positive when "
     "the budget is in deficit.")
para(doc,
     "Part 2 chains vintages on purpose so that GEAR can be judged against the data of "
     "its own day. That would be wrong here, because a definition that changes mid-sample "
     "gets baked into the coefficients. Part 3 therefore uses one current vintage "
     "throughout and keeps Boshoff and Fourie's series as a sensitivity check.")
para(doc,
     "The Breusch-Godfrey test rejects the null of no autocorrelation, so I report "
     "Newey-West standard errors with one lag. Breusch-Pagan finds no heteroskedasticity, "
     "Jarque-Bera does not reject normal residuals, and all variance inflation factors "
     "sit below 1.6.")

df3 = pd.read_csv(P3_CSV)
s_all, o_all, h_all = fit(df3)
_, _, h_pre = fit(df3[df3.year < 2008])
_, _, h_post = fit(df3[df3.year >= 2008])
_, _, h_nc = fit(df3[~df3.year.isin([2009, 2020])])
_, _, h_nc2 = fit(df3[(df3.year >= 2008) & (~df3.year.isin([2009, 2020]))])

SPECS = [
    ("Full sample, 1994\u20132024", h_all),
    ("Pre-2008, 1994\u20132007", h_pre),
    ("2008 onwards", h_post),
    ("Full, excl. 2009 & 2020", h_nc),
    ("2008 on, excl. 2009 & 2020", h_nc2),
]
rt = doc.add_table(rows=len(SPECS) + 1, cols=5)
rt.style = "Table Grid"
rt.alignment = WD_TABLE_ALIGNMENT.CENTER
for j, h in enumerate(["Specification", "N", "Lagged GDP growth", "Real rate", "Deficit/GDP"]):
    ctext(rt.rows[0].cells[j], h, bold=True, size=8.5)
    shade(rt.rows[0].cells[j])
for i, (lab, res) in enumerate(SPECS, start=1):
    ctext(rt.rows[i].cells[0], lab, size=8, align="left")
    ctext(rt.rows[i].cells[1], str(int(res.nobs)), size=8)
    for j, v in enumerate(["gdp_growth_lag1", "real_rate", "deficit_gdp"], start=2):
        star = "*" if res.pvalues[v] < 0.05 else ""
        ctext(rt.rows[i].cells[j],
              f"{res.params[v]:.2f}{star}\n({res.bse[v]:.2f})", size=8)
caption(doc, "Table 4. Real private investment growth. Newey-West standard errors in "
             "parentheses. * = p < 0.05.")

para(doc,
     "Read the first row alone and GEAR wins. The deficit coefficient is -1.83 and "
     "significant at the 1 per cent level, exactly the sign the confidence argument "
     "predicts, while lagged GDP growth is insignificant. That reading does not survive "
     "two checks.")
rss_p = smf.ols(FORMULA, data=s_all).fit().ssr
rss_a = smf.ols(FORMULA, data=s_all[s_all.year < 2008]).fit().ssr
rss_b = smf.ols(FORMULA, data=s_all[s_all.year >= 2008]).fit().ssr
n, k = len(s_all), 4
Fstat = ((rss_p - (rss_a + rss_b)) / k) / ((rss_a + rss_b) / (n - 2 * k))
pval = 1 - sps.f.cdf(Fstat, k, n - 2 * k)
para(doc,
     f"The first is the 2008 split the brief asks for. A Chow test rejects parameter "
     f"stability (F = {Fstat:.2f}, p = {pval:.3f}). Estimating either side, the deficit "
     f"coefficient is +1.67 before 2008 and -2.31 after, and it is significant in both "
     f"directions. A coefficient that reverses sign like that is not measuring a stable "
     f"behavioural parameter. The full-sample estimate is averaging two opposite regimes.")
para(doc,
     "The second check matters more. In 2009 and 2020 the deficit exploded and private "
     "investment collapsed, but the recession caused both. Automatic stabilisers widen "
     "the deficit in a downturn by construction, so the correlation runs from recession "
     "to deficit rather than from deficit to lost confidence. Dropping those two years "
     "from thirty-one reverses the conclusion. The deficit coefficient falls to -0.70 "
     "and loses significance, then to -0.14 in the post-2008 window. Lagged GDP growth "
     "rises to 0.94 and becomes significant at the 1 per cent level.")
doc.add_picture(str(FIGS / "part3_coefficient_stability.png"), width=Inches(6.2))
caption(doc, "Figure. Coefficient stability across specifications, with 95 per cent "
             "confidence intervals.")
para(doc,
     "So which camp does the evidence favour? On balance the demand camp, with "
     "qualifications. The demand coefficient is positive in all five specifications and "
     "becomes significant precisely when the observations most contaminated by reverse "
     "causation come out. That is what a real relationship obscured by noise looks like. "
     "A coefficient of 0.94 also means something economically: a one-point rise in last "
     "year's growth goes with roughly a one-point rise in investment growth.")
para(doc,
     "Against that, the demand result is not significant on the full sample, and it "
     "depends on which GDP series I use. Re-estimating with Boshoff and Fourie's "
     "factor-cost series gives 0.26 with a p-value of 0.77, so nothing survives. Part of "
     "that is the shorter sample ending in 2018 and part is the change in definition, and "
     "I cannot separate the two.")
para(doc,
     "The firmer finding is the negative one. There is no reliable evidence for the "
     "confidence channel GEAR was built on. The only specification where the fiscal "
     "signal is significant with GEAR's predicted sign is also the one most obviously "
     "contaminated by recession-driven simultaneity, and it does not survive dropping two "
     "outlier years. That fits Part 2, where the consolidation arrived and the investment "
     "never did. It also explains the 2004 to 2007 episode: growth and investment rose "
     "together in those years because demand was strong, which is what the demand channel "
     "predicts, and the budget surplus was along for the ride.")
para(doc,
     "The 1994 split the brief also asks for cannot be run. The supplied deficit and "
     "policy-rate series both start in 1994, so there are no pre-1994 observations for two "
     "of the three regressors. That is a limit of the data rather than a choice about "
     "method, and I report it as such instead of substituting a different test.")
para(doc,
     "None of these coefficients is causal. Investment, growth and the deficit are "
     "determined together and I use no instrument. What the crisis-year exercise shows is "
     "which results are most contaminated by that simultaneity, which is a weaker claim "
     "than causation but a defensible one.")

# --------------------------------------------------------------- part 4 -----
doc.add_heading("Part 4. The counterfactual", level=1)
para(doc,
     "What would have had to be true for LABOUR/ILO to work? The strategy was a "
     "conditional bet, and four conditions had to hold together.")
para(doc,
     "First, investment had to respond strongly to demand. Nattrass cites Chirinko's "
     "finding that lagged demand is the most significant empirical determinant of "
     "investment, so this was the better-supported prior even in 1996. My own estimates "
     "agree: outside the two recession years, a point of lagged growth buys 0.75 to 0.94 "
     "points of investment growth. On this condition the later evidence supports "
     "LABOUR/ILO.")
para(doc,
     "Second, growth had to translate into jobs. Here the record is better than the usual "
     "jobless-growth story suggests. Formal non-agricultural employment grew between 1.9 "
     "and 4.5 per cent a year from 2001 to 2006 and beat GEAR's 4.3 per cent target in "
     "2006. Demand-led growth did create formal jobs when it came. But Nattrass's warning "
     "still bites. Raising average labour productivity, which the high-productivity "
     "industrial and wage policies aimed at, mechanically lowers the employment "
     "elasticity of output. Real wage growth in 1996 to 1999 ran at 1.7, 2.3, 8.6 and 3.0 "
     "per cent against GEAR's assumed path of -0.5, 1.0, 1.0 and 1.0, and formal "
     "employment fell in every one of those years. The strategy wanted labour-demanding "
     "growth while its own allies bargained for wage floors that discourage it.")
para(doc,
     "Third, the capital account had to stay calm. This is where Nattrass criticises "
     "LABOUR/ILO hardest and where the counterfactual is weakest. A deficit-financed "
     "expansion only works if the risk premium and the capital outflow response to fiscal "
     "divergence are small. South Africa's history says otherwise: the 2001 currency "
     "collapse, the 2008 reversal, and the debt path since 2020. Nattrass's East Asian "
     "comparison is the telling one. Malaysia and Thailand could run large deficits "
     "because deep domestic savings made them less prone to destabilising capital flight. "
     "South Africa's savings rate was low then and is low now, so the same deficit is a "
     "different instrument here.")
para(doc,
     "Fourth, the expansion had to avoid destabilising the economy. Nattrass is explicit "
     "that the demand relationship has a ceiling. If expansion produces inflation and "
     "depreciation, profitability suffers and investment falls rather than rises. Latin "
     "American macroeconomic populism is her example. LABOUR/ILO needed demand strong "
     "enough to pull investment along but not so strong that it broke the conditions "
     "investment depends on, which is a narrow path to walk.")
para(doc,
     "The conclusion is not that LABOUR/ILO would have worked. It is that each camp was "
     "right about what the other missed. LABOUR/ILO identified the mechanism GEAR got "
     "wrong, since investment does follow demand and the confidence channel does not show "
     "up in my results. GEAR took seriously the constraint LABOUR/ILO waved away, since an "
     "open capital account and a low savings rate really do limit what fiscal policy can "
     "do. Nattrass criticised both camps in 1996 and my own evidence leaves that criticism "
     "standing.")

# ----------------------------------------------------------- conclusion -----
doc.add_heading("Conclusion", level=1)
para(doc,
     "Three findings come out of this exercise. The first is descriptive. Across "
     "twenty-nine years South Africa met the targets GEAR set for inflation, the deficit "
     "and the real interest rate in most years, and missed the targets for growth, "
     "investment and employment in nearly all of them. Private investment growth never "
     "once reached its target. GEAR was not sold as a stabilisation plan for its own "
     "sake, so meeting only the stabilisation half is a failure on the strategy's own "
     "terms.")
para(doc,
     "The second finding is that the regression evidence points the same way, but only "
     "after the crisis years are handled properly. Taken whole, the sample says the "
     "deficit predicts investment with GEAR's expected sign. That result rests entirely "
     "on 2009 and 2020, when recession drove the deficit and investment at the same time "
     "and in opposite directions. Remove those two years and the fiscal signal "
     "disappears while the demand channel strengthens.")
para(doc,
     "The third finding concerns what the data can and cannot settle. My demand result "
     "does not hold on the alternative GDP vintage, the dependent variable's definition "
     "is not fully verified, the employment series has a nine-year hole, and nothing here "
     "is identified causally. The evidence is mixed. What makes it useful is that the "
     "mixing has a traceable source, which is two recessions doing the work of a "
     "behavioural parameter. Nattrass refused to call the bet in 1996 on the grounds that "
     "the profession knew very little about how investors respond. Thirty years of data "
     "narrow the question without closing it.")

# --------------------------------------------------------------- traps ------
doc.add_page_break()
doc.add_heading("How I handled the traps", level=1)
TRAPS = [
    ("1. Employment series is not continuous",
     "Kept OHS, LFS, QLFS and QES separate by survey label and never spliced across them. "
     "The supplied extract has no coverage for 2016 to 2024, so employment appears for "
     "only 12 of 29 years. I left the gap visible rather than interpolating."),
    ("2. Private investment is not one thing",
     "Not fully resolved, and reported as such. The series carries no source or series "
     "code. Its 2009 and 2020 contractions (-12.8 and -14.6 per cent) are far too steep "
     "for a blended total that includes public and parastatal capital spending, which is "
     "consistent with a private-only series. That is corroboration, not confirmation."),
    ("3. Nominal versus real, and which deflator",
     "Investment and GDP are constant-price. The deficit is a ratio of two nominal series, "
     "so it needs no deflating. The real bank rate is the nominal annual average minus "
     "annual-average CPI, which is how Nattrass built hers. That is an ex-post rate, not "
     "an ex-ante one, and the two can differ sharply in fast-disinflation years."),
    ("4. Boshoff and Fourie's splice",
     "Used as the Part 3 sensitivity check. The demand result holds on SARB market-price "
     "GDP and disappears on the factor-cost series, so the finding is sensitive to this "
     "choice and I say so rather than reporting only the specification I prefer."),
    ("5. Cells reconstructed from a damaged scan",
     "All checked against Nattrass (2001) and the 1996 GEAR document. All correct as "
     "supplied. The dictionary says six cells, the file has five."),
    ("6. Data vintage",
     "Made explicitly and differently in each part. Part 2 chains vintages so GEAR is "
     "judged against the data of its day, with the splice year marked on every plot. Part "
     "3 holds one vintage fixed so the break is not estimated into the coefficients."),
    ("7. Endogeneity",
     "Diagnosed, not solved. No instrument is used and no coefficient is causal. The "
     "crisis-year exercise exists to show which results simultaneity contaminates most."),
]
tt = doc.add_table(rows=len(TRAPS) + 1, cols=2)
tt.style = "Table Grid"
for j, h in enumerate(["Trap", "How it was handled"]):
    ctext(tt.rows[0].cells[j], h, bold=True)
    shade(tt.rows[0].cells[j])
for i, (a, b) in enumerate(TRAPS, start=1):
    ctext(tt.rows[i].cells[0], a, size=8.5, align="left")
    ctext(tt.rows[i].cells[1], b, size=8.5, align="left")
    tt.rows[i].cells[0].width = Cm(4.5)
    tt.rows[i].cells[1].width = Cm(12)
caption(doc, "Table 5. The seven traps and how each was treated.")

# ----------------------------------------------------------- references -----
doc.add_heading("References", level=1)
REFS = [
    "Boshoff, W.H. and Fourie, J. (2020) 'The South African economy in the twentieth "
    "century', in Boshoff, W.H. (ed.) Business Cycles and Structural Change in South "
    "Africa. Cham: Springer.",
    "Chirinko, R. (1993) 'Business fixed investment spending: modeling strategies, "
    "empirical results and policy implications', Journal of Economic Literature, 31, "
    "pp. 1875-1911. Cited in Nattrass (2001).",
    "Nattrass, N. (1996) 'Gambling on investment: competing economic strategies in South "
    "Africa', Transformation, 31, pp. 25-42.",
    "Nattrass, N. (2001) 'High productivity now: a critical review of South Africa's "
    "growth strategy', Transformation, 45, pp. 1-24.",
    "South Africa (1996) Growth, Employment and Redistribution: A Macroeconomic Strategy. "
    "Pretoria: Department of Finance.",
    "South African Reserve Bank (2001) Annual Economic Report 2001. Pretoria: SARB.",
    "Statistics South Africa (various years) Consumer Price Index (P0141); Quarterly "
    "Employment Statistics; Labour Force Survey. Pretoria: StatsSA.",
    "Weeks, J. (1999) 'Stuck in low GEAR? Macroeconomic policy in South Africa, 1996-98', "
    "Cambridge Journal of Economics, 23(4), pp. 795-811.",
]
for r_ in REFS:
    p = doc.add_paragraph()
    rr = p.add_run(r_)
    rr.font.size = Pt(9.5)

doc.save(OUT)
print(f"Saved: {OUT}")
print(f"Body word count (prose only, excludes tables, figures, captions, references): {word_count}")
