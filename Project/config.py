"""
Project-wide settings and constants.
"""
import datetime as dt
import re

# ----------Ticker Constants----------

TARGETS = ["XLE", "ICLN"]
# ICLN only launched in 2008, so use PBW before then
TARGET_PROXIES = {"ICLN": "PBW"}
COMMODITY_BENCHMARKS = ["CL=F", "NG=F"]
MACRO_BENCHMARKS = ["SPY", "IWM", "^VIX", "^TNX"]
# SPDR ETFs for proxying sectors
SECTOR_BENCHMARKS = ["XLB", "XLF", "XLI", "XLK", "XLP", "XLU", "XLV", "XLY"]

# Energy stocks for doing Factor-esque PCA
FACTOR_UNIVERSE = {
    "traditional": ["COP", "CVX", "EOG", "HAL", "OXY", "SLB", "VLO", "XOM"],
    "clean": ["CSIQ", "FSLR", "NEE", "ORA", "PLUG"],
}

_SPECIAL_NAMES = {"CL=F": "crude", "NG=F": "natgas", "^VIX": "vix", "^TNX": "tnx"}
def short_name(ticker: str) -> str:
    """
    Use regex to fix up a column-safe name for a ticker
    """
    return _SPECIAL_NAMES.get(ticker, re.sub(r"[^a-z0-9]", "", ticker.lower()))

# ----------Time Constants----------

TRAINING_START = "2000-01-01"
TRAINING_END = "2026-10-16"
LIVE_START = "2026-10-19"
LIVE_END = "2026-11-20"
TRADE_WINDOW = ("14:15", "15:00")
LIVE_HISTORY_DAYS = 400

# ----------Model Constants----------

# Basic groups we tested -- raw technical data, calendar data around elections, and sector PCA
DEFAULT_GROUPS = ["technical_indicators", "calendar", "pca"]
CLASSIFIER = "xgb"
HORIZON_DAYS = 5
DEAD_ZONE = 0.0
MAX_FEATURES = None
CORR_THRESHOLD = 0.90
N_PCA = 3
N_FACTORS = 3
HALF_LIFE_YEARS = 6.0
CALIBRATION_YEARS = 2

# ----------Trading Constants----------

# We tested between "agree", "switch", "kelly", "all_in"
SIZING_RULE = "agree"
# Go to cash if both sides are below this
P_EXIT = 0.45
MOMENTUM_LOOKBACK_DAYS = 20
# "basket" or "etf", where "basket" is using the weighted set of stocks rather than the ETFs themselves
HOLDINGS = "basket"
BASKETS = {
    "XLE": ["XOM", "CVX", "COP", "OXY", "EOG", "SLB", "HAL", "VLO"],
    "ICLN": ["FSLR", "NEE", "ORA", "CSIQ"],
}

STARTING_CAPITAL = 100_000.0
P_CASH = 0.50
KELLY_MULT = 0.5
WIN_LOSS_RATIO = 1.0

MODEL_DIR = "models"
LEDGER_DIR = "ledger"
PAGE_DIR = "live"


def election_day(year: int) -> dt.date:
    """
    US elections happen the Tuesday after the first Monday in November (NOT the first Tuesday)
    """
    first_november_monday = dt.date(year, 11, 1) + dt.timedelta(days=(7 - dt.date(year, 11, 1).weekday()) % 7)
    return first_november_monday + dt.timedelta(days=1)

# Get all election days for even years, which is when federal elections happen
ELECTION_DAYS = [election_day(y) for y in range(1998, 2030, 2)]
