# Traps 2 and 3 — definitional checks

*Written to close the gap flagged earlier: trap 2 (private investment
definition) was only loosely checked, and trap 3 (real vs nominal, deflator
choice) had never been written up as one consolidated statement. Both belong
in the final report's methodology section.*

## Trap 2 — is "private investment" the same thing across 1996–2000 and 2001–2024?

**What I tried:** I looked for the exact SARB series code behind
`sarb_private_investment_1994_2025_RAW.csv` so I could confirm it is
"gross fixed capital formation, private business enterprises, constant
prices" — the same concept Nattrass's 1996–2000 figures use — rather than
total GFCF or a different investment aggregate. SARB's online statistical
query tool is an interactive JavaScript form, not a fetchable data page, so
I could not resolve the code directly, and this file (unlike most others in
the Additional data folder) carries no source/series-code column at all.

**What I could check instead, and what it shows:** South Africa's 2009
recession is a useful natural test, because public and private investment
moved in *opposite* directions that year — Eskom's Medupi/Kusile build and
2010 World Cup stadium construction kept public and parastatal capital
formation expanding even as private investment collapsed. Total GFCF is
widely reported as falling only modestly in 2009 (public/parastatal spending
offset most of the private decline), while this series shows **private
investment falling 12.8% in 2009** — a decline far too large to be a
blended total-GFCF figure for that year, and consistent with a private-only
series. The same pattern holds in 2020 (−14.6%, COVID), a year private
capital spending collapsed much more sharply than public infrastructure
spend. This is directional, corroborating evidence, not a citation.

**Conclusion — stated as a limitation, not resolved as a fact:** the balance
of evidence (the 2009/2020 contraction sizes) is consistent with this being
a private-only series comparable to Nattrass's, but I cannot independently
confirm it against a primary SARB table or series code, and this file lacks
the source column every other file in the folder has. **This is reported in
the final write-up as an unresolved limitation on the Part 3 regression's
dependent variable**, per the assignment's instruction to notice traps and
be honest about what the evidence can support, rather than silently assumed
away.

## Trap 3 — nominal vs real, and which deflator, for every series used

| Series | Real or nominal? | How "real" is constructed |
|---|---|---|
| Real GDP growth | Real | Boshoff & Fourie (1994–2017): GDP at factor cost, constant 2010 prices. SARB market-price series (2018–2024, Additional data): GDP at market prices, constant prices (base year not confirmed — another facet of trap 2/6, flagged). **These are not the same deflator or the same price concept (factor cost vs market prices)** — the splice at 2017/2018 is a genuine break, marked in the Part 2 plots, not hidden. |
| Real private investment growth | Real | GEAR/Nattrass actuals (1996–2000): Nattrass's own real (constant-price) private investment series. Additional data (2001–2024): `private_inv_constant_Rm`, stated to be constant prices; base year not confirmed (see trap 2 above). |
| CPI inflation | This *is* the deflator for other series, not itself deflated | Headline CPI, annual average (StatsSA P0141). Not CPIX or Dec/Dec — annual average was chosen for comparability with GEAR's own annual-average CPI targets. |
| Deficit, % of GDP | Ratio of two nominal series | Both numerator (cash-flow balance) and denominator (GDP) are **current-price (nominal)** Rand values, so the ratio itself needs no deflating — a common source of error in this literature (comparing a real numerator to a nominal denominator, or vice versa) is avoided here because both sides of the ratio are on the same (nominal) basis. |
| Real bank/repo rate | Real, constructed here (not given directly by SARB) | Nominal SARB Bank rate (annual average) minus headline CPI annual-average inflation — an ex-post real rate, exactly the method Data.md documents Nattrass having used. This is a simple Fisher approximation (nominal − expected inflation ≈ real), not an ex-ante real rate using inflation expectations; that distinction is worth a sentence in the final write-up since ex-post and ex-ante real rates can diverge sharply in high-inflation or disinflation years (e.g. 1998, when inflation was falling fast). |

**One outstanding deflator question for Part 3:** the regression's real
interest rate and real GDP growth need to be on a mutually consistent basis
before estimation. Since real GDP growth for 2018–2024 already breaks from
Boshoff & Fourie's factor-cost concept to a market-price concept, I will
need to either (a) restrict the regression's main specification to the
period where a single real GDP concept is available throughout, or (b) run
it on the full spliced series and explicitly re-run with the pre-2018-only
period as a sensitivity check (folding in trap 4's Boshoff & Fourie
splice-sensitivity requirement at the same time, since both are "does the
regression survive a change in GDP vintage/definition" questions). I'll
decide this when I build the Part 3 model.
