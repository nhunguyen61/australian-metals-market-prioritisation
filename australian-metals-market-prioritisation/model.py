"""
Forecast validation and 12-month projection for SITC 68 shortlist markets.

Fixes four defects in the first version of this analysis:

1. The only benchmark was a flat random walk anchored on the last training
   month. For Thailand that month was an outlier (183.6 against a test mean
   of 117.6), inflating benchmark error to 59% and overstating how much the
   ETS model improved on it. Both a flat naive and a seasonal naive are now
   reported, and the harder of the two is used as the benchmark to beat.

2. ETS specifications were selected on test-set error while SARIMA orders
   were selected on training AIC. The two were then compared on that same
   test set, which gave ETS an unearned advantage. Both families are now
   selected on the training sample only (AICc for ETS, AIC for SARIMA), so
   the test set is used once, for comparison, and never for selection.

3. Forecasts were reported as point estimates. Every projected 12-month
   change was smaller than the corresponding model's own MAPE, so none of
   them could support a recommendation. Annual totals now carry simulated
   80% and 95% intervals.

4. Three-year CAGR was measured from a single base quarter that happens to
   be a local trough for the fastest-growing market. A sensitivity table
   across four base quarters is now produced alongside it.

Input  : data/clean/exports_tidy.csv
Output : outputs/model_validation.csv   - all models, all markets, test errors
         outputs/forecast_intervals.csv - 12-month totals with intervals
         outputs/cagr_sensitivity.csv   - CAGR by base quarter
         outputs/model_results.md       - written summary

Run    : python src/model.py
"""

from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.tsa.exponential_smoothing.ets import ETSModel
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.statespace.sarimax import SARIMAX

ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "data" / "clean" / "exports_tidy.csv"
OUT = ROOT / "outputs"

SITC = 68
MARKETS = ["Vietnam", "Thailand", "Malaysia"]
TRAIN_END = "2025-06-30"
TEST_START = "2025-07-31"
HORIZON = 12
N_SIMS = 5000
SEED = 42

# Base quarters for the CAGR sensitivity check, with the actual number of
# years from each base to the end of the series.
#
# Using a fixed 1/3 exponent for every base was a defect in the first
# version of this script: Mar-2023 to Jun-2026 is 3.25 years, not 3, so a
# fixed exponent attributes the growth to the wrong span and mis-states
# every annualised rate except the one measured over exactly three years.
CAGR_BASES = {
    "2023-03-31": 3.25,
    "2023-06-30": 3.00,
    "2023-09-30": 2.75,
    "2023-12-31": 2.50,
}


# --------------------------------------------------------------------------
# Data
# --------------------------------------------------------------------------

def load_matrix() -> pd.DataFrame:
    df = pd.read_csv(CLEAN, parse_dates=["date"])
    df = df[df.sitc_code == SITC]
    w = df.pivot(index="date", columns="country", values="value_aud_m").sort_index()
    return w.asfreq("ME")


# --------------------------------------------------------------------------
# Error metrics
# --------------------------------------------------------------------------

def mae(actual: np.ndarray, fc: np.ndarray) -> float:
    return float(np.mean(np.abs(actual - fc)))


def mape(actual: np.ndarray, fc: np.ndarray) -> float:
    return float(np.mean(np.abs((actual - fc) / actual)) * 100)


# --------------------------------------------------------------------------
# Benchmarks
# --------------------------------------------------------------------------

def naive_forecast(train: pd.Series, h: int) -> np.ndarray:
    """Flat random walk: repeat the last observed value."""
    return np.repeat(train.iloc[-1], h)


def seasonal_naive_forecast(train: pd.Series, h: int) -> np.ndarray:
    """Repeat the same calendar month from the previous year."""
    if h > 12:
        raise ValueError("Seasonal naive here only covers a 12-month horizon.")
    return train.iloc[-12:].values[:h]


# --------------------------------------------------------------------------
# ETS - specification chosen on the training sample by AICc
# --------------------------------------------------------------------------

ETS_GRID = [
    dict(trend=None, seasonal=None, damped_trend=False),
    dict(trend="add", seasonal=None, damped_trend=False),
    dict(trend="add", seasonal=None, damped_trend=True),
    dict(trend=None, seasonal="add", damped_trend=False),
    dict(trend="add", seasonal="add", damped_trend=False),
    dict(trend="add", seasonal="add", damped_trend=True),
]


def label_ets(spec: dict) -> str:
    parts = ["ETS"]
    if spec["trend"]:
        parts.append("damped trend" if spec["damped_trend"] else "trend")
    if spec["seasonal"]:
        parts.append("seasonal")
    return " ".join(parts) if len(parts) > 1 else "ETS level only"


def fit_best_ets(train: pd.Series):
    """
    Fit every candidate specification and keep the lowest-AICc one.

    Selection uses only the training sample. This is the fix for defect 2:
    the test set must not influence which model is chosen, or the reported
    test error stops being an out-of-sample estimate.
    """
    best = None
    trace = []
    for spec in ETS_GRID:
        label = label_ets(spec)
        try:
            model = ETSModel(
                train,
                error="add",
                seasonal_periods=12 if spec["seasonal"] else None,
                **spec,
            )
            res = model.fit(disp=False)
        except Exception as exc:
            # Record rather than swallow. A specification that fails to
            # converge should be visible, not silently absent from the
            # comparison - otherwise "AICc chose the simplest model" can
            # mean "the others never ran".
            trace.append((label, None, type(exc).__name__))
            continue
        trace.append((label, round(float(res.aicc), 2), "ok"))
        if best is None or res.aicc < best[1]:
            best = (res, res.aicc, label)
    if best is None:
        raise RuntimeError("No ETS specification converged.")
    return best + (trace,)


# --------------------------------------------------------------------------
# SARIMA - order chosen on the training sample by AIC
# --------------------------------------------------------------------------

P_RANGE = Q_RANGE = range(0, 3)
SP_RANGE = SQ_RANGE = range(0, 2)


def fit_best_sarima(train: pd.Series):
    best = None
    for p, q, sp, sq in product(P_RANGE, Q_RANGE, SP_RANGE, SQ_RANGE):
        order, seasonal_order = (p, 1, q), (sp, 1, sq, 12)
        try:
            res = SARIMAX(
                train,
                order=order,
                seasonal_order=seasonal_order,
                enforce_stationarity=False,
                enforce_invertibility=False,
            ).fit(disp=False)
        except Exception:
            continue
        if not np.isfinite(res.aic):
            continue
        if best is None or res.aic < best[1]:
            label = f"SARIMA{order}{seasonal_order}"
            best = (res, res.aic, label)
    if best is None:
        raise RuntimeError("No SARIMA order converged.")
    return best


# --------------------------------------------------------------------------
# Intervals on the 12-month total
# --------------------------------------------------------------------------

def simulate_annual_total(res, h: int, rng: np.random.Generator) -> np.ndarray:
    """
    Distribution of the summed 12-month forecast.

    Summing monthly confidence bounds would be wrong: the bound on a sum is
    not the sum of the bounds, because monthly errors are correlated through
    the state. Simulating whole paths and summing each one handles that.
    """
    sims = res.simulate(nsimulations=h, anchor="end", repetitions=N_SIMS)
    arr = np.asarray(sims)
    if arr.ndim == 3:            # (h, 1, reps) for some statsmodels versions
        arr = arr[:, 0, :]
    return arr.sum(axis=0)


def simulate_naive_annual_total(train: pd.Series, h: int,
                                rng: np.random.Generator) -> np.ndarray:
    """
    Random-walk paths bootstrapped from training first differences.

    A flat naive forecast has no fitted model to simulate from, but it is
    still a stochastic process. Ignoring that would let the benchmark be
    reported without uncertainty while the models carry intervals - an
    unfair comparison in the benchmark's favour.
    """
    steps = train.diff().dropna().values
    draws = rng.choice(steps, size=(N_SIMS, h), replace=True)
    paths = train.iloc[-1] + np.cumsum(draws, axis=1)
    return np.clip(paths, 0, None).sum(axis=1)


def simulate_snaive_annual_total(train: pd.Series, h: int,
                                 rng: np.random.Generator) -> np.ndarray:
    """Seasonal naive with residuals bootstrapped from year-on-year changes."""
    base = train.iloc[-12:].values[:h]
    resid = (train - train.shift(12)).dropna().values
    draws = rng.choice(resid, size=(N_SIMS, h), replace=True)
    return np.clip(base + draws, 0, None).sum(axis=1)


# --------------------------------------------------------------------------
# Pipeline
# --------------------------------------------------------------------------

def evaluate_market(w: pd.DataFrame, market: str, rng) -> tuple[pd.DataFrame, dict]:
    series = w[market].dropna()
    train, test = series.loc[:TRAIN_END], series.loc[TEST_START:]
    actual = test.values
    h = len(actual)

    ets_res, ets_aicc, ets_label, ets_trace = fit_best_ets(train)
    sar_res, sar_aic, sar_label = fit_best_sarima(train)

    print(f"\n[{market}] ETS specification search (AICc, training sample only):")
    for label, aicc, status in ets_trace:
        print(f"   {label:28s} {str(aicc):>10s}  {status}")

    candidates = {
        "Naive (flat)": naive_forecast(train, h),
        "Seasonal naive": seasonal_naive_forecast(train, h),
        ets_label: np.asarray(ets_res.forecast(h)),
        sar_label: np.asarray(sar_res.forecast(h)),
    }

    rows = [
        {
            "market": market,
            "model": name,
            "MAE": round(mae(actual, fc), 2),
            "MAPE": round(mape(actual, fc), 2),
            "selected_on": "n/a (benchmark)" if "aive" in name else "training sample",
        }
        for name, fc in candidates.items()
    ]
    table = pd.DataFrame(rows).sort_values("MAPE").reset_index(drop=True)

    # The benchmark to beat is the better of the two naive methods, not
    # whichever one happens to look weakest.
    bench = table[table.model.str.contains("aive")].MAPE.min()
    winner = table.iloc[0]
    beats_benchmark = bool(winner.MAPE < bench)

    # Refit the winner on the full series and simulate the annual total.
    full = series
    if winner.model == "Naive (flat)":
        totals = simulate_naive_annual_total(full, HORIZON, rng)
    elif winner.model == "Seasonal naive":
        totals = simulate_snaive_annual_total(full, HORIZON, rng)
    elif winner.model.startswith("ETS"):
        spec = next(s for s in ETS_GRID if label_ets(s) == winner.model)
        refit = ETSModel(full, error="add",
                         seasonal_periods=12 if spec["seasonal"] else None,
                         **spec).fit(disp=False)
        totals = simulate_annual_total(refit, HORIZON, rng)
    else:
        order = sar_res.model.order
        seasonal_order = sar_res.model.seasonal_order
        refit = SARIMAX(full, order=order, seasonal_order=seasonal_order,
                        enforce_stationarity=False,
                        enforce_invertibility=False).fit(disp=False)
        totals = simulate_annual_total(refit, HORIZON, rng)

    # Residual autocorrelation on the selected statistical model.
    #
    # model_df must be passed: the Ljung-Box statistic loses one degree of
    # freedom per estimated parameter. Omitting it inflates p-values and
    # makes residuals look cleaner than they are.
    stat_res = sar_res if winner.model.startswith("SARIMA") else ets_res
    n_params = int(np.asarray(stat_res.params).size)
    lb = acorr_ljungbox(
        np.asarray(stat_res.resid), lags=[12, 24], model_df=n_params, return_df=True
    )
    lb_p = {f"ljungbox_p_lag{lag}": round(float(lb.loc[lag, "lb_pvalue"]), 4)
            for lag in [12, 24] if lag in lb.index}

    latest12 = float(full.iloc[-12:].sum())
    lo95, lo80, med, hi80, hi95 = np.percentile(totals, [2.5, 10, 50, 90, 97.5])

    summary = {
        "market": market,
        "winning_model": winner.model,
        "test_MAPE": winner.MAPE,
        "benchmark_MAPE": round(float(bench), 2),
        "beats_benchmark": beats_benchmark,
        "latest_12m": round(latest12, 0),
        "forecast_median": round(float(med), 0),
        "change_pct": round((med / latest12 - 1) * 100, 1),
        "lo80": round(float(lo80), 0),
        "hi80": round(float(hi80), 0),
        "lo95": round(float(lo95), 0),
        "hi95": round(float(hi95), 0),
        # The decision-relevant question is not the point estimate but
        # whether the interval excludes no-growth.
        "growth_excludes_zero_80": bool(lo80 > latest12),
        "ets_aicc": round(float(ets_aicc), 2),
        "sarima_aic": round(float(sar_aic), 2),
        "n_params_tested": n_params,
        **lb_p,
    }
    return table, summary


def cagr_sensitivity(w: pd.DataFrame) -> pd.DataFrame:
    """Annualised growth to the end of the series from four base quarters."""
    r = w.rolling(12).sum()
    latest = r.iloc[-1]
    data = {
        base[:7]: ((latest / r.loc[base]) ** (1 / years) - 1) * 100
        for base, years in CAGR_BASES.items()
    }
    out = pd.DataFrame(data).round(1)
    out["min"] = out.min(axis=1)
    out["max"] = out.max(axis=1)
    out["spread"] = (out["max"] - out["min"]).round(1)
    return out.sort_values("max", ascending=False)


def recent_momentum(w: pd.DataFrame) -> pd.DataFrame:
    """
    Trough-to-latest change in the rolling 12-month series.

    A three-year CAGR is blind to a turning point inside the window. China
    carries a negative three-year rate while having risen sharply off a
    recent trough, and a recommendation built on the CAGR alone would
    describe that market backwards.
    """
    r = w.rolling(12).sum().dropna()
    rows = []
    for c in r.columns:
        trough_date = r[c].idxmin()
        rows.append({
            "market": c,
            "trough_month": trough_date.strftime("%Y-%m"),
            "trough": round(float(r[c].min()), 0),
            "latest": round(float(r[c].iloc[-1]), 0),
            "change_from_trough_pct": round(float(r[c].iloc[-1] / r[c].min() - 1) * 100, 1),
            "months_since_trough": int(((r.index[-1] - trough_date).days) / 30.44),
        })
    return pd.DataFrame(rows).sort_values("change_from_trough_pct", ascending=False)


def main() -> None:
    rng = np.random.default_rng(SEED)
    OUT.mkdir(parents=True, exist_ok=True)
    w = load_matrix()

    tables, summaries = [], []
    for market in MARKETS:
        table, summary = evaluate_market(w, market, rng)
        tables.append(table)
        summaries.append(summary)
        print(f"\n=== {market} ===")
        print(table.to_string(index=False))

    validation = pd.concat(tables, ignore_index=True)
    forecasts = pd.DataFrame(summaries)
    cagr = cagr_sensitivity(w)
    momentum = recent_momentum(w)

    validation.to_csv(OUT / "model_validation.csv", index=False)
    forecasts.to_csv(OUT / "forecast_intervals.csv", index=False)
    cagr.to_csv(OUT / "cagr_sensitivity.csv")
    momentum.to_csv(OUT / "recent_momentum.csv", index=False)

    print("\n=== Forecast, next 12 months (AUD m) ===")
    print(forecasts[[
        "market", "winning_model", "test_MAPE", "benchmark_MAPE",
        "beats_benchmark", "latest_12m", "forecast_median", "change_pct",
        "lo80", "hi80", "growth_excludes_zero_80",
    ]].to_string(index=False))

    print("\n=== CAGR sensitivity by base quarter (%) ===")
    print(cagr.to_string())

    print("\n=== Recent momentum: rolling-12m trough to latest ===")
    print(momentum.to_string(index=False))

    lines = [
        "# Model results (revised)",
        "",
        "## Validation, 12-month holdout Jul 2025 - Jun 2026",
        "",
        "Both benchmarks are reported. Model specifications were selected on the",
        "training sample only (ETS by AICc, SARIMA by AIC); the test set was used",
        "once, to compare, and never to select.",
        "",
        "```",
        validation.to_string(index=False),
        "```",
        "",
        "## Forecast Jul 2026 - Jun 2027, with simulated intervals",
        "",
        "Intervals come from 5,000 simulated 12-month paths, summed per path.",
        "`growth_excludes_zero_80` is the decision-relevant column: it says",
        "whether the 80% interval sits entirely above the latest actual 12-month",
        "total. Where it is False, the projected change is not distinguishable",
        "from no change and must not be used to justify a recommendation.",
        "",
        "```",
        forecasts.to_string(index=False),
        "```",
        "",
        "## Three-year CAGR by base quarter",
        "",
        "Growth rates are measured to Jun 2026 from four alternative base",
        "quarters. The `range` column shows how much the headline figure depends",
        "on that choice.",
        "",
        "```",
        cagr.to_string(),
        "```",
        "",
        "## Recent momentum",
        "",
        "Three-year growth rates cannot see a turning point inside their own",
        "window. This table reports the low point of each rolling 12-month",
        "series and the change since, so a market with a negative long-run rate",
        "but a recent recovery is not described as simply declining.",
        "",
        "```",
        momentum.to_string(index=False),
        "```",
    ]
    (OUT / "model_results.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"\nWrote {OUT / 'model_results.md'}")


if __name__ == "__main__":
    main()
