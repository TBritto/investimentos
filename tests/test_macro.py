import pandas as pd

from src.analytics.macro import get_period_start, latest_value


def test_get_period_start_returns_expected_dates() -> None:
    today = pd.Timestamp("2026-04-28")

    assert get_period_start("1 ano", today=today) == "2025-04-28"
    assert get_period_start("5 anos", today=today) == "2021-04-28"
    assert get_period_start("maximo", today=today) is None


def test_latest_value_returns_last_by_date() -> None:
    data = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-02", "2024-01-01"]),
            "value": [2.0, 1.0],
            "code": [1, 1],
        }
    )

    assert latest_value(data) == 2.0
