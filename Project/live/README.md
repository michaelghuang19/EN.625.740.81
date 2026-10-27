# Live trades: trading project around energy around the 2026 elections

As of 2026-10-27. Strategy: agree rule, holding baskets, rebalanced on the first
trading day of each week; models trained on data through 2026-10-16; contest 2026-10-19 to 2026-11-20.

## Latest decision

**2026-10-26: TRADE** - model and momentum agree on XLE

## Holdings

| ticker | shares | value |
| --- | --- | --- |
| COP | 85.8 | 1.269e+04 |
| CVX | 55.98 | 1.278e+04 |
| EOG | 79.35 | 1.278e+04 |
| HAL | 366.5 | 1.305e+04 |
| OXY | 202.7 | 1.272e+04 |
| SLB | 244.7 | 1.323e+04 |
| VLO | 30.43 | 1.179e+04 |
| XOM | 70.38 | 1.266e+04 |


## Returns since 2026-10-19

| series | return | max_drawdown | last_value |
| --- | --- | --- | --- |
| portfolio | 0.01703 | -0.02113 | 1.017e+05 |
| both baskets 50/50 | 0.02775 | -0.0117 | 1.028e+05 |
| XLE/ICLN 50/50 | -0.009277 | -0.01912 | 9.907e+04 |
| SPY | 0.004149 | -0.01697 | 1.004e+05 |


## Threads to follow

### Election week runup

Did energy run up into election day (Nov 3) and go flat after, as it did in the past midterms (about +3-4% over the 20 trading days into election day)? Did clean or traditional react more?

| series | into_election | after_election |
| --- | --- | --- |
| portfolio | 0.01703 |  |
| both baskets 50/50 | 0.02775 |  |
| XLE/ICLN 50/50 | -0.009277 |  |
| SPY | 0.004149 |  |
| XLE | 0.006047 |  |
| ICLN | -0.0246 |  |
| XLE basket | 0.01709 |  |
| ICLN basket | 0.03895 |  |

### Model vs. momentum agreement

How often did the two agree, and was the model right more often when they did?

| measure | live | backtest |
| --- | --- | --- |
| weeks | 2 |  |
| share of weeks the two agree | 1 | 0.63 |
| model right when they agree | 0.5 | 0.57 |
| model right when they disagree |  | 0.5 |
| momentum right overall | 0.5 |  |

| week_of | model_side | momentum_side | agree | better_side | XLE_return | ICLN_return | model_right | momentum_right | complete |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-10-19 | XLE | XLE | True | XLE | 0.03904 | -0.01037 | True | True | True |
| 2026-10-26 | XLE | XLE | True | ICLN | -0.02113 | 0.04983 | False | False | False |

### Baskets vs ETFs

How far did each stock basket drift from its ETF?

| side | etf_return | basket_return | basket_minus_etf | daily_corr | backtest_corr |
| --- | --- | --- | --- | --- | --- |
| XLE | 0.006047 | 0.01709 | 0.01104 | 0.997 |  |
| ICLN | -0.0246 | 0.03895 | 0.06355 | 0.892 | 0.82 |

### Regime shifts

Did a 12-month regime flip, or did the momentum side change? Momentum side changed on: 2026-10-27.

| date | market_up_12m | energy_beats_market_12m | clean_beats_traditional_12m | momentum_side | momentum_side_changed |
| --- | --- | --- | --- | --- | --- |
| 2026-10-19 00:00:00 | True | True | False | XLE | False |
| 2026-10-27 00:00:00 | True | True | False |  | True |

### Live vs backtest range

Is the excess return inside the range the backtest expects?

| measure | value |
| --- | --- |
| excess over both baskets so far | -0.01042 |
| backtest: mean 24-day excess | 0.0056 |
| backtest: 10th percentile | -0.0396 |
| backtest: 90th percentile | 0.0469 |
| backtest: share of 24-day windows positive | 0.57 |
| backtest: mean excess in past Oct 19-Nov 20 windows (beat in 11 of 16) | 0.0142 |


## Every decision

| date | p_XLE | p_ICLN | model_side | momentum_side | target_XLE | target_ICLN | equity_est | action | reason | n_orders | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-10-26 | 0.6416 | 0.5606 | XLE | XLE | 1 | 0 | 1.039e+05 | TRADE | model and momentum agree on XLE | 8 | backfill |
| 2026-10-23 | 0.6083 | 0.5448 | XLE | XLE | 1 | 0 | 1.034e+05 | NO_TRADE | mid-week, holding until the next weekly rebalance; today's signal: model and momentum agree on XLE | 0 | backfill |
| 2026-10-22 | 0.6425 | 0.5634 | XLE | XLE | 1 | 0 | 1.001e+05 | NO_TRADE | mid-week, holding until the next weekly rebalance; today's signal: model and momentum agree on XLE | 0 | backfill |
| 2026-10-21 | 0.6055 | 0.5231 | XLE | XLE | 1 | 0 | 1.012e+05 | NO_TRADE | mid-week, holding until the next weekly rebalance; today's signal: model and momentum agree on XLE | 0 | backfill |
| 2026-10-20 | 0.6336 | 0.4802 | XLE | XLE | 1 | 0 | 1.006e+05 | NO_TRADE | mid-week, holding until the next weekly rebalance; today's signal: model and momentum agree on XLE | 0 | backfill |
| 2026-10-19 | 0.6169 | 0.4382 | XLE | XLE | 1 | 0 | 1e+05 | TRADE | model and momentum agree on XLE | 8 | backfill |


## Every trade

| ticker | side | shares | price | dollars | date | fill_price | mode |
| --- | --- | --- | --- | --- | --- | --- | --- |
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


