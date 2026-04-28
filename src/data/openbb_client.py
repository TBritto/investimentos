from __future__ import annotations

import datetime as dt

import pandas as pd
from openbb import obb


def fetch_price_history(
    symbol: str,
    start_date: dt.date,
    end_date: dt.date,
) -> pd.DataFrame:
    """Busca historico de precos pelo OpenBB."""
    return obb.equity.price.historical(
        symbol=symbol.upper(),
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
    ).to_dataframe()


def fetch_fundamental_statement(symbol: str, statement_type: str) -> pd.DataFrame:
    """Busca demonstrativos fundamentais quando o provedor configurado permitir."""
    if statement_type == "DRE":
        return obb.equity.fundamental.income(symbol=symbol.upper(), provider="fmp").to_dataframe()
    if statement_type == "Balanco":
        return obb.equity.fundamental.balance(symbol=symbol.upper(), provider="fmp").to_dataframe()
    if statement_type == "Fluxo de caixa":
        return obb.equity.fundamental.cash(symbol=symbol.upper(), provider="fmp").to_dataframe()

    raise ValueError(f"Tipo de demonstrativo desconhecido: {statement_type}")


def fetch_financial_ratios(symbol: str) -> pd.DataFrame:
    """Busca indicadores financeiros pelo OpenBB."""
    return obb.equity.fundamental.ratios(symbol=symbol.upper()).to_dataframe()
