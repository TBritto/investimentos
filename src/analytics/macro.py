from __future__ import annotations

import pandas as pd


def get_period_start(period: str, today: pd.Timestamp | None = None) -> str | None:
    current_day = today or pd.Timestamp.today()
    if period == "1 ano":
        return (current_day - pd.DateOffset(years=1)).strftime("%Y-%m-%d")
    if period == "5 anos":
        return (current_day - pd.DateOffset(years=5)).strftime("%Y-%m-%d")
    return None


def latest_value(data: pd.DataFrame) -> float | None:
    if data.empty:
        return None
    return float(data.sort_values("date").iloc[-1]["value"])
