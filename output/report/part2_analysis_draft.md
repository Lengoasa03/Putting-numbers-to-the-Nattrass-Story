# Part 2 — Extending the series: analysis draft

*Draft prose for the final write-up. Figures referenced are in `figures/part2_*.png`,
built from `data/part2_extended_series_1996_2024.csv` by `part2_plot_series.py`.*

## Which of GEAR's targets were met, and when?

A target is scored as "met" if the actual value beat or matched GEAR's own
target for that year (1996–2000), or — for years after GEAR's targets stop in
2000 — beat or matched GEAR's final (2000) target level, treated as the
strategy's implied steady-state goal. "Beat" means higher for the growth-type
indicators (GDP, private investment, employment) and lower for the
restraint-type indicators (inflation, deficit, real interest rate).

| Indicator | Years the target was met |
|---|---|
| Real GDP growth | 1996 only |
| Real private investment growth | **Never**, 1996–2024 |
| Non-agric. formal employment growth | 2006 only (and only 12 of 29 years have data at all — see the gap discussion below) |
| CPI inflation | Almost every year: 1996–2001, then 2003–2024 (missed only 2002 and 2008, both identifiable shock years — the 2001/02 currency collapse and the global financial crisis/commodity spike) |
| Budget deficit, % of GDP | 1996, 1998–2008 (missed 1997, then continuously from 2009 onward) |
| Real bank/repo rate | 2006–2023 |

## Is there a pattern? (There is.)

Yes, and it is stark: **the three "stabilisation" indicators (inflation, the
deficit, the real interest rate) were met in the overwhelming majority of
years after 2000. The three "growth" indicators (GDP growth, private
investment growth, employment growth) were essentially never met.**

This is not a close call. Inflation beat its steady-state target in 27 of 29
years; the deficit beat its target in 13 of 29 (with a clean run 1998–2008
before the post-2008 fiscal deterioration); the real interest rate beat its
target in 18 consecutive years from 2006. Real GDP growth beat its target in
exactly one year — 1996, the very first year, before the strategy had time to
act. Private investment growth never once reached its target, in either the
1996–2000 window Nattrass covered or the 24 years since.

**Why this matters:** GEAR's architects (SAF/GEAR, per Nattrass) bet that
credible fiscal and monetary discipline would restore business *confidence*,
and that confidence — not demand — was the binding constraint on private
investment. The results here are close to a clean test of that bet, and it
fails on its own terms: South Africa delivered the discipline (low, stable
inflation; a shrinking then roughly balanced budget for a decade; positive,
moderate real interest rates) far more successfully than it delivered growth
or investment. If confidence were the binding constraint, sustained
stabilisation success should have been followed by a sustained investment
and growth response. It was not. That is the pattern GEAR's critics — the
LABOUR/ILO side, in Nattrass's framing — pointed to: investment looks far
more tied to *demand conditions* (which is what Part 3's regression tests
directly) than to the confidence signals GEAR targeted.

A caveat belongs here too, because the brief warns against a lazy "GEAR
simply failed" reading: growth *did* accelerate for a real stretch,
2004–2007 (peaking near 5.6% in 2006), alongside a budget surplus and the
lowest inflation of the whole series (2004: 1.4%) — the one period where
stabilisation and growth moved together. That episode complicates a simple
"stabilisation without growth" story and has to be engaged with directly in
Part 3/4, not glossed over.

## Data-quality flag carried over from this step

Non-agric. formal employment growth is only observable for 12 of the 29
years (1996–1999, 2001–2006, 2010, 2014). The run from 2016–2024 — exactly
the period that would show how employment behaved after the 2008 financial
crisis and through the COVID shock — is **not covered by any source
supplied**. This is reported as a genuine limitation of the available data,
per trap #1, rather than bridged by interpolation or a spliced-together
"employment_series_name" that would misrepresent three incompatible surveys
(OHS, LFS/QLFS, QES) as one continuous measure.
