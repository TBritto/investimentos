import pandas as pd
import pytest

from src.analytics.returns import calculate_returns, cumulative_return
from src.analytics.risk import (
    annualized_volatility,
    correlation_matrix,
    drawdown_series,
    max_drawdown,
    sharpe_ratio,
)


def test_calculate_returns_does_not_mutate_input_and_handles_nan() -> None:
    prices = pd.DataFrame({"A": [100.0, 110.0, None, 121.0], "B": [50.0, 55.0, 60.5, 66.55]})
    original = prices.copy(deep=True)

    returns = calculate_returns(prices)

    pd.testing.assert_frame_equal(prices, original)
    assert returns["A"].dropna().iloc[0] == pytest.approx(0.10)
    assert returns["B"].iloc[0] == pytest.approx(0.10)


def test_cumulative_return_compounds_period_returns() -> None:
    returns = pd.Series([0.10, -0.05, 0.02, None])

    assert cumulative_return(returns) == pytest.approx((1.10 * 0.95 * 1.02) - 1)


def test_annualized_volatility_scales_standard_deviation() -> None:
    returns = pd.Series([0.01, -0.01, 0.02, -0.02])

    assert annualized_volatility(returns, periods_per_year=4) == pytest.approx(returns.std() * 2)


def test_drawdown_series_and_max_drawdown() -> None:
    prices = pd.Series([100.0, 120.0, 90.0, 150.0])

    drawdowns = drawdown_series(prices)

    assert drawdowns.tolist() == pytest.approx([0.0, 0.0, -0.25, 0.0])
    assert max_drawdown(prices) == pytest.approx(-0.25)


def test_correlation_matrix_uses_returns_columns() -> None:
    returns = pd.DataFrame({"A": [0.01, 0.02, 0.03], "B": [0.02, 0.04, 0.06]})

    matrix = correlation_matrix(returns)

    assert matrix.loc["A", "B"] == pytest.approx(1.0)


def test_sharpe_ratio_returns_zero_for_empty_or_flat_series() -> None:
    assert sharpe_ratio(pd.Series(dtype=float)) == 0.0
    assert sharpe_ratio(pd.Series([0.01, 0.01, 0.01])) == 0.0


def test_sharpe_ratio_uses_excess_return() -> None:
    returns = pd.Series([0.02, 0.01, -0.01, 0.03])

    expected = ((returns - 0.04 / 4).mean() / returns.std()) * 2

    assert sharpe_ratio(returns, risk_free_rate=0.04, periods_per_year=4) == pytest.approx(expected)
