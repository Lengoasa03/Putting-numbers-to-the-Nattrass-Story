# Part 3 — Testing the gamble: analysis draft

*Numeric record: `report/part3_results.txt`. Figure:
`figures/part3_coefficient_stability.png`. Scripts: `part3_build_regression_data.py`,
`part3_estimate.py`, `part3_plot_coefficients.py`.*

## The model and what it tests

    inv_growth_t = β₀ + β₁·gdp_growth_{t−1} + β₂·real_rate_t + β₃·deficit_gdp_t + ε_t

Estimated on annual data, 1994–2024, N = 31, on a **single consistent
current vintage** (SARB/StatsSA). Newey–West (HAC, lag 1) standard errors,
because the Breusch–Godfrey test rejects no-autocorrelation (LM = 5.01,
p = 0.025); OLS standard errors would overstate precision. Breusch–Pagan
finds no heteroskedasticity (p = 0.29), Jarque–Bera does not reject
normal residuals (p = 0.96), and VIFs are all below 1.6, so
multicollinearity is not an issue.

**Deficit sign convention: `deficit_gdp` is positive when in deficit.** So:

- **LABOUR/ILO (demand)** predicts **β₁ > 0** — investment follows demand.
- **SAF/GEAR (confidence/signal)** predicts **β₃ < 0** — a bigger deficit
  damages investor confidence, so consolidation crowds investment *in*.

## Headline result, and why it does not survive scrutiny

On the full sample the result looks like a clean win for GEAR:

| Variable | Coef. | HAC s.e. | p |
|---|---|---|---|
| Lagged real GDP growth (demand) | 0.521 | 0.389 | 0.180 |
| Real bank rate | −0.062 | 0.372 | 0.868 |
| **Deficit, % of GDP (signal)** | **−1.831** | 0.596 | **0.002** |

R² = 0.42. The signal channel is significant with exactly GEAR's predicted
sign; the demand channel is insignificant. Taken at face value this says
Nattrass's SAF/GEAR camp was right and the ILO camp was wrong.

**It should not be taken at face value.** Two tests break it.

### 1. The sign reverses across the 2008 split

A Chow test rejects parameter stability at 2008 (F(4,23) = 4.02,
p = 0.013). Estimating either side:

| Sample | Demand (β₁) | Signal (β₃) |
|---|---|---|
| 1994–2007 (N=14) | 0.870 (p = 0.113) | **+1.666 (p = 0.008)** |
| 2008–2024 (N=17) | 0.297 (p = 0.322) | **−2.311 (p < 0.001)** |

The signal coefficient does not merely weaken — it **flips sign and is
significant in both directions**. Before 2008, bigger deficits went with
*more* private investment (the Keynesian/demand sign); after 2008, with
*less*. A coefficient that reverses like this is not measuring a stable
behavioural parameter. The full-sample −1.83 is an average of two opposite
regimes, not a structural finding.

### 2. Two recession years drive the entire result

This is trap #7 (endogeneity) made concrete. In 2009 and 2020, the deficit
exploded *and* private investment collapsed — but the recession caused
both. Automatic stabilisers widen the deficit in a downturn by
construction, so the correlation runs recession → deficit, not deficit →
lost confidence → falling investment. Dropping those two observations
(2 of 31) reverses the entire interpretation:

| Sample | Demand (β₁) | Signal (β₃) |
|---|---|---|
| Full, 1994–2024 | 0.521 (p = 0.180) | −1.831 (**p = 0.002**) |
| Full, excl. 2009 & 2020 | **0.941 (p = 0.004)** | −0.697 (p = 0.150) |
| 2008–2024, excl. 2009 & 2020 | **0.747 (p < 0.001)** | −0.143 (p = 0.827) |

Once the two crisis years are removed, **the signal channel loses
significance entirely (p = 0.15, then p = 0.83) and the demand channel
becomes strongly significant.** The point estimate of 0.94 says a one-point
rise in last year's GDP growth is associated with roughly a one-point rise
in private investment growth — economically substantial, not just
statistically detectable. The 2008-onwards figure of 0.75 (p < 0.001, with
the real rate also correctly signed and significant at −0.98) is the
cleanest specification in the whole exercise on conventional criteria.

Figure `part3_coefficient_stability.png` shows this: the demand coefficient
is positive in all five specifications and tightens as the crisis outliers
come out; the signal coefficient swings from +1.67 to −2.31 and collapses
toward zero without them.

## Which stable does the evidence favour?

**On balance, the demand (LABOUR/ILO) channel — but with real
qualifications, and the honest answer is that the evidence is mixed in a
specific, diagnosable way.**

The case for demand: β₁ is positive in every single specification run, and
becomes significant precisely when the observations most contaminated by
reverse causation are removed. That is the pattern one expects from a real
relationship being obscured by noise, not manufactured by it.

The case against over-claiming it: the demand coefficient is *not*
significant on the full sample (p = 0.18), and it depends on the GDP series
used. The sensitivity check using Boshoff & Fourie's factor-cost GDP
(traps #4 and #6) gives β₁ = 0.264 (p = 0.774) — nothing survives. That is
a genuine fragility: the demand result holds on SARB market-price GDP and
vanishes on B&F factor-cost GDP over a shorter (1994–2018) sample. Part of
that is the shorter sample and part is the definitional switch, and I
cannot cleanly separate the two.

What can be said with more confidence is the **negative** finding: there is
**no robust evidence for the confidence channel GEAR was built on.** The
one specification where the signal channel is significant with GEAR's
predicted sign is also the specification most obviously contaminated by
recession-driven simultaneity, and it does not survive removing two
outlier years. GEAR's central bet — that fiscal consolidation would signal
credibility and thereby unlock private investment — is not supported here,
which is consistent with Part 2's finding that South Africa delivered the
consolidation without ever once hitting an investment target.

The pre-2008 positive deficit coefficient (+1.67) deserves a note rather
than a celebration. It has the demand sign, but 1994–2007 is exactly the
period when deficits were *shrinking* while investment was *rising*, so a
positive coefficient on a falling variable is as easily read as coincident
trends as causation. With N = 14 and no instrument, it cannot bear weight.

## Does the answer change if you split at 1994, or at 2008?

**At 2008: yes, decisively** — see above. The Chow test rejects stability
and the signal coefficient reverses sign. This is the single most
informative result in Part 3.

**At 1994: the split cannot be run.** The supplied deficit and policy-rate
series both begin in 1994, so there are zero pre-1994 observations for two
of the three regressors. This is a data-availability limit, not a modelling
choice. Rather than approximate it with a different or shorter
specification and present that as the requested test, it is reported as not
estimable on the data provided.

## Limitations, stated plainly

1. **Endogeneity is not solved, only diagnosed** (trap #7). Investment,
   growth and the deficit are jointly determined. No instrument is used, so
   none of these coefficients can be read as causal. What the crisis-year
   exercise shows is *which* results are most contaminated by simultaneity —
   which is a weaker but honest claim.
2. **N = 31.** Annual macro data on a 31-year window, with sub-samples of
   14 and 17. Power is low, and the sub-sample results in particular should
   be read as suggestive.
3. **The dependent variable's definition is not fully verified** (trap #2).
   The private investment series carries no source or series code; its
   2009/2020 contraction magnitudes are consistent with a private-only
   series, but this is corroboration, not confirmation.
4. **GDP vintage matters to the answer** (traps #4, #6). The demand result
   holds on SARB market-price GDP and does not hold on Boshoff & Fourie
   factor-cost GDP. Both are reported; neither is suppressed.
5. **The real rate is ex-post** (nominal minus realised CPI), following
   Nattrass's own construction, not an ex-ante rate using expectations.
