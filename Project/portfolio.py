"""
Turn model probabilities and momentum into side weights, stock holdings and orders
"""
import math

import config


def kelly_fraction(p: float, win_loss_ratio: float = config.WIN_LOSS_RATIO) -> float:
    """
    Kelly criterion bet size: p - (1 - p) / win_loss_ratio, never below 0
    """
    return max(p - (1 - p) / win_loss_ratio, 0.0)


def target_weights(probs: dict, rule: str = "kelly", p_cash: float = config.P_CASH,
                   kelly_multiplier: float = config.KELLY_MULT,
                   win_loss_ratio: float = config.WIN_LOSS_RATIO) -> dict:
    """
    Weight per ticker for the kelly and all_in rules (the rest is cash).
    
    `kelly` bets a fraction of the Kelly size.
    `all_in` puts 100% in the best ticker if it clears p_cash.
    """
    probs = {ticker: p for ticker, p in probs.items() if not math.isnan(p)}
    weights = {ticker: 0.0 for ticker in probs}
    if not probs:
        return weights

    best = max(probs, key=probs.get)
    if probs[best] < p_cash:
        return weights
    if rule == "all_in":
        weights[best] = 1.0
        return weights

    for ticker, p in probs.items():
        weights[ticker] = kelly_multiplier * kelly_fraction(p, win_loss_ratio)
    total = sum(weights.values())
    # Scale down if the bets add up to more than 100%
    if total > 1:
        weights = {ticker: weight / total for ticker, weight in weights.items()}
    return weights


def momentum_side(close, lookback: int = config.MOMENTUM_LOOKBACK_DAYS) -> str:
    """
    The ETF that's up over the lookback. XLE if both/neither are up.
    """
    is_up = {ticker: close[ticker].iloc[-1] > close[ticker].iloc[-1 - lookback] for ticker in config.TARGETS}
    return max(config.TARGETS, key=lambda ticker: is_up[ticker])


def side_weights(probs: dict, momentum_side_pick: str, rule: str = config.SIZING_RULE) -> tuple[dict, str]:
    """
    Weight on each side (XLE = traditional, ICLN = clean) and a one-line reason.
    """
    best = max(probs, key=probs.get)
    if probs[best] < config.P_EXIT:
        return {ticker: 0.0 for ticker in probs}, f"model rates both sides below {config.P_EXIT:.2f}: cash"
    if rule == "switch":
        return {ticker: float(ticker == best) for ticker in probs}, f"model prefers {best}"
    if rule == "agree":
        if best == momentum_side_pick:
            return {ticker: float(ticker == best) for ticker in probs}, f"model and momentum agree on {best}"
        return ({ticker: 0.5 for ticker in probs},
                f"model prefers {best}, momentum prefers {momentum_side_pick}: half in each")
    weights = target_weights(probs, rule=rule)
    return weights, f"{rule} sizing"


def to_holdings(sides: dict, holdings: str = config.HOLDINGS) -> dict:
    """
    Spread each side's weight over the ETF itself or equally over its basket stocks
    """
    if holdings == "etf":
        return dict(sides)
    return {ticker: weight / len(config.BASKETS[side])
            for side, weight in sides.items() for ticker in config.BASKETS[side]}


def plan_orders(shares: dict, cash: float, prices: dict, weights: dict) -> list[dict]:
    """
    Orders (fractional shares, to 4 decimal points) that move holdings to the target weights. 
    Sells first to secure cash. 
    """
    equity = cash + sum(count * prices[ticker] for ticker, count in shares.items() if count)
    orders = []
    for ticker, weight in weights.items():
        held = shares.get(ticker, 0)
        target = weight * equity
        delta = round(target / prices[ticker] - held, 4)
        if delta:
            orders.append({"ticker": ticker, "side": "BUY" if delta > 0 else "SELL", "shares": abs(delta),
                           "price": prices[ticker], "dollars": abs(delta) * prices[ticker]})
    return sorted(orders, key=lambda order: order["side"] != "SELL")


def apply_orders(shares: dict, cash: float, orders: list[dict]) -> tuple[dict, float]:
    """
    Update share counts and cash for a list of orders.
    """
    shares = dict(shares)
    for order in orders:
        sign = 1 if order["side"] == "BUY" else -1
        shares[order["ticker"]] = shares.get(order["ticker"], 0) + sign * order["shares"]
        cash -= sign * order["dollars"]
    return shares, cash
