# Midterm Election Energy Trading (625.740 Project)

## Overview

By predicting whether whether XLE (traditional energy) and ICLN (clean energy) rise over the next 5 trading
days, we then allocate the $100,000 book into traditional or clean energy stocks, rebalanced weekly. Trades are
placed as market-on-close (MOC) orders, established at least 15 minutes ahead of the declared intent to trade. s

## Pipeline

```
data_loader.py   Load prices from Yahoo Finance
      |
features.py      Build features for model inputs based on input data
      |
model.py         Train and calibrate the model
      |
portfolio.py     Translate predictions into actual trades
      |
run_daily.py     Run the daily decisions end-to-end and write corresponding results
```

## Automated trading mechanism (GitHub Actions + daily page)

Using the GitHub Actions running the Python start script from the repo root; models go to `models/`, the trade log 
to `ledger/`, and corresponding results to `live/`. 

Each week, aim to hold the traditional energy side (8 oil and gas stocks) or clean energy side 
(4 clean-energy stocks), equally weighted. If there's not enough signal, then don't trade. 

We use a 5-day horizon, rebalance once a week, and trade at most once a week. 
Every weekday from when trading starts, the daily run writes one of the following rows to `ledger/decisions.csv`:
- `TRADE` with the corresponding orders
- `NO_TRADE` with the reason (mid-week, already at target, no price today). 

`live/README.md` is then updated with all decisions, holdings, and returns.
