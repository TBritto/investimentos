import pandas as pd
import pytest

from src.analytics.portfolio import calculate_risk_metrics, parse_weights, validate_portfolio_inputs


def test_parse_weights() -> None:
    assert parse_weights("0.5, 0.3,0.2") == [0.5, 0.3, 0.2]


def test_validate_portfolio_inputs_rejects_unbalanced_weights() -> None:
    with pytest.raises(ValueError, match="soma dos pesos"):
        validate_portfolio_inputs(["AAPL", "MSFT"], [0.8, 0.1])


def test_calculate_risk_metrics_returns_expected_keys() -> None:
    returns = pd.Series([0.01, -0.02, 0.015, 0.005])
    metrics = calculate_risk_metrics(returns)

    assert set(metrics) == {"annual_return", "annual_volatility", "sharpe_ratio"}
