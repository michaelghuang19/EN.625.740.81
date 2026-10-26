# Live trades: trading project around energy around the 2026 elections

As of 2026-10-26. Strategy: agree rule, holding baskets, rebalanced on the first
trading day of each week; models trained on data through 2026-10-16; contest 2026-10-19 to 2026-11-20.

## Latest decision

**2026-10-23: NO_TRADE** - mid-week, holding until the next weekly rebalance; today's signal: model and momentum agree on XLE

## Holdings

| ticker | shares | value |
| --- | --- | --- |
| COP | 86.06 | 1.302e+04 |
| CVX | 55.71 | 1.294e+04 |
| EOG | 79.29 | 1.294e+04 |
| HAL | 379 | 1.331e+04 |
| OXY | 199.3 | 1.278e+04 |
| SLB | 254.6 | 1.325e+04 |
| VLO | 28.85 | 1.227e+04 |
| XOM | 70.11 | 1.289e+04 |


## Returns since 2026-10-19

| series | return | max_drawdown | last_value |
| --- | --- | --- | --- |
| portfolio | 0.03397 | -0.01021 | 1.034e+05 |
| both baskets 50/50 | 0.01381 | -0.0117 | 1.014e+05 |
| XLE/ICLN 50/50 | -0.01002 | -0.01985 | 9.9e+04 |
| SPY | -0.001552 | -0.01697 | 9.984e+04 |


## Threads to follow

### Election week runup

Did energy run up into election day (Nov 3) and go flat after, as it did in the past midterms (about +3-4% over the 20 trading days into election day)? Did clean or traditional react more?

| series | into_election | after_election |
| --- | --- | --- |
| portfolio | 0.03397 |  |
| both baskets 50/50 | 0.01381 |  |
| XLE/ICLN 50/50 | -0.01002 |  |
| SPY | -0.001552 |  |
| XLE | 0.02456 |  |
| ICLN | -0.04459 |  |
| XLE basket | 0.03414 |  |
| ICLN basket | -0.006377 |  |

### Model vs. momentum agreement

How often did the two agree, and was the model right more often when they did?

| measure | live | backtest |
| --- | --- | --- |
| weeks | 1 |  |
| share of weeks the two agree | 1 | 0.63 |
| model right when they agree | 1 | 0.57 |
| model right when they disagree |  | 0.5 |
| momentum right overall | 1 |  |

| week_of | model_side | momentum_side | agree | better_side | XLE_return | ICLN_return | model_right | momentum_right | complete |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-10-19 | XLE | XLE | True | XLE | 0.03414 | -0.006377 | True | True | True |

### Baskets vs ETFs

How far did each stock basket drift from its ETF?

| side | etf_return | basket_return | basket_minus_etf | daily_corr | backtest_corr |
| --- | --- | --- | --- | --- | --- |
| XLE | 0.02456 | 0.03414 | 0.009584 | 0.9924 |  |
| ICLN | -0.04459 | -0.006377 | 0.03821 | 0.9121 | 0.82 |

### Regime shifts

Did a 12-month regime flip, or did the momentum side change? Momentum side changed on: 2026-10-26.

| date | market_up_12m | energy_beats_market_12m | clean_beats_traditional_12m | momentum_side | momentum_side_changed |
| --- | --- | --- | --- | --- | --- |
| 2026-10-19 00:00:00 | True | True | False | XLE | False |
| 2026-10-26 00:00:00 | True | True | False |  | True |

### Live vs backtest range

Is the excess return inside the range the backtest expects?

| measure | value |
| --- | --- |
| excess over both baskets so far | 0.01989 |
| backtest: mean 24-day excess | 0.0056 |
| backtest: 10th percentile | -0.0396 |
| backtest: 90th percentile | 0.0469 |
| backtest: share of 24-day windows positive | 0.57 |
| backtest: mean excess in past Oct 19-Nov 20 windows (beat in 11 of 16) | 0.0142 |


## Every decision

| date | p_XLE | p_ICLN | model_side | momentum_side | target_XLE | target_ICLN | equity_est | action | reason | n_orders | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-10-23 | 0.6083 | 0.5448 | XLE | XLE | 1 | 0 | 1.034e+05 | NO_TRADE | mid-week, holding until the next weekly rebalance; today's signal: model and momentum agree on XLE | 0 | backfill |
| 2026-10-22 | 0.6425 | 0.5634 | XLE | XLE | 1 | 0 | 1.001e+05 | NO_TRADE | mid-week, holding until the next weekly rebalance; today's signal: model and momentum agree on XLE | 0 | backfill |
| 2026-10-21 | 0.6055 | 0.5231 | XLE | XLE | 1 | 0 | 1.012e+05 | NO_TRADE | mid-week, holding until the next weekly rebalance; today's signal: model and momentum agree on XLE | 0 | backfill |
| 2026-10-20 | 0.6336 | 0.4802 | XLE | XLE | 1 | 0 | 1.006e+05 | NO_TRADE | mid-week, holding until the next weekly rebalance; today's signal: model and momentum agree on XLE | 0 | backfill |
| 2026-10-19 | 0.6169 | 0.4382 | XLE | XLE | 1 | 0 | 1e+05 | TRADE | model and momentum agree on XLE | 8 | backfill |


## Every trade

| ticker | side | shares | price | dollars | date | fill_price | mode |
| --- | --- | --- | --- | --- | --- | --- | --- |
| VLO | BUY | 28.85 | 433.3 | 1.25e+04 | 2026-10-19 | 433.3 | backfill |
| HAL | BUY | 379 | 32.98 | 1.25e+04 | 2026-10-19 | 32.98 | backfill |
| SLB | BUY | 254.6 | 49.09 | 1.25e+04 | 2026-10-19 | 49.09 | backfill |
| EOG | BUY | 79.29 | 157.6 | 1.25e+04 | 2026-10-19 | 157.6 | backfill |
| OXY | BUY | 199.3 | 62.72 | 1.25e+04 | 2026-10-19 | 62.72 | backfill |
| COP | BUY | 86.06 | 145.2 | 1.25e+04 | 2026-10-19 | 145.2 | backfill |
| CVX | BUY | 55.71 | 224.4 | 1.25e+04 | 2026-10-19 | 224.4 | backfill |
| XOM | BUY | 70.11 | 178.3 | 1.25e+04 | 2026-10-19 | 178.3 | backfill |


