# Which Asian markets should an Australian non-ferrous metals exporter prioritise?

A market-prioritisation analysis of Australian merchandise exports using 138 months of ABS trade data across eight Asian destinations. Python is used for data cleaning, screening, model validation and forecasting; Power BI is used for the decision dashboard.

**Dashboard:** Power BI, with three pages: **Market Overview**, **Market Prioritisation**, and **Forecast Validation & 12-Month Outlook**. A public Power BI embed is not included; the portfolio version should retain the `.pbix` backup and static dashboard screenshots in the repository.

---

## The question

A metals trading business with existing Australian supply wants to know where to concentrate commercial effort over the next 12 months. Which destination markets combine meaningful size, sustained growth, sufficient stability, and forecast behaviour that adds value beyond simple naive benchmarks?

The analysis addresses three questions:

1. Which metal commodity group provides a meaningful market-allocation problem?
2. Which Asian destinations combine growth, scale and stability?
3. Do statistical forecasts add enough out-of-sample value to support those rankings?

---

## Three findings

### 1. The commodity that dominates the trade is the one with the least allocation choice

Ores and scrap (SITC 28) represent **91.9%** of sampled export value, and **79.1%** of that selected-market trade goes to a single destination. The concentration is a real finding, but it largely answers the prioritisation question before modelling begins.

Non-ferrous metals (SITC 68) represent **8.1%** of sampled value and are much more evenly distributed across the eight selected destinations, with the major markets clustered around 11–17% of selected-market trade. SITC 68 therefore became the analytical focus.

Iron and steel (SITC 67) represent only **0.04%** of sampled value. In this selected-market context, Australia exports very large amounts of upstream ore and comparatively little finished iron and steel; that is a useful value-chain observation, but not a strong forecasting problem.

### 2. Vietnam is the clearest growth case, and the conclusion is robust to the starting quarter

Vietnam records a headline three-year CAGR of **33.2%**, with relatively low 36-month volatility (**CV 0.246** versus a sample median of about **0.32**). Its selected SARIMA model achieves **14.13% MAPE** on the held-out year and beats both flat-naive and seasonal-naive benchmarks.

The growth conclusion also survives a base-date sensitivity check. Across four alternative 2023 starting quarters, Vietnam's annualised growth remains between **27.7% and 33.2%**. Thailand also passes the growth, stability and forecastability criteria, but its growth estimate is much more base-sensitive (**11.2% to 26.1%**).

### 3. The current market ranking is recent, and long-run growth can hide a turning point

Malaysia is currently the largest SITC 68 destination in the selected set at about **AUD 2.17bn** over the latest 12 months, but that ranking is recent rather than structural. It reached first place only in early 2026 after China had fallen sharply.

China still carries a negative three-year CAGR of **−8.1%**, with sensitivity estimates ranging from **−15.1% to −5.1%**, but its rolling 12-month exports rose from about **AUD 1.53bn in January 2026 to AUD 2.00bn in June 2026**, a **30.7%** rebound from the recent trough. The case illustrates why a single long-horizon growth statistic can misdescribe current momentum.

---

## Recommendations

| Market | Position | Basis |
|---|---|---|
| **Vietnam** | **Priority for growth** | Strongest sustained growth, low volatility, robust base-date sensitivity, and SARIMA beats both naive benchmarks |
| **Thailand** | **Selective expansion** | Growth and stability criteria met; SARIMA beats the better naive benchmark, but growth and forecast ranges are wider than Vietnam's |
| **Malaysia** | **Maintain coverage** | Largest and most stable market, but the selected ETS model does not beat flat naive and retains residual autocorrelation |
| **China** | **Watch closely** | Negative three-year trend, but a strong recent rebound means the longer-run CAGR is not the full story |
| **South Korea** | **Established / low momentum** | Relatively stable but negative three-year growth |
| **Japan** | **Monitor** | Positive growth but volatility above the screening threshold |
| **Taiwan** | **Monitor / borderline** | Positive growth, but stability narrowly fails and CAGR is sensitive to the base quarter |
| **India** | **Deprioritise** | Very small base and extreme volatility despite a high percentage growth rate |

The forecasts **support** these rankings; they do not establish them. All three 95% forecast intervals include zero growth and also admit contraction, so historical growth, stability and out-of-sample forecast performance carry more decision weight than the central point forecasts.

---

## Data

**Source:** ABS Data Explorer, dataflow `ABS:MERCH_EXP(1.0.0)`, *Merchandise Exports by Commodity (SITC)* — FOB merchandise export value by destination country and state of origin, monthly.

**Scope:** SITC 28, 67 and 68 × 8 destinations × State = Total Australia, Jan 2015 – Jun 2026 (**138 months**). Reference period June 2026, released 6 August 2026. Downloaded 1 September 2026; download parameters are recorded in `data/raw/download_log.md`.

**Destinations:** China, Japan, South Korea, India, Taiwan, Vietnam, Thailand and Malaysia.

DFAT pivot tables were not used because their monthly series begins in Jan 2022 and DFAT applies adjustments that make those figures non-comparable with the ABS extract used here.

### Data quality work

**Unit multiplier.** `OBS_VALUE` is not raw AUD. `UNIT_MULT = 3` means the extract is denominated in thousands, so using `OBS_VALUE` directly would understate values by a factor of 1,000.

**Missing rows.** Eleven monthly rows are absent from the raw extract, all in SITC 67. The cleaning pipeline reindexes onto the complete commodity × country × month grid and inserts `NaN`, flagged as `is_imputed_gap`. Missing values are **not** filled with zero because the file cannot distinguish a genuine nil observation from confidentiality suppression.

**Explicit zeros.** Seven observations are exactly zero, all in SITC 67. They are treated as unresolved rather than interpreted because they were not cross-checked against the ABS Confidential Commodities List.

The SITC 68 analysis matrix contains **138 months × 8 markets with no missing values**.

---

## Method

### Screening

Growth is measured as three-year CAGR on rolling 12-month export totals. Stability is measured as the coefficient of variation of monthly export values over the latest 36 months. Rolling totals are used because month-to-month export values are heavily affected by shipment timing.

The market-screening rule was fixed before forecast model comparison:

- shortlist if **3-year CAGR ≥ 5%**;
- shortlist if **36-month CV < sample median**;
- treat the market as forecastable only if its selected statistical model beats the **better of flat-naive and seasonal-naive benchmarks** on the held-out year.

### Validation

Training period: **Jan 2015 – Jun 2025 (126 months)**  
Test period: **Jul 2025 – Jun 2026 (12 months)**

ETS specifications are selected on the training sample using **AICc across six candidate specifications**. SARIMA orders are selected using **training AIC** over a `(p,1,q)(P,1,Q)₁₂` grid. The test set is used once for out-of-sample comparison and never for model selection.

All six ETS candidate specifications ran successfully in the final audit, so the selected ETS models were not artifacts of silent convergence failures.

### Benchmarks

Two naive baselines are reported:

- **Flat naive:** repeat the final training observation.
- **Seasonal naive:** repeat the same calendar month from the previous year.

Both are needed. Thailand's final training month is unusually high, which makes flat-naive MAPE **58.97%** and exaggerates the apparent improvement of statistical models. Malaysia shows the opposite problem: its final training observation happens to be very close to the following test-period mean, making flat naive unusually competitive at **12.08% MAPE**.

### Forecast uncertainty

The selected statistical model for each shortlisted market is refit on the full 138-month series. Annual forecast intervals are generated from **5,000 simulated 12-month paths** and summed path by path. The simulation is seeded for reproducibility.

The point estimate is therefore interpreted together with the interval, rather than as a deterministic prediction.

---

## Results

### Screening

| Market | Latest 12M (AUD m) | Share of selected markets | 3Y CAGR | CV (36m) | Shortlisted |
|---|---:|---:|---:|---:|:--:|
| Malaysia | 2,173 | 17.3% | +12.0% | 0.220 | Yes |
| China | 1,999 | 15.9% | −8.1% | 0.362 | No |
| South Korea | 1,840 | 14.6% | −3.6% | 0.310 | No |
| Japan | 1,817 | 14.4% | +10.0% | 0.397 | No |
| Vietnam | 1,676 | 13.3% | +33.2% | 0.246 | Yes |
| Taiwan | 1,475 | 11.7% | +8.4% | 0.337 | No |
| Thailand | 1,412 | 11.2% | +14.9% | 0.277 | Yes |
| India | 193 | 1.5% | +34.1% | 1.549 | No |

Median CV is approximately **0.32**. Shares are calculated only across the eight selected destinations, not across all Australian export markets.

India tops the headline growth column but is excluded on stability. Its CV of **1.549** is about five times the median, and the series behaves more like irregular shipments on a small base than a stable growth market.

Taiwan narrowly fails the stability screen (**0.337 vs ~0.32 median**) and its annualised growth varies from **1.5% to 12.9%** depending on the starting quarter, making it genuinely borderline.

### Growth-rate sensitivity

Annualised growth to Jun 2026 from four alternative 2023 base quarters:

| Market | Mar-23 | Jun-23 | Sep-23 | Dec-23 | Range |
|---|---:|---:|---:|---:|---:|
| Vietnam | 27.7% | 33.2% | 33.1% | 32.2% | 5.5 pp |
| Thailand | 11.2% | 14.9% | 18.0% | 26.1% | 14.9 pp |
| Malaysia | 10.3% | 12.0% | 11.7% | 15.0% | 4.7 pp |
| Japan | 7.8% | 10.0% | 14.9% | 16.5% | 8.7 pp |
| Taiwan | 1.5% | 8.4% | 8.3% | 12.9% | 11.4 pp |
| South Korea | −0.1% | −3.6% | −4.9% | −6.2% | 6.1 pp |
| China | −5.1% | −8.1% | −12.6% | −15.1% | 10.0 pp |
| India | 16.1% | 34.1% | 34.4% | 39.2% | 23.1 pp |

The headline screening CAGR uses Jun-2023. Vietnam's conclusion is comparatively robust to the base quarter, whereas Thailand, Taiwan, China and especially India are more sensitive.

### Validation: 12-month holdout

| Market | Flat naive | Seasonal naive | ETS (AICc) | SARIMA (AIC) | Selected statistical model | Beats better benchmark |
|---|---:|---:|---:|---:|---|:--:|
| Vietnam | 16.72% | 18.49% | 18.19% | **14.13%** | SARIMA(0,1,2)(0,1,1)₁₂ | Yes |
| Thailand | 58.97% | 21.11% | 17.43% | **15.59%** | SARIMA(1,1,2)(0,1,1)₁₂ | Yes |
| Malaysia | **12.08%** | 28.00% | 13.88% | 19.82% | ETS Level | **No** |

MAPE is measured on Jul 2025 – Jun 2026.

Vietnam and Thailand both add out-of-sample value relative to the better naive benchmark. Malaysia does not: its best statistical model (ETS Level, **13.88%**) is slightly worse than flat naive (**12.08%**). Under the predefined rule, Malaysia therefore remains a maintain/monitor market rather than a forecast-driven expansion candidate.

### Residual diagnostics

Ljung–Box tests were run on the selected statistical models at lags 12 and 24, with degrees of freedom adjusted for estimated parameters.

| Market | Lag 12 p-value | Lag 24 p-value | Interpretation |
|---|---:|---:|---|
| Vietnam | 0.3030 | 0.4048 | No statistically significant residual autocorrelation detected |
| Thailand | 0.4548 | 0.5670 | No statistically significant residual autocorrelation detected |
| Malaysia | **0.0011** | **0.0097** | Significant residual autocorrelation remains |

Malaysia therefore carries an additional model-specification warning beyond its failure to beat the flat-naive benchmark.

### Forecasts: Jul 2026 – Jun 2027

| Market | Latest 12M (AUD m) | Point forecast (AUD m) | Change | 95% interval on change |
|---|---:|---:|---:|---:|
| Vietnam | 1,676 | **1,940** | **+15.8%** | **−10.2% to +41.5%** |
| Thailand | 1,411 | **1,518** | **+7.5%** | **−15.9% to +31.6%** |
| Malaysia | 2,173 | **2,072** | **−4.7%** | **−48.5% to +38.5%** |

All three 95% intervals span zero growth. The correct interpretation is therefore not that Vietnam *will* grow 15.8%, Thailand *will* grow 7.5%, or Malaysia *will* decline 4.7%. The central estimates indicate direction, but the uncertainty remains large enough to admit materially different outcomes.

Historical growth, stability and out-of-sample forecast performance therefore carry more weight in the recommendations than the point forecasts themselves.

---

## Analytical revisions

The analysis was audited and corrected. Those revisions are documented because the size and direction of the corrections are themselves useful evidence of analytical discipline.

**Commodity scope changed after inspection.** The project began with SITC 28, 67 and 68, then narrowed to SITC 68 once the size and concentration structure showed that it offered the meaningful allocation problem.

**Test-set leakage removed.** ETS specifications were initially chosen by test-set error while SARIMA orders were selected on training AIC. Once ETS selection was moved to training-only AICc, Thailand's ETS MAPE moved from **15.23% to 17.43%** — a **2.2 percentage-point** optimism gap caused purely by model-selection leakage.

**Benchmark logic strengthened.** A single flat-naive baseline made Thailand's model improvement look much larger than it was because the final training month was an outlier. The final rule requires a selected statistical model to beat the **better of flat naive and seasonal naive**.

**Growth-rate sensitivity corrected.** The first sensitivity implementation incorrectly used a fixed three-year exponent for every starting quarter. The corrected calculation uses the actual elapsed years for each base date. Vietnam's resulting range is **27.7–33.2%**.

**Naive methods kept as benchmarks, not selected statistical models.** The final pipeline first selects the best statistical model, then compares it against the better naive benchmark. This prevents Malaysia's strong flat-naive baseline from being incorrectly promoted as the statistical forecast model.

**Simulation reproducibility fixed.** Forecast-path simulation now uses a deterministic seed compatible with both ETS and SARIMA, so annual forecast intervals reproduce across runs.

**Point forecasts demoted.** Central changes are modest relative to out-of-sample error and all three 95% intervals include zero growth. The final recommendations therefore use point forecasts as supporting evidence rather than decision rules.

---

## Power BI dashboard

The Power BI report contains three pages:

1. **Market Overview** — latest 12-month SITC 68 market size, market ranking, rolling 12-month trends, commodity mix, and China's rebound from its recent trough.
2. **Market Prioritisation** — growth-versus-volatility bubble chart, CAGR base-quarter sensitivity, and final recommendation table.
3. **Forecast Validation & 12-Month Outlook** — out-of-sample model comparison, point forecasts with 95% error bars, benchmark status, forecast summary and residual diagnostics.

The dashboard is designed to show the decision logic visually rather than present forecasts as certain outcomes.

---

## Limitations

**Nominal values.** Export values are FOB nominal values and are not deflated.

**Price and quantity cannot be separated.** The ABS dataflow used here contains value only, so higher export value cannot be decomposed into higher shipment volume versus higher commodity prices. This is the largest interpretive limitation.

**Long-run growth can hide turning points.** A three-year CAGR cannot detect a reversal inside its own window; China is the clearest example.

**Structural breaks.** The training period spans COVID-era disruption, Australia–China trade tensions and commodity-cycle changes. ETS and SARIMA estimate across those regimes rather than modelling explicit structural breaks.

**Holdout overlaps an ABS revision window.** The June 2026 release revised historical observations back to December 2025, so part of the test period contains values that were not available in their final revised form at the original point in time. The exercise is therefore not a true vintage-data backtest.

**Confidentiality suppression.** Some commodity–country observations may be affected by ABS confidentiality treatment. Explicit SITC 67 zeros were not interpreted as true nil trade without further verification.

**Univariate forecasting.** Commodity prices, exchange rates, GDP, tariffs, industrial demand and policy variables are not included.

**Selected-market shares only.** Reported market shares refer to the eight selected destinations, not global Australian exports.

**Growth is base-sensitive.** This is quantified directly through the sensitivity table rather than assumed away.

---

## Repository structure

```text
data/raw/        source extract, never modified, plus download_log.md
data/clean/      exports_tidy.csv
src/clean.py     cleaning, gap handling, unit conversion, quality report
src/model.py     benchmarks, model selection, intervals, diagnostics, sensitivity
outputs/         data_quality_report.md, model_validation.csv,
                 forecast_intervals.csv, cagr_sensitivity.csv,
                 recent_momentum.csv, model_results.md
powerbi/         Power BI .pbix backup and theme JSON
dashboard/       static screenshots for the three Power BI pages
```

### Reproduce

```bash
pip install pandas numpy statsmodels matplotlib
python src/clean.py
python src/model.py
```

Figures may not reproduce exactly against a fresh ABS download because ABS merchandise-trade data are revised over time. `data/raw/download_log.md` records the extract used for this analysis.
