from __future__ import annotations

import pandas as pd


def calculate_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Calcula retornos periodicos simples: preco_t / preco_t-1 - 1.

    Linhas sem preco anterior ou com valores ausentes sao removidas apos o calculo.
    O DataFrame de entrada nao e modificado.
    """
    clean_prices = prices.copy()
    returns = clean_prices.pct_change()
    return returns.dropna(how="all")


def cumulative_return(returns: pd.Series) -> float:
    """Calcula retorno acumulado: produto de (1 + retorno_t) - 1."""
    clean_returns = returns.dropna()
    if clean_returns.empty:
        return 0.0
    return float((1 + clean_returns).prod() - 1)
