"""
Write the live results to live/: a README that GitHub shows as a page, plus the CSVs behind it
"""
import os
import numpy as np
import pandas as pd

import config
import data_loader

LEDGER = config.LEDGER_DIR
LIVE_DIR = config.PAGE_DIR


def _read(name: str) -> pd.DataFrame:
    path = os.path.join(LEDGER, name)
    return pd.read_csv(path) if os.path.exists(path) else pd.DataFrame()


def equity_curve(trades: pd.DataFrame, close: pd.DataFrame) -> pd.Series:
    """
    Portfolio value at each close, replaying the trade log at fill prices
    """
    cash, shares, values = config.STARTING_CAPITAL, {}, {}
    trades_by_day = {day: day_trades for day, day_trades in trades.groupby("date")} if len(trades) else {}
    for day in close.index:
        for _, trade in trades_by_day.get(day.date().isoformat(), pd.DataFrame()).iterrows():
            price = trade["fill_price"] if pd.notna(trade["fill_price"]) else trade["price"]
            sign = 1 if trade["side"] == "BUY" else -1
            shares[trade["ticker"]] = shares.get(trade["ticker"], 0) + sign * trade["shares"]
            cash -= sign * trade["shares"] * price
        values[day] = cash + sum(count * close.at[day, ticker] for ticker, count in shares.items() if count)
    return pd.Series(values, name="portfolio")


def buy_and_hold(close: pd.DataFrame, weights: dict) -> pd.Series:
    start = close.iloc[0]
    return sum(config.STARTING_CAPITAL * weight * close[ticker] / start[ticker] for ticker, weight in weights.items())


def benchmarks(close: pd.DataFrame) -> pd.DataFrame:
    both_baskets = {ticker: 0.5 / len(basket) for basket in config.BASKETS.values() for ticker in basket}
    return pd.DataFrame({
        "both baskets 50/50": buy_and_hold(close, both_baskets),
        "XLE/ICLN 50/50": buy_and_hold(close, {"XLE": 0.5, "ICLN": 0.5}),
        "SPY": buy_and_hold(close, {"SPY": 1.0}),
    })


def summary(curves: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame([{"series": name, "return": curve.iloc[-1] / config.STARTING_CAPITAL - 1,
                          "max_drawdown": (curve / curve.cummax() - 1).min(), "last_value": curve.iloc[-1]}
                         for name, curve in curves.items()])


def md_table(df: pd.DataFrame) -> str:
    """
    A GitHub markdown table, with cutoffs to 4 decimal points
    """
    if not len(df):
        return "_None yet._\n"

    def cell(value) -> str:
        if value is None or pd.isna(value):
            return ""
        return f"{value:,.4g}" if isinstance(value, float) else str(value)

    rows = [" | ".join(map(str, df.columns)), " | ".join("---" for _ in df.columns)]
    rows += [" | ".join(cell(value) for value in row) for row in df.itertuples(index=False)]
    return "\n".join(f"| {row} |" for row in rows) + "\n"


# Backtest reference numbers for the threads, based on research module explorations
EXPECTED = {
    "excess_24d_mean": 0.0056, "excess_24d_p10": -0.0396, "excess_24d_p90": 0.0469, "excess_24d_share_pos": 0.57,
    "past_windows_beat": "11 of 16", "past_windows_mean_excess": 0.0142,
    "agree_share": 0.63, "right_when_agree": 0.57, "right_when_disagree": 0.50,
    "midterm_runup": "about +3-4% over the 20 trading days into election day",
    "clean_basket_corr_icln": 0.82,
}


def side_returns(close: pd.DataFrame) -> pd.DataFrame:
    """
    Daily returns of each ETF and of its equal-weight basket
    """
    returns = close.pct_change(fill_method=None)
    out = {ticker: returns[ticker] for ticker in config.TARGETS}
    for etf, basket in config.BASKETS.items():
        out[f"{etf} basket"] = returns[basket].mean(axis=1)
    return pd.DataFrame(out)


def _growth(returns: pd.Series) -> float:
    clean = returns.dropna().to_numpy(dtype=float)
    return float(np.prod(1.0 + clean) - 1.0) if len(clean) else float("nan")


# --------Thread helpers----------
# We have a bunch of thread methods that follow things that I want to investigate or that I think could
# be of interest for doing the final report and overall research


def thread_election(curves: pd.DataFrame, sides: pd.DataFrame, election: pd.Timestamp) -> pd.DataFrame:
    """
    Investigate election week runup effect: return into election day and after it,
    for the portfolio, benchmarks, and each side
    """
    daily = pd.concat([curves.pct_change(), sides], axis=1)
    return pd.DataFrame([{"series": column, "into_election": _growth(daily[column].loc[:election].iloc[1:]),
                          "after_election": _growth(daily[column].loc[election:].iloc[1:])}
                         for column in daily.columns])


def thread_agreement(decisions: pd.DataFrame, sides: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Investigate model/momentum agreement on trading decision, and which side did better until the next one
    """
    if not len(decisions) or "model_side" not in decisions:
        return pd.DataFrame(), pd.DataFrame()
    decided = decisions.dropna(subset=["model_side"]).copy()
    if decided.empty:
        return pd.DataFrame(), pd.DataFrame()
    decided["date"] = pd.to_datetime(decided["date"])

    calendar = sides.index
    weeks = decided[[date == calendar[calendar.isocalendar().week.to_numpy() == date.isocalendar()[1]].min()
                     for date in decided["date"]]]
    
    rows = []
    for position, (_, decision) in enumerate(weeks.iterrows()):
        end = weeks["date"].iloc[position + 1] if position + 1 < len(weeks) else calendar[-1]
        period = sides.loc[decision["date"]:end].iloc[1:]
        if period.empty:
            continue
        held = {ticker: _growth(period[f"{ticker} basket" if config.HOLDINGS == "basket" else ticker])
                for ticker in config.TARGETS}
        winner = max(held, key=held.get)
        rows.append({"week_of": decision["date"].date(), "model_side": decision["model_side"],
                     "momentum_side": decision["momentum_side"],
                     "agree": decision["model_side"] == decision["momentum_side"], "better_side": winner,
                     **{f"{ticker}_return": value for ticker, value in held.items()},
                     "model_right": decision["model_side"] == winner,
                     "momentum_right": decision["momentum_side"] == winner,
                     "complete": len(period) >= 4})
    
    weekly = pd.DataFrame(rows)
    if weekly.empty:
        return weekly, pd.DataFrame()
    agree, disagree = weekly[weekly["agree"]], weekly[~weekly["agree"]]

    summary = pd.DataFrame([
        {"measure": "weeks", "live": len(weekly), "backtest": ""},
        {"measure": "share of weeks the two agree", "live": weekly["agree"].mean(), "backtest": EXPECTED["agree_share"]},
        {"measure": "model right when they agree", "live": agree["model_right"].mean() if len(agree) else None,
         "backtest": EXPECTED["right_when_agree"]},
        {"measure": "model right when they disagree", "live": disagree["model_right"].mean() if len(disagree) else None,
         "backtest": EXPECTED["right_when_disagree"]},
        {"measure": "momentum right overall", "live": weekly["momentum_right"].mean(), "backtest": ""},
    ])
    return weekly, summary


def thread_underlyings(sides: pd.DataFrame) -> pd.DataFrame:
    """
    Investigate how far each basket drifted from its ETF over the contest
    """
    rows = []
    for etf in config.TARGETS:
        basket_returns = sides[f"{etf} basket"]
        rows.append({"side": etf, "etf_return": _growth(sides[etf]), "basket_return": _growth(basket_returns),
                     "basket_minus_etf": _growth(basket_returns) - _growth(sides[etf]),
                     "daily_corr": sides[etf].corr(basket_returns),
                     "backtest_corr": EXPECTED["clean_basket_corr_icln"] if etf == "ICLN" else ""})
    return pd.DataFrame(rows)


def thread_regimes(history: pd.DataFrame, decisions: pd.DataFrame) -> pd.DataFrame:
    """
    Investigate 12-month market and energy regimes during the contest, and days the momentum side changed
    """
    trailing_12m = history.pct_change(252, fill_method=None).loc[config.LIVE_START:]
    labels = pd.DataFrame({"market_up_12m": trailing_12m["SPY"] > 0,
                           "energy_beats_market_12m": trailing_12m["XLE"] > trailing_12m["SPY"],
                           "clean_beats_traditional_12m": trailing_12m["ICLN"] > trailing_12m["XLE"]})
    if len(decisions) and "momentum_side" in decisions:
        momentum_rows = decisions.dropna(subset=["momentum_side"])
        labels = labels.join(pd.Series(momentum_rows["momentum_side"].values,
                                       index=pd.to_datetime(momentum_rows["date"]), name="momentum_side"))
        labels["momentum_side_changed"] = labels["momentum_side"].ne(labels["momentum_side"].shift()) & \
            labels["momentum_side"].shift().notna()
    return labels.rename_axis("date").reset_index()


def thread_vs_backtest(curves: pd.DataFrame) -> pd.DataFrame:
    """
    Investigate excess return over the both-baskets benchmark so far, next to the backtest's range for a window this long
    """
    excess = curves["portfolio"].iloc[-1] / curves["both baskets 50/50"].iloc[-1] - 1
    return pd.DataFrame([
        {"measure": "excess over both baskets so far", "value": excess},
        {"measure": "backtest: mean 24-day excess", "value": EXPECTED["excess_24d_mean"]},
        {"measure": "backtest: 10th percentile", "value": EXPECTED["excess_24d_p10"]},
        {"measure": "backtest: 90th percentile", "value": EXPECTED["excess_24d_p90"]},
        {"measure": "backtest: share of 24-day windows positive", "value": EXPECTED["excess_24d_share_pos"]},
        {"measure": "backtest: mean excess in past Oct 19-Nov 20 windows (beat in "
                    f"{EXPECTED['past_windows_beat']})", "value": EXPECTED["past_windows_mean_excess"]},
    ])


THREAD_TEXT = {
    "election": ("Election week runup", "Did energy run up into election day (Nov 3) and go flat after, as it did in the past "
                 f"midterms ({EXPECTED['midterm_runup']})? Did clean or traditional react more?"),
    "agreement": ("Model vs. momentum agreement", "How often did the two agree, and was the model right more often when they did?"),
    "underlyings": ("Baskets vs ETFs", "How far did each stock basket drift from its ETF?"),
    "regimes": ("Regime shifts", "Did a 12-month regime flip, or did the momentum side change?"),
    "vs_backtest": ("Live vs backtest range", "Is the excess return inside the range the backtest expects?"),
}


def build_threads(decisions: pd.DataFrame, curves: pd.DataFrame, history: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """
    Compute the five thread tables and save each as live/thread_<name>.csv
    """
    close = history.loc[config.LIVE_START:config.LIVE_END]
    sides = side_returns(close)
    election = pd.Timestamp(next(day for day in config.ELECTION_DAYS if day.isoformat() >= config.LIVE_START))
    weekly, agree_summary = thread_agreement(decisions, sides)
    tables = {"election": thread_election(curves, sides, election), "agreement": agree_summary,
              "agreement_weekly": weekly, "underlyings": thread_underlyings(sides),
              "regimes": thread_regimes(history, decisions), "vs_backtest": thread_vs_backtest(curves)}
    for name, table in tables.items():
        table.to_csv(os.path.join(LIVE_DIR, f"thread_{name}.csv"), index=False)
    return tables


def threads_md(tables: dict[str, pd.DataFrame]) -> str:
    """
    The threads section of live/README.md
    """
    parts = []
    for key, (title, question) in THREAD_TEXT.items():
        table = tables[key]
        if key == "regimes" and len(table):
            changed = table.loc[table["momentum_side_changed"].fillna(False).astype(bool), "date"] \
                if "momentum_side_changed" in table else []
            # Show only the first and latest day; the CSV has every day
            table = table.iloc[[0, -1]]
            question += f" Momentum side changed on: {', '.join(str(date.date()) for date in changed) or 'no day yet'}."
        parts.append(f"### {title}\n\n{question}\n\n{md_table(table)}")
        if key == "agreement":
            parts.append(md_table(tables["agreement_weekly"]))
    return "\n".join(parts)


def build_page() -> str:
    decisions, trades = _read("decisions.csv"), _read("trades.csv")
    os.makedirs(LIVE_DIR, exist_ok=True)
    decisions.to_csv(os.path.join(LIVE_DIR, "decisions.csv"), index=False)
    trades.to_csv(os.path.join(LIVE_DIR, "trades.csv"), index=False)

    # Extra history before the contest for the 12-month regime labels (thread T4)
    history = data_loader.fetch_holdings_closes(
        (pd.Timestamp(config.LIVE_START) - pd.Timedelta(days=config.LIVE_HISTORY_DAYS)).date().isoformat())
    history = history.loc[:config.LIVE_END]
    close = history.loc[config.LIVE_START:].dropna(how="all")
    close.rename_axis("date").to_csv(os.path.join(LIVE_DIR, "prices.csv"))
    curves = pd.concat([equity_curve(trades, close), benchmarks(close)], axis=1)
    curves.rename_axis("date").to_csv(os.path.join(LIVE_DIR, "equity.csv"))
    stats = summary(curves)
    stats.to_csv(os.path.join(LIVE_DIR, "summary.csv"), index=False)
    tables = build_threads(decisions, curves, history)

    # Net shares per ticker: buys minus sells
    held = pd.Series(dtype=float)
    if len(trades):
        signed = trades["shares"].where(trades["side"] == "BUY", -trades["shares"])
        held = signed.groupby(trades["ticker"]).sum()
        held = held[held.abs() > 1e-9]
    holdings = pd.DataFrame({"ticker": held.index, "shares": held.values,
                             "value": [float(count * close.iloc[-1][ticker]) for ticker, count in held.items()]})
    latest = (f"**{decisions.iloc[-1]['date']}: {decisions.iloc[-1]['action']}** - {decisions.iloc[-1]['reason']}"
              if len(decisions) else "No decisions logged yet.")
    text = f"""# Live trades: trading project around energy around the 2026 elections

As of {close.index[-1]:%Y-%m-%d}. Strategy: {config.SIZING_RULE} rule, holding {config.HOLDINGS}s, rebalanced on the first
trading day of each week; models trained on data through {config.TRAINING_END}; contest {config.LIVE_START} to {config.LIVE_END}.

## Latest decision

{latest}

## Holdings

{md_table(holdings)}

## Returns since {config.LIVE_START}

{md_table(stats)}

## Threads to follow

{threads_md(tables)}

## Every decision

{md_table(decisions.iloc[::-1])}

## Every trade

{md_table(trades.iloc[::-1])}

"""
    path = os.path.join(LIVE_DIR, "README.md")
    with open(path, "w") as f:
        f.write(text)
    print(f"Wrote {path}")
    return path


if __name__ == "__main__":
    build_page()
