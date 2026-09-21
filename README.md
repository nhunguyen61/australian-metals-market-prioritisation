# Which Asian markets should an Australian non-ferrous metals exporter prioritise?

![Python](https://img.shields.io/badge/Python-Analytics-blue)
![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-yellow)
![ABS Data](https://img.shields.io/badge/Data-ABS-green)

A market-prioritisation analysis of Australian merchandise exports using 138 months of ABS trade data across eight Asian destinations. Python is used for data cleaning, screening, model validation and forecasting; Power BI is used to build the decision-support dashboard.

**Dashboard:** Power BI report with three pages:
- Market Overview
- Market Prioritisation
- Forecast Validation & 12-Month Outlook

The portfolio version retains the `.pbix` backup and static dashboard screenshots in the repository.

---

# Dashboard Preview

## Market Overview

![Market Overview](dashboard/01_market_overview.png)


## Market Prioritisation

![Market Prioritisation](dashboard/02_market_prioritisation.png)


## Forecast Validation & Outlook

![Forecast Validation](dashboard/03_forecast_validation.png)


---

# Key Findings

## 1. SITC 68 provides the most meaningful market allocation problem

The analysis initially evaluated three commodity groups:

- SITC 28 — Ores and scrap
- SITC 67 — Iron and steel
- SITC 68 — Non-ferrous metals

Ores and scrap dominate Australian exports, representing **91.9%** of sampled export value. However, the trade is highly concentrated, limiting the strategic allocation problem.

Non-ferrous metals (SITC 68) represent **8.1%** of sampled value but are distributed more evenly across the eight selected Asian destinations, making it the most suitable commodity group for market prioritisation.

Iron and steel represents only **0.04%** of sampled value and was excluded from forecasting analysis.

---

## 2. Vietnam demonstrates the strongest growth momentum

Vietnam records:

- 3-year CAGR: **33.2%**
- 36-month volatility (CV): **0.246**
- SARIMA validation MAPE: **14.13%**

The growth conclusion remains consistent under alternative base-quarter sensitivity testing, with annualised growth ranging from **27.7% to 33.2%**.

Thailand also satisfies growth, stability and forecastability criteria, although its growth estimate is more sensitive to the starting period.

---

## 3. Current market leadership does not always represent long-term momentum

Malaysia is currently the largest SITC 68 destination:

- Latest 12-month export value: **AUD 2.17bn**

However, its selected ETS model does not outperform the flat-naive benchmark.

China experienced a negative three-year CAGR (**−8.1%**) but showed recent recovery:

- Rolling 12-month exports increased from approximately AUD 1.53bn (Jan 2026) to AUD 2.00bn (Jun 2026)
- Recovery from recent trough: **30.7%**

This highlights the importance of combining long-term growth indicators with recent market momentum.

---

# Market Prioritisation Outcome

| Market | Suggested Position | Evidence |
|---|---|---|
| Vietnam | Growth opportunity | Highest sustained growth, low volatility and SARIMA outperforming naive benchmarks |
| Thailand | Selective expansion | Meets screening criteria with strong forecast performance |
| Malaysia | Maintain coverage | Largest market but forecast improvement over naive benchmark is limited |
| China | Monitor recovery | Negative long-term trend but improving recent momentum |
| South Korea | Established market | Stable but negative growth trend |
| Japan | Monitor | Positive growth but higher volatility |
| Taiwan | Monitor | Positive growth but borderline stability |
| India | Low priority | High growth percentage driven by small and volatile base |

Forecasts are treated as supporting evidence rather than deterministic predictions. Historical growth, stability and out-of-sample validation remain the primary decision factors.

---

# Methodology

The analysis followed a structured market prioritisation framework.

## 1. Data Preparation

- Extracted Australian SITC export data from ABS Data Explorer
- Converted export values into AUD million
- Prepared monthly time-series data from Jan 2015 to Jun 2026

## 2. Market Screening

Markets were evaluated using:

- Export scale
- 3-year CAGR growth
- 36-month volatility (coefficient of variation)
- Forecast performance against benchmarks

## 3. Forecasting

Models evaluated:

- Flat naive benchmark
- Seasonal naive benchmark
- ETS (Exponential Smoothing)
- SARIMA

Models were selected using training-period criteria and evaluated on an out-of-sample 12-month validation period.

## 4. Forecast Uncertainty

Forecast intervals were generated using 5,000 simulated 12-month forecast paths.

Point forecasts are interpreted together with uncertainty intervals rather than as guaranteed outcomes.

---

# Tools

## Programming

- Python
  - pandas
  - numpy
  - statsmodels
  - pmdarima
  - scikit-learn

## Forecasting Methods

- ETS
- SARIMA
- Flat naive benchmark
- Seasonal naive benchmark

## Visualisation

- Power BI

## Data Source

- Australian Bureau of Statistics (ABS)
- Merchandise Exports by Commodity (SITC)

---

# Data

**Source:** ABS Data Explorer  
Dataset: *Merchandise Exports by Commodity (SITC)*

Scope:

- Commodity groups: SITC 28, 67 and 68
- Destinations:
  - China
  - Japan
  - South Korea
  - India
  - Taiwan
  - Vietnam
  - Thailand
  - Malaysia

Period:

- January 2015 – June 2026
- 138 monthly observations

---

# Validation Results

Training period: Jan 2015 – Jun 2025
Testing period: Jul 2025 – Jun 2026


Forecast validation:

| Market | Selected Model | MAPE | Beats Benchmark |
|---|---|---|---|
| Vietnam | SARIMA(0,1,2)(0,1,1)12 | 14.13% | Yes |
| Thailand | SARIMA(1,1,2)(0,1,1)12 | 15.59% | Yes |
| Malaysia | ETS Level | 13.88% | No |

---

# Power BI Dashboard

The dashboard contains three pages:

### 1. Market Overview

Includes:

- Latest 12-month export value
- Market ranking
- Rolling 12-month trends
- Commodity composition
- China's recent recovery


### 2. Market Prioritisation

Includes:

- Growth vs volatility bubble chart
- CAGR sensitivity analysis
- Market prioritisation table


### 3. Forecast Validation & 12-Month Outlook

Includes:

- Model comparison
- Benchmark performance
- Forecast intervals
- Residual diagnostics

The dashboard focuses on explaining decision logic rather than presenting forecasts as certain outcomes.

---

# Limitations

## Nominal Export Values

Export values are FOB nominal values and are not adjusted for inflation.

## Value vs Volume

ABS data contains export value only. Higher export value cannot be separated into:

- Higher shipment volume
- Higher commodity prices

## Structural Changes

The modelling period includes:

- COVID disruption
- Australia-China trade tensions
- Commodity-cycle changes

## Forecasting Scope

The models are univariate and do not include:

- Commodity prices
- Exchange rates
- GDP
- Industrial demand
- Policy variables

---

# Repository Structure

```text
australian-metals-market-prioritisation/

├── data/
│   └── clean/
│       └── exports_tidy.csv

├── src/
│   ├── clean.py
│   └── model.py

├── outputs/
│   ├── forecast_intervals.csv
│   ├── model_validation.csv
│   ├── cagr_sensitivity.csv
│   ├── recent_momentum.csv
│   └── model_results.md

├── powerbi/
│   └── Australian_Metals_Market_Prioritisation.pbix

├── dashboard/
│   ├── 01_market_overview.png
│   ├── 02_market_prioritisation.png
│   └── 03_forecast_validation.png

└── README.md
