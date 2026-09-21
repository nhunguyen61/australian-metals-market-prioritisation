# Model results (revised)

## Validation, 12-month holdout Jul 2025 - Jun 2026

Both benchmarks are reported. Model specifications were selected on the
training sample only (ETS by AICc, SARIMA by AIC); the test set was used
once, to compare, and never to select.

```
  market                        model   MAE  MAPE     selected_on
 Vietnam SARIMA(0, 1, 2)(0, 1, 1, 12) 19.77 14.13 training sample
 Vietnam                 Naive (flat) 23.84 16.72 n/a (benchmark)
 Vietnam                 ETS seasonal 25.92 18.19 training sample
 Vietnam               Seasonal naive 24.32 18.49 n/a (benchmark)
Thailand SARIMA(1, 1, 2)(0, 1, 1, 12) 16.79 15.59 training sample
Thailand               ETS level only 17.98 17.43 training sample
Thailand               Seasonal naive 25.99 21.11 n/a (benchmark)
Thailand                 Naive (flat) 65.94 58.97 n/a (benchmark)
Malaysia                 Naive (flat) 21.63 12.08 n/a (benchmark)
Malaysia               ETS level only 27.47 13.88 training sample
Malaysia SARIMA(0, 1, 2)(0, 1, 1, 12) 38.62 19.82 training sample
Malaysia               Seasonal naive 53.66 28.00 n/a (benchmark)
```

## Forecast Jul 2026 - Jun 2027, with simulated intervals

Intervals come from 5,000 simulated 12-month paths, summed per path.
`growth_excludes_zero_80` is the decision-relevant column: it says
whether the 80% interval sits entirely above the latest actual 12-month
total. Where it is False, the projected change is not distinguishable
from no change and must not be used to justify a recommendation.

```
  market                winning_model  test_MAPE  benchmark_MAPE  beats_benchmark  latest_12m  forecast_median  change_pct   lo80   hi80   lo95   hi95  growth_excludes_zero_80  ets_aicc  sarima_aic  n_params_tested  ljungbox_p_lag12  ljungbox_p_lag24
 Vietnam SARIMA(0, 1, 2)(0, 1, 1, 12)      14.13           16.72             True      1676.0           1940.0        15.8 1654.0 2227.0 1505.0 2372.0                    False   1033.73      815.66                4            0.3030            0.4048
Thailand SARIMA(1, 1, 2)(0, 1, 1, 12)      15.59           21.11             True      1411.0           1518.0         7.5 1298.0 1735.0 1187.0 1857.0                    False   1093.25      874.35                5            0.4548            0.5670
Malaysia               ETS level only      13.88           12.08            False      2173.0           2072.0        -4.7 1464.0 2700.0 1120.0 3009.0                    False   1245.55      976.18                2            0.0011            0.0097
```

## Three-year CAGR by base quarter

Growth rates are measured to Jun 2026 from four alternative base
quarters. The `range` column shows how much the headline figure depends
on that choice.

```
             2023-03  2023-06  2023-09  2023-12   min   max  spread
country                                                            
India           16.1     34.1     34.4     39.2  16.1  39.2    23.1
Vietnam         27.7     33.2     33.1     32.2  27.7  33.2     5.5
Thailand        11.2     14.9     18.0     26.1  11.2  26.1    14.9
Japan            7.8     10.0     14.9     16.5   7.8  16.5     8.7
Malaysia        10.3     12.0     11.7     15.0  10.3  15.0     4.7
Taiwan           1.5      8.4      8.3     12.9   1.5  12.9    11.4
South Korea     -0.1     -3.6     -4.9     -6.2  -6.2  -0.1     6.1
China           -5.1     -8.1    -12.6    -15.1 -15.1  -5.1    10.0
```

## Recent momentum

Three-year growth rates cannot see a turning point inside their own
window. This table reports the low point of each rolling 12-month
series and the change since, so a market with a negative long-run rate
but a recent recovery is not described as simply declining.

```
     market trough_month  trough  latest  change_from_trough_pct  months_since_trough
      India      2024-06    56.0   193.0                   243.3                   23
    Vietnam      2015-12   536.0  1676.0                   212.5                  125
   Malaysia      2016-02   768.0  2173.0                   182.9                  123
South Korea      2017-12   702.0  1840.0                   162.1                  101
      Japan      2016-06   743.0  1817.0                   144.6                  119
   Thailand      2015-12   581.0  1412.0                   142.8                  125
     Taiwan      2016-01   634.0  1475.0                   132.5                  124
      China      2026-01  1529.0  1999.0                    30.7                    4
```