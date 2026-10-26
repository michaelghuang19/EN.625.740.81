"""
Load daily close data from Yahoo Finance.
"""
import time
import pandas as pd
import yfinance as yf

import config


def download_close(tickers: list[str], start: str, end: str | None = None) -> pd.DataFrame:
    """
    Daily adjusted closes, one column per ticker
    """
    # Yahoo seems to throttle requests, so if we run into issues, just wait and retry
    # TODO: Maybe use tenacity here later? 
    for attempt in range(3):
        raw = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=False)
        if not raw.empty:
            break
        time.sleep(20 * (attempt + 1))
    if raw.empty:
        raise RuntimeError(f"Yahoo Finance returned no data for {tickers}")
    close = raw["Close"]
    if isinstance(close, pd.Series):
        close = close.to_frame(tickers[0])
    close = close[tickers].dropna(how="all")
    if close.index.tz is not None:
        close.index = close.index.tz_localize(None)
    return close


def splice_proxy(series: pd.Series, proxy: pd.Series) -> pd.Series:
    """
    Fill in a series before its first date using the proxy's returns
    """
    first = series.first_valid_index()
    scaled = proxy.loc[:first] * series.loc[first] / proxy.loc[first]
    return series.combine_first(scaled)


def fetch_market_data(start: str = config.TRAINING_START, end: str | None = None) -> pd.DataFrame:
    """
    Closes for the targets, commodities and macro tickers
    """
    proxies = config.TARGET_PROXIES
    tickers = config.TARGETS + list(proxies.values()) + config.COMMODITY_BENCHMARKS + config.MACRO_BENCHMARKS
    close = download_close(tickers, start, end)

    # Crude went negative in 2020, which breaks things, so exclude that
    commodities = config.COMMODITY_BENCHMARKS
    close[commodities] = close[commodities].where(close[commodities] > 0)
    close = close[close["SPY"].notna()].ffill(limit=5)

    for t, proxy in proxies.items():
        close[t] = splice_proxy(close[t], close[proxy])
    return close.drop(columns=list(proxies.values()))


def fetch_sector_matrix(start: str = config.TRAINING_START, end: str | None = None) -> pd.DataFrame:
    """
    Daily returns of the sector ETFs, used for the sector PCA
    """
    return download_close(config.SECTOR_BENCHMARKS, start, end).pct_change(fill_method=None).dropna(how="all")


def fetch_factor_universe(start: str = config.TRAINING_START, end: str | None = None) -> pd.DataFrame:
    """
    Daily returns of the energy stocks used for the factor PCA
    """
    tickers = config.FACTOR_UNIVERSE["traditional"] + config.FACTOR_UNIVERSE["clean"]
    return download_close(tickers, start, end).pct_change(fill_method=None).dropna(how="all")


def fetch_holdings_closes(start: str, end: str | None = None) -> pd.DataFrame:
    """
    Closes for everything we can hold or compare against: both ETFs, the basket stocks and SPY
    """
    tickers = list(dict.fromkeys(config.TARGETS + [t for b in config.BASKETS.values() for t in b] + ["SPY"]))
    close = download_close(tickers, start, end)
    return close[close["SPY"].notna()].ffill(limit=5)
