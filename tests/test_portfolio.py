import pandas as pd
import pytest

from src.analytics.portfolio import (
    calculate_portfolio_composition,
    calculate_risk_metrics,
    parse_weights,
    validate_portfolio_csv_columns,
    validate_portfolio_inputs,
)


def test_parse_weights() -> None:
    assert parse_weights("0.5, 0.3,0.2") == [0.5, 0.3, 0.2]


def test_validate_portfolio_inputs_rejects_unbalanced_weights() -> None:
    with pytest.raises(ValueError, match="soma dos pesos"):
        validate_portfolio_inputs(["AAPL", "MSFT"], [0.8, 0.1])


def test_calculate_risk_metrics_returns_expected_keys() -> None:
    returns = pd.Series([0.01, -0.02, 0.015, 0.005])
    metrics = calculate_risk_metrics(returns)

    assert set(metrics) == {"annual_return", "annual_volatility", "sharpe_ratio"}


def test_validate_portfolio_csv_columns_rejects_missing_columns() -> None:
    data = pd.DataFrame({"ativo": ["AAPL"], "quantidade": [1]})

    with pytest.raises(ValueError, match="preco_medio"):
        validate_portfolio_csv_columns(data)


def test_calculate_portfolio_composition_returns_asset_and_class_percentages() -> None:
    data = pd.DataFrame(
        {
            "ativo": ["aapl", "msft", "tesouro"],
            "quantidade": [2, 1, 3],
            "preco_medio": [100.0, 300.0, 100.0],
            "classe": ["Acoes", "Acoes", "Renda Fixa"],
        }
    )

    normalized, by_asset, by_class, total_invested = calculate_portfolio_composition(data)

    assert total_invested == 800.0
    assert normalized.loc[0, "ativo"] == "AAPL"
    assert normalized["valor_investido"].tolist() == [200.0, 300.0, 300.0]
    assert by_asset.loc[0, "percentual"] == 0.375
    assert by_class.loc[by_class["classe"] == "Acoes", "percentual"].iloc[0] == 0.625
