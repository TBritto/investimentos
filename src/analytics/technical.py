from __future__ import annotations

import pandas as pd


def add_moving_averages(data: pd.DataFrame, periods: list[int]) -> pd.DataFrame:
    result = data.copy()
    for period in periods:
        result[f"MM_{period}"] = result["close"].rolling(window=period).mean()
    return result


def add_bollinger_bands(data: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    result = data.copy()
    result["BB_media"] = result["close"].rolling(window=window).mean()
    result["BB_desvio"] = result["close"].rolling(window=window).std()
    result["BB_superior"] = result["BB_media"] + (result["BB_desvio"] * 2)
    result["BB_inferior"] = result["BB_media"] - (result["BB_desvio"] * 2)
    return result


def add_rsi(data: pd.DataFrame, periods: int = 14) -> pd.DataFrame:
    result = data.copy()
    delta = result["close"].diff()
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)
    avg_gain = gain.ewm(com=periods - 1, min_periods=periods).mean()
    avg_loss = loss.ewm(com=periods - 1, min_periods=periods).mean()
    rs = avg_gain / avg_loss
    result["RSI"] = 100 - (100 / (1 + rs))
    return result
