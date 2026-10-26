"""
Daily run at 2:30 PM ET: score both sides, decide whether to trade, log the decision and update live/README.md.

Each weekday from LIVE_START to LIVE_END gets one row in ledger/decisions.csv: TRADE/NO_TRADE and why.
"""
import argparse
import datetime as dt
import json
import os
import sys
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

import config
import data_loader
import features
import model
import page
import portfolio

STATE_PATH = os.path.join(config.LEDGER_DIR, "positions.json")
TRADES_PATH = os.path.join(config.LEDGER_DIR, "trades.csv")
DECISIONS_PATH = os.path.join(config.LEDGER_DIR, "decisions.csv")
EASTERN = ZoneInfo("America/New_York")


class Inputs:
    """
    Prices and features from `start` to the latest price (generally should be 2:30 PM price on T)
    """

    def __init__(self, start: str, end: str | None = None):
        self.close = data_loader.fetch_market_data(start, end)
        self.sectors = data_loader.fetch_sector_matrix(start, end)
        self.stocks = data_loader.fetch_factor_universe(start, end)
        self.holdings = data_loader.fetch_holdings_closes(start, end)
        self.base = features.build_base_features(self.close, self.sectors)

    def probs(self, models: dict) -> pd.DataFrame:
        """
        P(up over HORIZON_DAYS days) for every date and ticker.
        """
        return pd.DataFrame(
            {
                t: m.predict_proba(self.base, self.sectors, self.stocks) for t, m in models.items()
            },
            index=self.base.index
        )


def train_and_save():
    """
    Train one model per ETF on data through TRAINING_END and save them to models/
    """
    close = data_loader.fetch_market_data()
    sectors = data_loader.fetch_sector_matrix()
    stocks = data_loader.fetch_factor_universe()
    base = features.build_base_features(close, sectors)
    models = {
        ticker: model.train_asset_model(base, sectors, close, ticker, config.TRAINING_END, stock_returns=stocks)
        for ticker in config.TARGETS
    }
    print(f"Saved models trained through {config.TRAINING_END} to {model.save_models(models)}")


def load_state() -> dict:
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH) as f:
            return json.load(f)
    return {"cash": config.STARTING_CAPITAL, "shares": {}}


def save_state(state: dict):
    os.makedirs(config.LEDGER_DIR, exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def append_csv(path: str, rows: list[dict]):
    """
    Append rows, rewriting the file so a row with new or missing columns can't shift the others.
    """
    if rows:
        os.makedirs(config.LEDGER_DIR, exist_ok=True)
        old = pd.read_csv(path) if os.path.exists(path) else None
        pd.concat([old, pd.DataFrame(rows)], ignore_index=True).to_csv(path, index=False)


def logged_dates() -> set:
    if not os.path.exists(DECISIONS_PATH):
        return set()
    return set(pd.read_csv(DECISIONS_PATH)["date"])


def reconcile_fills(holdings: pd.DataFrame, state: dict, today: pd.Timestamp) -> dict:
    """
    Live trades are sized at the 2:30 PM price but "fill" at the 4:00 PM close.
    Replace each past trade's estimated price with that day's close and correct cash for the difference.
    """
    if not os.path.exists(TRADES_PATH):
        return state
    trades = pd.read_csv(TRADES_PATH, parse_dates=["date"])
    for row in trades.index[trades["fill_price"].isna() & (trades["date"] < today)]:
        fill = holdings.at[trades.at[row, "date"], trades.at[row, "ticker"]]
        sign = 1 if trades.at[row, "side"] == "BUY" else -1
        state["cash"] -= sign * trades.at[row, "shares"] * (fill - trades.at[row, "price"])
        trades.at[row, "fill_price"] = fill
    trades.to_csv(TRADES_PATH, index=False)
    return state


def is_rebalance_day(date: pd.Timestamp, calendar: pd.DatetimeIndex) -> bool:
    """
    For simplicity, we do rebalancing only on first trading day of the week
    """
    iso, (year, week, _) = calendar.isocalendar(), date.isocalendar()
    same_week = (iso["year"].to_numpy() == year) & (iso["week"].to_numpy() == week)
    return date == calendar[same_week].min()


def decide(date: pd.Timestamp, inputs: Inputs, probs: pd.DataFrame, state: dict) -> tuple[dict, list[dict], dict]:
    """
    Decision for `date` using only data up to that date. Returns (log row, orders, state after orders).
    """
    close = inputs.close.loc[:date]
    today_probs = probs.loc[date].to_dict()
    momentum_pick = portfolio.momentum_side(close)
    sides, why = portfolio.side_weights(today_probs, momentum_pick)
    prices = inputs.holdings.loc[date].to_dict()
    equity = state["cash"] + sum(count * prices[ticker] for ticker, count in state["shares"].items() if count)
    row = {"date": date.date().isoformat(),
           **{f"p_{ticker}": round(value, 4) for ticker, value in today_probs.items()},
           "model_side": max(today_probs, key=today_probs.get), "momentum_side": momentum_pick,
           **{f"target_{ticker}": weight for ticker, weight in sides.items()},
           "equity_est": round(equity, 2)}

    holding_nothing = not any(state["shares"].values())
    if not (holding_nothing or is_rebalance_day(date, inputs.close.index)):
        return dict(row, action="NO_TRADE", reason=f"mid-week, holding until the next weekly rebalance; today's signal: {why}"), [], state

    # Zero out anything held that the new target doesn't include, so switching sides sells it
    weights = {ticker: 0.0 for ticker in state["shares"]} | portfolio.to_holdings(sides)
    orders = portfolio.plan_orders(state["shares"], state["cash"], prices, weights)
    if not orders:
        return dict(row, action="NO_TRADE", reason=f"already at target; {why}"), [], state
    shares, cash = portfolio.apply_orders(state["shares"], state["cash"], orders)
    return dict(row, action="TRADE", reason=why), orders, {"cash": cash, "shares": shares}


def format_post(when: str, row: dict, orders: list[dict], state: dict, prices: dict) -> str:
    """
    Present the decision output nicely for display the run log
    """
    lines = [f"[{when}] {row['action']}: {row['reason']}"]
    if orders:
        lines.append("Orders, filled at today's 4:00 PM ET close:")
        lines += [f"  {order['side']} {order['shares']:g} {order['ticker']} "
                  f"(~${order['dollars']:,.0f} at ${order['price']:.2f})" for order in orders]
    held = [f"{ticker} {count:g}" for ticker, count in state["shares"].items() if count]
    equity = state["cash"] + sum(count * prices[ticker] for ticker, count in state["shares"].items() if count)
    lines.append(f"Holding after: {', '.join(held) or 'nothing'}; cash ~${state['cash']:,.0f}; equity ~${equity:,.0f}")
    lines.append(f"Model P(up over {config.HORIZON_DAYS} days): "
                 + ", ".join(f"{ticker} {row[f'p_{ticker}']:.2f}" for ticker in config.TARGETS)
                 + f"; {config.MOMENTUM_LOOKBACK_DAYS}-day momentum favours {row['momentum_side']}")
    return "\n".join(lines)


def record(row: dict, orders: list[dict], state: dict, mode: str, fill_at_close: bool):
    """
    Save the new positions and append the day's trades and decision to the ledger
    """
    save_state(dict(state, as_of=row["date"]))
    append_csv(TRADES_PATH, [dict(order, date=row["date"], fill_price=order["price"] if fill_at_close else np.nan, mode=mode) for order in orders])
    append_csv(DECISIONS_PATH, [dict(row, n_orders=len(orders), mode=mode)])


def live_history_start(first_day) -> str:
    """
    First date of the price history a live run loads (LIVE_HISTORY_DAYS before first_day)
    """
    return (pd.Timestamp(first_day) - pd.Timedelta(days=config.LIVE_HISTORY_DAYS)).date().isoformat()


def backfill(until: str | None = None) -> int:
    """
    Replay each unlogged trading day from LIVE_START to `until` (default yesterday) at that day's close
    """
    today = dt.datetime.now(EASTERN).date()
    until = pd.Timestamp(until or today - dt.timedelta(days=1))
    until = min(until, pd.Timestamp(config.LIVE_END))
    models = model.load_models()
    inputs = Inputs(live_history_start(config.LIVE_START))
    probs = inputs.probs(models)
    already_logged = logged_dates()
    days = [day for day in inputs.close.loc[config.LIVE_START:until].index 
            if day.date().isoformat() not in already_logged]
    state = load_state()
    for day in days:
        row, orders, state = decide(day, inputs, probs, state)
        print(format_post(f"{day:%Y-%m-%d} close, backfill", row, orders, state, inputs.holdings.loc[day].to_dict()), "\n")
        record(row, orders, state, mode="backfill", fill_at_close=True)
    print(f"Backfilled {len(days)} day(s) through {until:%Y-%m-%d}")
    page.build_page()
    return 0


def preview(as_of: str | None) -> int:
    """
    Print the decision for as_of (default today) without logging anything
    """
    models = model.load_models()
    day = pd.Timestamp(as_of) if as_of else pd.Timestamp(dt.datetime.now(EASTERN).date())
    inputs = Inputs(live_history_start(day))
    day = inputs.close.loc[:day].index[-1]
    row, orders, state = decide(day, inputs, inputs.probs(models), load_state())
    print(format_post(f"{day:%Y-%m-%d} preview", row, orders, state, inputs.holdings.loc[day].to_dict()))
    return 0


def in_trade_window(now: dt.datetime) -> bool:
    earliest, latest = config.TRADE_WINDOW
    return earliest <= now.strftime("%H:%M") <= latest


def run_daily(force: bool = False) -> int:
    """
    The scheduled run: decide once per trading day inside TRADE_WINDOW
    """
    now = dt.datetime.now(EASTERN)
    today = now.date()
    if not force and not in_trade_window(now):
        print(f"{now:%H:%M} ET is outside the trade window {config.TRADE_WINDOW}; nothing to do")
        return 0
    if not config.LIVE_START <= today.isoformat() <= config.LIVE_END:
        print(f"{today} is outside the contest ({config.LIVE_START} to {config.LIVE_END}); refreshing the page only")
        page.build_page()
        return 0
    already_logged = logged_dates()
    if today.isoformat() in already_logged:
        print("Already decided today; nothing to do")
        return 0

    inputs = Inputs(live_history_start(today))
    missing = [day for day in inputs.close.loc[config.LIVE_START:pd.Timestamp(today) - pd.Timedelta(days=1)].index
               if day.date().isoformat() not in already_logged]
    if missing:
        print(f"WARNING: {len(missing)} earlier contest day(s) have no decision; run --backfill to fill them")
    if inputs.close.index[-1].date() != today:
        row = {"date": today.isoformat(), "action": "NO_TRADE",
               "reason": f"no price for today (latest bar {inputs.close.index[-1]:%Y-%m-%d}): holiday or data delay"}
        print(row["reason"])
        append_csv(DECISIONS_PATH, [dict(row, n_orders=0, mode="live")])
        page.build_page()
        return 0

    day = inputs.close.index[-1]
    state = reconcile_fills(inputs.holdings, load_state(), day)
    row, orders, state = decide(day, inputs, inputs.probs(model.load_models()), state)
    print(format_post(now.strftime("%Y-%m-%d %H:%M ET"), row, orders, state, inputs.holdings.loc[day].to_dict()))
    record(row, orders, state, mode="live", fill_at_close=False)
    page.build_page()
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--train", action="store_true", help="fit and save models on data through TRAINING_END")
    parser.add_argument("--dry-run", action="store_true", help="print a decision without logging anything")
    parser.add_argument("--as-of", help="with --dry-run: the date to decide for (default today)")
    parser.add_argument("--backfill", action="store_true", help="replay unlogged days from LIVE_START at the close")
    parser.add_argument("--until", help="with --backfill: last day to replay (default yesterday)")
    parser.add_argument("--page", action="store_true", help="rewrite live/ from the ledger")
    parser.add_argument("--force", action="store_true", help="skip the post-window check")
    args = parser.parse_args()
    if args.train:
        train_and_save()
    elif args.backfill:
        sys.exit(backfill(args.until))
    elif args.dry_run:
        sys.exit(preview(args.as_of))
    elif args.page:
        page.build_page()
    else:
        sys.exit(run_daily(args.force))
