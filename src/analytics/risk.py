from __future__ import annotations

import pandas as pd


def annualized_volatility(returns: pd.Series, periods_per_year: int = 252) -> float:
    """Calcula volatilidade anualizada: desvio_padrao(retornos) * sqrt(periodos/ano)."""
    clean_returns = returns.dropna()
    if clean_returns.empty:
        return 0.0
    return float(clean_returns.std() * (periods_per_year ** 0.5))


def drawdown_series(prices: pd.Series) -> pd.Series:
    """Calcula drawdown por periodo: preco / maximo_acumulado - 1."""
    clean_prices = prices.dropna().copy()
    if clean_prices.empty:
        return pd.Series(dtype=float)
    running_max = clean_prices.cummax()
    return (clean_prices / running_max) - 1


def max_drawdown(prices: pd.Series) -> float:
    """Calcula o pior drawdown da serie de precos."""
    drawdowns = drawdown_series(prices)
    if drawdowns.empty:
        return 0.0
    return float(drawdowns.min())


def correlation_matrix(returns: pd.DataFrame) -> pd.DataFrame:
    """Calcula matriz de correlacao de Pearson entre colunas de retornos."""
    clean_returns = returns.copy().dropna(how="all")
    return clean_returns.corr()


def sharpe_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.0,
    periods_per_year: int = 252,
) -> float:
    """Calcula Sharpe simplificado anualizado.

    Formula: (media(retornos - rf_periodico) / desvio_padrao(retornos)) * sqrt(periodos/ano).
    O `risk_free_rate` e anual e convertido para taxa periodica simples.
    """
    clean_returns = returns.dropna()
    if clean_returns.empty:
        return 0.0

    periodic_risk_free_rate = risk_free_rate / periods_per_year
    excess_returns = clean_returns - periodic_risk_free_rate
    volatility = clean_returns.std()
    if volatility == 0:
        return 0.0
    return float((excess_returns.mean() / volatility) * (periods_per_year ** 0.5))
