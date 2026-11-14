# Live trades: trading project around energy around the 2026 elections

As of 2026-11-13. Strategy: agree rule, holding baskets, rebalanced on the first
trading day of each week; models trained on data through 2026-10-16; contest 2026-10-19 to 2026-11-20.

## Latest decision

**2026-11-13: NO_TRADE** - mid-week, holding until the next weekly rebalance; today's signal: model and momentum agree on XLE

## Holdings

| ticker | shares | value |
| --- | --- | --- |
| COP | 86.33 | 1.228e+04 |
| CVX | 55.08 | 1.211e+04 |
| EOG | 78.21 | 1.238e+04 |
| HAL | 364.2 | 1.23e+04 |
| OXY | 208.2 | 1.223e+04 |
| SLB | 230.4 | 1.191e+04 |
| VLO | 32.54 | 1.236e+04 |
| XOM | 70.47 | 1.202e+04 |


## Returns since 2026-10-19

| series | return | max_drawdown | last_value |
| --- | --- | --- | --- |
| portfolio | -0.02401 | -0.1116 | 9.76e+04 |
| both baskets 50/50 | 0.00854 | -0.03222 | 1.009e+05 |
| XLE/ICLN 50/50 | -0.03478 | -0.05864 | 9.652e+04 |
| SPY | -0.0158 | -0.05186 | 9.842e+04 |


## Threads to follow

### Election week runup

Did energy run up into election day (Nov 3) and go flat after, as it did in the past midterms (about +3-4% over the 20 trading days into election day)? Did clean or traditional react more?

| series | into_election | after_election |
| --- | --- | --- |
| portfolio | -0.008879 | -0.01526 |
| both baskets 50/50 | 0.03361 | -0.02426 |
| XLE/ICLN 50/50 | -0.01287 | -0.0222 |
| SPY | -0.01583 | 2.654e-05 |
| XLE | -0.01652 | -0.02579 |
| ICLN | -0.009225 | -0.01862 |
| XLE basket | -0.008642 | -0.01493 |
| ICLN basket | 0.07815 | -0.03116 |

### Model vs. momentum agreement

How often did the two agree, and was the model right more often when they did?

| measure | live | backtest |
| --- | --- | --- |
| weeks | 4 |  |
| share of weeks the two agree | 1 | 0.63 |
| model right when they agree | 0.5 | 0.57 |
| model right when they disagree |  | 0.5 |
| momentum right overall | 0.5 |  |

| week_of | model_side | momentum_side | agree | better_side | XLE_return | ICLN_return | model_right | momentum_right | complete |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-10-19 | XLE | XLE | True | XLE | 0.03904 | -0.01037 | True | True | True |
| 2026-10-26 | XLE | XLE | True | ICLN | -0.03811 | 0.0599 | False | False | True |
| 2026-11-02 | XLE | XLE | True | ICLN | -0.07032 | 0.0642 | False | False | True |
| 2026-11-09 | XLE | XLE | True | XLE | 0.05101 | -0.06423 | True | True | True |

### Baskets vs ETFs

How far did each stock basket drift from its ETF?

| side | etf_return | basket_return | basket_minus_etf | daily_corr | backtest_corr |
| --- | --- | --- | --- | --- | --- |
| XLE | -0.04189 | -0.02344 | 0.01844 | 0.9888 |  |
| ICLN | -0.02768 | 0.04455 | 0.07223 | 0.8623 | 0.82 |

### Regime shifts

Did a 12-month regime flip, or did the momentum side change? Momentum side changed on: no day yet.

| date | market_up_12m | energy_beats_market_12m | clean_beats_traditional_12m | momentum_side | momentum_side_changed |
| --- | --- | --- | --- | --- | --- |
| 2026-10-19 00:00:00 | True | True | False | XLE | False |
| 2026-11-13 00:00:00 | True | True | False | XLE | False |

### Live vs backtest range

Is the excess return inside the range the backtest expects?

| measure | value |
| --- | --- |
| excess over both baskets so far | -0.03227 |
| backtest: mean 24-day excess | 0.0056 |
| backtest: 10th percentile | -0.0396 |
| backtest: 90th percentile | 0.0469 |
| backtest: share of 24-day windows positive | 0.57 |
| backtest: mean excess in past Oct 19-Nov 20 windows (beat in 11 of 16) | 0.0142 |


## Every decision

| date | p_XLE | p_ICLN | model_side | momentum_side | target_XLE | target_ICLN | equity_est | action | reason | n_orders | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-11-13 | 0.6635 | 0.5476 | XLE | XLE | 1 | 0 | 9.76e+04 | NO_TRADE | mid-week, holding until the next weekly rebalance; today's signal: model and momentum agree on XLE | 0 | backfill |
| 2026-11-12 | 0.6579 | 0.5403 | XLE | XLE | 1 | 0 | 9.617e+04 | NO_TRADE | mid-week, holding until the next weekly rebalance; today's signal: model and momentum agree on XLE | 0 | backfill |
| 2026-11-11 | 0.6467 | 0.5748 | XLE | XLE | 1 | 0 | 9.491e+04 | NO_TRADE | mid-week, holding until the next weekly rebalance; today's signal: model and momentum agree on XLE | 0 | backfill |
| 2026-11-10 | 0.6653 | 0.5923 | XLE | XLE | 1 | 0 | 9.314e+04 | NO_TRADE | mid-week, holding until the next weekly rebalance; today's signal: model and momentum agree on XLE | 0 | backfill |
| 2026-11-09 | 0.6904 | 0.5945 | XLE | XLE | 1 | 0 | 9.287e+04 | TRADE | model and momentum agree on XLE | 8 | backfill |
| 2026-11-06 | 0.6734 | 0.6029 | XLE | XLE | 1 | 0 | 9.277e+04 | NO_TRADE | mid-week, holding until the next weekly rebalance; today's signal: model and momentum agree on XLE | 0 | backfill |
| 2026-11-05 | 0.6588 | 0.5938 | XLE | XLE | 1 | 0 | 9.262e+04 | NO_TRADE | mid-week, holding until the next weekly rebalance; today's signal: model and momentum agree on XLE | 0 | backfill |
| 2026-11-04 | 0.6509 | 0.5146 | XLE | XLE | 1 | 0 | 9.492e+04 | NO_TRADE | mid-week, holding until the next weekly rebalance; today's signal: model and momentum agree on XLE | 0 | backfill |
| 2026-11-03 | 0.6525 | 0.4842 | XLE | XLE | 1 | 0 | 9.911e+04 | NO_TRADE | mid-week, holding until the next weekly rebalance; today's signal: model and momentum agree on XLE | 0 | backfill |
| 2026-11-02 | 0.6413 | 0.4947 | XLE | XLE | 1 | 0 | 9.992e+04 | TRADE | model and momentum agree on XLE | 8 | backfill |
| 2026-10-30 | 0.6538 | 0.501 | XLE | XLE | 1 | 0 | 1.043e+05 | NO_TRADE | mid-week, holding until the next weekly rebalance; today's signal: model and momentum agree on XLE | 0 | backfill |
| 2026-10-29 | 0.6778 | 0.5048 | XLE | XLE | 1 | 0 | 1.024e+05 | NO_TRADE | mid-week, holding until the next weekly rebalance; today's signal: model and momentum agree on XLE | 0 | backfill |
| 2026-10-28 | 0.6536 | 0.5252 | XLE | XLE | 1 | 0 | 1.02e+05 | NO_TRADE | mid-week, holding until the next weekly rebalance; today's signal: model and momentum agree on XLE | 0 | backfill |
| 2026-10-27 | 0.6334 | 0.5149 | XLE | XLE | 1 | 0 | 1.017e+05 | NO_TRADE | mid-week, holding until the next weekly rebalance; today's signal: model and momentum agree on XLE | 0 | backfill |
| 2026-10-26 | 0.6416 | 0.5606 | XLE | XLE | 1 | 0 | 1.039e+05 | TRADE | model and momentum agree on XLE | 8 | backfill |
| 2026-10-23 | 0.6083 | 0.5448 | XLE | XLE | 1 | 0 | 1.034e+05 | NO_TRADE | mid-week, holding until the next weekly rebalance; today's signal: model and momentum agree on XLE | 0 | backfill |
| 2026-10-22 | 0.6425 | 0.5634 | XLE | XLE | 1 | 0 | 1.001e+05 | NO_TRADE | mid-week, holding until the next weekly rebalance; today's signal: model and momentum agree on XLE | 0 | backfill |
| 2026-10-21 | 0.6055 | 0.5231 | XLE | XLE | 1 | 0 | 1.012e+05 | NO_TRADE | mid-week, holding until the next weekly rebalance; today's signal: model and momentum agree on XLE | 0 | backfill |
| 2026-10-20 | 0.6336 | 0.4802 | XLE | XLE | 1 | 0 | 1.006e+05 | NO_TRADE | mid-week, holding until the next weekly rebalance; today's signal: model and momentum agree on XLE | 0 | backfill |
| 2026-10-19 | 0.6169 | 0.4382 | XLE | XLE | 1 | 0 | 1e+05 | TRADE | model and momentum agree on XLE | 8 | backfill |


## Every trade

| ticker | side | shares | price | dollars | date | fill_price | mode |
| --- | --- | --- | --- | --- | --- | --- | --- |
| HAL | BUY | 3.276 | 31.88 | 104.4 | 2026-11-09 | 31.88 | backfill |
| OXY | BUY | 2.502 | 55.76 | 139.5 | 2026-11-09 | 55.76 | backfill |
| COP | BUY | 1.275 | 134.5 | 171.4 | 2026-11-09 | 134.5 | backfill |
| CVX | BUY | 0.2415 | 210.8 | 50.9 | 2026-11-09 | 210.8 | backfill |
| XOM | BUY | 0.958 | 164.7 | 157.8 | 2026-11-09 | 164.7 | backfill |
| VLO | SELL | 0.2009 | 356.8 | 71.67 | 2026-11-09 | 356.8 | backfill |
| SLB | SELL | 8.335 | 50.38 | 419.9 | 2026-11-09 | 50.38 | backfill |
| EOG | SELL | 0.8922 | 148.4 | 132.4 | 2026-11-09 | 148.4 | backfill |
| VLO | BUY | 2.31 | 381.5 | 881.3 | 2026-11-02 | 381.5 | backfill |
| OXY | BUY | 2.994 | 60.72 | 181.8 | 2026-11-02 | 60.72 | backfill |
| HAL | SELL | 5.58 | 34.61 | 193.1 | 2026-11-02 | 34.61 | backfill |
| SLB | SELL | 5.905 | 52.31 | 308.9 | 2026-11-02 | 52.31 | backfill |
| EOG | SELL | 0.2399 | 157.9 | 37.88 | 2026-11-02 | 157.9 | backfill |
| COP | SELL | 0.7397 | 146.8 | 108.6 | 2026-11-02 | 146.8 | backfill |
| CVX | SELL | 1.141 | 227.8 | 260 | 2026-11-02 | 227.8 | backfill |
| XOM | SELL | 0.8602 | 179.7 | 154.6 | 2026-11-02 | 179.7 | backfill |
| VLO | BUY | 1.585 | 426.8 | 676.3 | 2026-10-26 | 426.8 | backfill |
| EOG | BUY | 0.0563 | 163.7 | 9.215 | 2026-10-26 | 163.7 | backfill |
| OXY | BUY | 3.407 | 64.07 | 218.3 | 2026-10-26 | 64.07 | backfill |
| CVX | BUY | 0.266 | 232 | 61.71 | 2026-10-26 | 232 | backfill |
| XOM | BUY | 0.2624 | 184.5 | 48.42 | 2026-10-26 | 184.5 | backfill |
| HAL | SELL | 12.56 | 35.44 | 445 | 2026-10-26 | 35.44 | backfill |
| SLB | SELL | 9.96 | 53.08 | 528.7 | 2026-10-26 | 53.08 | backfill |
| COP | SELL | 0.2658 | 151.4 | 40.23 | 2026-10-26 | 151.4 | backfill |
| VLO | BUY | 28.85 | 433.3 | 1.25e+04 | 2026-10-19 | 433.3 | backfill |
| HAL | BUY | 379 | 32.98 | 1.25e+04 | 2026-10-19 | 32.98 | backfill |
| SLB | BUY | 254.6 | 49.09 | 1.25e+04 | 2026-10-19 | 49.09 | backfill |
| EOG | BUY | 79.29 | 157.6 | 1.25e+04 | 2026-10-19 | 157.6 | backfill |
| OXY | BUY | 199.3 | 62.72 | 1.25e+04 | 2026-10-19 | 62.72 | backfill |
| COP | BUY | 86.06 | 145.2 | 1.25e+04 | 2026-10-19 | 145.2 | backfill |
| CVX | BUY | 55.71 | 224.4 | 1.25e+04 | 2026-10-19 | 224.4 | backfill |
| XOM | BUY | 70.11 | 178.3 | 1.25e+04 | 2026-10-19 | 178.3 | backfill |


