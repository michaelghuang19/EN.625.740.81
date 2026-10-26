"""
Model inputs (technical indicators, cross-asset, sector stress, election calendar) and the target.
"""
import numpy as np
import pandas as pd

from pandas import Series, DataFrame

import config

TRADING_DAYS = 252

FEATURE_GROUPS = {
    "technical_indicators": ("tech_",),
    "cross_asset": ("xasset_", "macro_"),
    "pca": ("pca_",),
    "factors": ("factor_",),
    "calendar": ("cal_",),
}


def select_columns(columns, groups) -> list[str]:
    prefixes = tuple(p for g in groups for p in FEATURE_GROUPS[g])
    return [c for c in columns if c.startswith(prefixes)]


def rsi(close: Series, window: int = 14) -> Series:
    """
    Relative strength index
    """
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / window, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / window, adjust=False).mean()
    return 100 - 100 / (1 + gain / loss)


def technical_indicators(close: Series) -> DataFrame:
    """
    Momentum and volatility features for one price series
    """
    ret = close.pct_change(fill_method=None)
    # Try different EWMs over differnt time horizons
    ewm_fast = close.ewm(span=10, adjust=False).mean()
    ewm_slow = close.ewm(span=50, adjust=False).mean()
    # Bollinger Band Width (volatility measure)
    bb_width = 4 * close.rolling(20).std() / close.rolling(20).mean()
    vol10 = ret.ewm(span=10).std() * np.sqrt(TRADING_DAYS)

    out = DataFrame({
        "roc5": close.pct_change(5, fill_method=None),
        "roc20": close.pct_change(20, fill_method=None),
        "ewm_gap": ewm_fast / ewm_slow - 1,
        "rsi14": rsi(close),
        "bb_width": bb_width,
        "bb_squeeze": bb_width.rolling(120).rank(pct=True),
        "vol10": vol10,
        "vol_ratio": vol10 / (ret.rolling(60).std() * np.sqrt(TRADING_DAYS)),
    })
    return out.add_prefix(f"tech_{config.short_name(close.name)}_")


def build_technical_indicators(close: DataFrame) -> DataFrame:
    """
    Technical indicators for both ETFs, crude, natural gas and SPY
    """
    tickers = config.TARGETS + config.COMMODITY_BENCHMARKS + ["SPY"]
    return pd.concat([technical_indicators(close[t]) for t in tickers], axis=1)


def build_cross_asset(close: DataFrame) -> DataFrame:
    """
    How the ETFs move with fuel prices, SPY, and each other.
    Also some similar analysis against VIX, treasury rates, and small caps.
    """
    ret = close.pct_change(fill_method=None)
    crude, natgas = ret["CL=F"], ret["NG=F"]
    out = {}
    for c in config.COMMODITY_BENCHMARKS:
        out[f"xasset_{config.short_name(c)}_z252"] = (close[c] - close[c].rolling(252).mean()) / close[c].rolling(252).std()
    for t in config.TARGETS:
        n = config.short_name(t)
        out[f"xasset_{n}_crude_beta20"] = ret[t].rolling(20).cov(crude) / crude.rolling(20).var()
        out[f"xasset_{n}_crude_corr20"] = ret[t].rolling(20).corr(crude)
        out[f"xasset_{n}_natgas_beta20"] = ret[t].rolling(20).cov(natgas) / natgas.rolling(20).var()
        out[f"xasset_{n}_rel_spy20"] = (close[t] / close["SPY"]).pct_change(20, fill_method=None)
    out["xasset_xle_icln_corr20"] = ret["XLE"].rolling(20).corr(ret["ICLN"])

    # Use z-scores and changes instead of raw levels, which drift over the years
    vix = close["^VIX"]
    out["macro_vix_z252"] = (vix - vix.rolling(252).mean()) / vix.rolling(252).std()
    out["macro_vix_chg5"] = vix.pct_change(5, fill_method=None)
    out["macro_tnx_chg5"] = close["^TNX"].diff(5)
    out["macro_tnx_chg20"] = close["^TNX"].diff(20)
    out["macro_vix_tnx_corr20"] = ret["^VIX"].rolling(20).corr(close["^TNX"].diff())
    out["macro_size_spread20"] = (close["IWM"] / close["SPY"]).pct_change(20, fill_method=None)
    return DataFrame(out)


def absorption_ratio(sector_returns: DataFrame, window: int = 60) -> Series:
    """
    Share of sector movement explained by one factor over the last 60 days. Higher values means sectors moving together. 
    """
    values = sector_returns.to_numpy()
    out = np.full(len(values), np.nan)
    for i in range(window, len(values) + 1):
        block = values[i - window:i]
        block = block[~np.isnan(block).any(axis=1)]
        if len(block) < window // 2:
            continue
        eig = np.linalg.eigvalsh(np.corrcoef(block, rowvar=False))
        out[i - 1] = eig[-1] / eig.sum()
    # Prefixed with pca_ so it explicitly belongs to the pca feature group rather than getting added to the base features
    return Series(out, index=sector_returns.index, name=f"pca_absorption{window}")


def build_calendar(index: pd.DatetimeIndex) -> DataFrame:
    """
    Election-cycle and seasonal features from the date alone
    """
    dates = index.normalize()
    elections = pd.DatetimeIndex(config.ELECTION_DAYS)
    pos = elections.searchsorted(dates)
    next_e, prev_e = elections[pos], elections[pos - 1]
    days_to = (next_e - dates).days.to_numpy()
    days_since = (dates - prev_e).days.to_numpy()

    return DataFrame({
        "cal_days_to_election": days_to,
        "cal_days_since_election": days_since,
        "cal_midterm_cycle": (next_e.year.to_numpy() % 4 == 2).astype(int),
        "cal_election_window": ((days_to <= 30) | (days_since <= 20)).astype(int),
        "cal_month": dates.month.to_numpy(),
        "cal_heating_season": dates.month.isin([11, 12, 1, 2, 3]).astype(int),
        "cal_driving_season": dates.month.isin([5, 6, 7, 8, 9]).astype(int),
    }, index=index)


def build_base_features(close: DataFrame, sector_returns: DataFrame) -> DataFrame:
    """
    Every feature except the sector PCA factors, which model.py adds per training window
    """
    parts = [
        build_technical_indicators(close),
        build_cross_asset(close),
        absorption_ratio(sector_returns).reindex(close.index),
        build_calendar(close.index),
    ]
    return pd.concat(parts, axis=1)


def make_target(close: DataFrame, ticker: str, dead_zone: float = 0.0) -> Series:
    """
    The label the model learns to predict: 1 if the ticker's price is higher HORIZON_DAYS trading days later, else 0. The last HORIZON_DAYS days have no label yet.

    `dead_zone` is used as a threshold where that level of price movements either way can be approximately treated as 0, since it's likely from noise. Seems to work well for training, but not live model
    """
    fwd = close[ticker].shift(-config.HORIZON_DAYS) / close[ticker] - 1
    y = (fwd > 0).astype(float).where(fwd.notna())
    if dead_zone > 0:
        typical = close[ticker].pct_change(fill_method=None).rolling(60).std() * np.sqrt(config.HORIZON_DAYS)
        y = y.where(fwd.abs() >= dead_zone * typical)
    return y
