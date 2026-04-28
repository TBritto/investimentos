from __future__ import annotations

import math

import pandas as pd


def parse_weights(raw_weights: str) -> list[float]:
    return [float(weight.strip()) for weight in raw_weights.split(",") if weight.strip()]


def validate_portfolio_inputs(tickers: list[str], weights: list[float]) -> None:
    if len(tickers) != len(weights):
        raise ValueError("A quantidade de ativos e pesos precisa ser igual.")
    if not math.isclose(sum(weights), 1.0, rel_tol=1e-9, abs_tol=1e-9):
        raise ValueError("A soma dos pesos precisa ser 1.")


def calculate_portfolio_returns(prices: pd.DataFrame, weights: list[float]) -> pd.Series:
    returns = prices.pct_change().dropna()
    return returns.dot(weights)


def calculate_risk_metrics(portfolio_returns: pd.Series) -> dict[str, float]:
    volatility = portfolio_returns.std() * (252 ** 0.5)
    annual_return = portfolio_returns.mean() * 252
    sharpe_ratio = annual_return / volatility if volatility else 0.0
    return {
        "annual_return": annual_return,
        "annual_volatility": volatility,
        "sharpe_ratio": sharpe_ratio,
    }
