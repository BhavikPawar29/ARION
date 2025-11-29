# backend/utils/fetch_data.py
"""
Robust data fetcher for ARION (hackathon-ready).
- Batch-downloads historical OHLC with yfinance.download (less noisy).
- Retries with exponential backoff on transient failures (429 / network).
- Uses last-close as current price (avoids additional quoteSummary calls).
- Falls back to sample JSON if live fetching fails.
- Simple on-disk caching per symbol-set to avoid repeated hits.
"""

import os
import time
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pandas as pd

try:
    import yfinance as yf
except Exception:
    yf = None

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # backend/
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
SAMPLE_PATH = os.path.join(DATA_DIR, "sample_summary.json")


def load_sample_summary() -> Optional[Dict[str, Any]]:
    if os.path.exists(SAMPLE_PATH):
        with open(SAMPLE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def cache_path_for(symbols: List[str], period: str):
    key = "-".join(sorted([s.upper() for s in symbols]))
    return os.path.join(DATA_DIR, f"cache_{key}_{period}.parquet")


class FetchError(Exception):
    pass


class DataFetcher:
    def __init__(self, max_retries: int = 3, backoff_base: float = 1.0):
        self.max_retries = max_retries
        self.backoff_base = backoff_base

    def _download_batch(self, symbols: List[str], period: str = "3mo", interval: str = "1d") -> Dict[str, pd.DataFrame]:
        if yf is None:
            raise FetchError("yfinance not available in environment")

        symbols_up = [s.upper() for s in symbols]
        cache_file = cache_path_for(symbols_up, period)
        # Use cache if fresh (5 minutes)
        if os.path.exists(cache_file):
            mtime = datetime.fromtimestamp(os.path.getmtime(cache_file))
            if datetime.now() - mtime < timedelta(minutes=5):
                try:
                    df_all = pd.read_parquet(cache_file)
                    # reconstruct split per symbol
                    result = {}
                    for sym in symbols_up:
                        if (sym,) in df_all.columns.nlevels and isinstance(df_all.columns, pd.MultiIndex):
                            # MultiIndex produced by yfinance when group_by='ticker'
                            result[sym] = df_all[sym].copy()
                        else:
                            # fallback: assume single frame with ticker columns
                            cols = [c for c in df_all.columns if c[0] == sym]
                            if cols:
                                result[sym] = df_all[cols].copy()
                    if result:
                        return result
                except Exception:
                    # ignore cache read errors
                    pass

        # Retry loop with exponential backoff
        attempt = 0
        last_exc = None
        while attempt < self.max_retries:
            try:
                # batch download - this reduces per-symbol requests
                # threads=False avoids threading issues on Windows/CI
                df = yf.download(
                    tickers=" ".join(symbols_up),
                    period=period,
                    interval=interval,
                    group_by="ticker",
                    threads=False,
                    progress=False,
                    timeout=15
                )
                if df is None or df.empty:
                    raise FetchError("yfinance returned no data")
                # Save parquet cache: easier to restore
                try:
                    # Some yfinance outputs are multiindex (ticker, column)
                    df.to_parquet(cache_file, index=True)
                except Exception:
                    pass

                # Convert to per-symbol dict
                result = {}
                # if yfinance returned grouped by ticker
                if isinstance(df.columns, pd.MultiIndex):
                    for sym in symbols_up:
                        if sym in df.columns.get_level_values(0):
                            # get columns for symbol
                            try:
                                df_sym = df[sym].copy()
                                result[sym] = df_sym
                            except Exception:
                                continue
                else:
                    # Single-level columns - assume common columns with ticker as part of column name
                    for sym in symbols_up:
                        cols = [c for c in df.columns if sym in str(c)]
                        if cols:
                            result[sym] = df[cols].copy()
                # final fallback: try splitting by top-level if group_by didn't work
                if not result:
                    # yfinance sometimes returns standard OHLC with symbol in the index? attempt to parse index
                    for sym in symbols_up:
                        # attempt to slice by symbol in column name
                        cols = [c for c in df.columns if sym in str(c)]
                        if cols:
                            result[sym] = df[cols].copy()

                if not result:
                    # As last resort if we couldn't split, return an empty dict to signal failure
                    raise FetchError("Could not parse yfinance response into symbols")

                return result

            except Exception as e:
                last_exc = e
                attempt += 1
                sleep_for = self.backoff_base * (2 ** (attempt - 1))
                # brief jitter
                time.sleep(sleep_for + (0.1 * attempt))
        raise FetchError(f"Failed to download after {self.max_retries} attempts: {last_exc}")

    def fetch_stock_data(self, symbols: List[str], period: str = "3mo", interval: str = "1d") -> Dict[str, pd.DataFrame]:
        try:
            data = self._download_batch(symbols, period=period, interval=interval)
            # enrich: add Returns, SMA, Volatility etc. per symbol
            for sym, df in list(data.items()):
                try:
                    # ensure standard column names present
                    if "Close" in df.columns:
                        df = df.rename(columns={c: c for c in df.columns})
                    # compute returns if possible
                    if "Close" in df.columns:
                        df["Returns"] = df["Close"].pct_change()
                        df["SMA_20"] = df["Close"].rolling(window=20).mean()
                        df["SMA_50"] = df["Close"].rolling(window=50).mean()
                        df["Volatility"] = df["Returns"].rolling(window=20).std() * (252 ** 0.5)
                    data[sym] = df
                except Exception:
                    # leave as-is if computations fail
                    data[sym] = df
            return data
        except FetchError as e:
            # fallback to sample
            sample = load_sample_summary()
            if sample:
                # we return empty dict to indicate sample; caller's try/except should read sample file
                return {}
            # re-raise if no sample available
            raise

    def fetch_current_prices(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        Simple current price fetch using the last available 'Close' from historical batch.
        Avoids per-symbol quoteSummary calls that trigger 429s.
        """
        try:
            data = self._download_batch(symbols, period="7d", interval="1d")
        except Exception:
            data = {}

        prices = {}
        for sym in symbols:
            s = sym.upper()
            if s in data and not data[s].empty and "Close" in data[s].columns:
                last = data[s]["Close"].dropna()
                if not last.empty:
                    price = float(last.iloc[-1])
                    prices[s] = {"price": price, "source": "close"}
                    continue
            # fallback to None
            prices[s] = {"price": None, "source": "none"}
        return prices

    def fetch_news(self, symbols: List[str], days: int = 7) -> Dict[str, List[Dict]]:
        # For hackathon/demo: avoid news fetching if no NEWS_API_KEY to reduce external calls.
        # If you want real news, set NEWS_API_KEY in .env and implement calls.
        return {s.upper(): [] for s in symbols}


if __name__ == "__main__":
    # quick local test
    dfetch = DataFetcher()
    syms = ["AAPL", "MSFT", "GOOGL"]
    try:
        d = dfetch.fetch_stock_data(syms, period="1mo")
        print("Fetched symbols:", list(d.keys()))
        for k, v in d.items():
            print(k, "rows:", len(v))
        print("Prices:", dfetch.fetch_current_prices(syms))
    except Exception as ex:
        print("Fetch failed:", ex)
        s = load_sample_summary()
        print("Loaded sample:", bool(s))
