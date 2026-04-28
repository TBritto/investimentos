from __future__ import annotations

import datetime as dt
from typing import Optional

import pandas as pd

try:
    from openbb import obb
except ImportError:
    obb = None


class OpenBBClientError(RuntimeError):
    """Erro amigavel para falhas na camada OpenBB."""


def get_equity_quote(symbol: str) -> pd.DataFrame:
    clean_symbol = _normalize_symbol(symbol)
    _ensure_openbb_available()
    try:
        return obb.equity.price.quote(symbol=clean_symbol).to_dataframe()
    except Exception as exc:
        raise OpenBBClientError(f"Nao foi possivel buscar cotacao para {clean_symbol}: {exc}") from exc


def get_equity_history(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    clean_symbol = _normalize_symbol(symbol)
    _ensure_openbb_available()
    kwargs = {"symbol": clean_symbol}
    if start_date:
        kwargs["start_date"] = start_date
    if end_date:
        kwargs["end_date"] = end_date

    try:
        data = obb.equity.price.historical(**kwargs).to_dataframe()
    except Exception as exc:
        raise OpenBBClientError(f"Nao foi possivel buscar historico para {clean_symbol}: {exc}") from exc

    if data.empty:
        return pd.DataFrame(columns=["date", clean_symbol])

    normalized = data.copy()
    if "close" not in normalized.columns:
        raise OpenBBClientError(f"Historico de {clean_symbol} sem coluna de fechamento.")
    normalized = normalized.reset_index().rename(columns={"index": "date"})
    if "date" not in normalized.columns:
        normalized = normalized.rename(columns={normalized.columns[0]: "date"})
    return normalized[["date", "close"]].rename(columns={"close": clean_symbol})


def compare_equities(
    symbols: list[str],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    clean_symbols = [_normalize_symbol(symbol) for symbol in symbols if symbol.strip()]
    if len(clean_symbols) < 2:
        raise OpenBBClientError("Informe ao menos dois tickers para comparar.")

    series = [
        get_equity_history(symbol, start_date=start_date, end_date=end_date).set_index("date")
        for symbol in clean_symbols
    ]
    comparison = pd.concat(series, axis=1).reset_index()
    return comparison


def fetch_price_history(
    symbol: str,
    start_date: dt.date,
    end_date: dt.date,
) -> pd.DataFrame:
    """Busca historico de precos pelo OpenBB."""
    try:
        _ensure_openbb_available()
        return obb.equity.price.historical(
            symbol=_normalize_symbol(symbol),
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
        ).to_dataframe()
    except Exception as exc:
        raise OpenBBClientError(f"Nao foi possivel buscar historico para {symbol}: {exc}") from exc


def fetch_fundamental_statement(symbol: str, statement_type: str) -> pd.DataFrame:
    """Busca demonstrativos fundamentais quando o provedor configurado permitir."""
    clean_symbol = _normalize_symbol(symbol)
    _ensure_openbb_available()
    try:
        if statement_type == "DRE":
            return obb.equity.fundamental.income(
                symbol=clean_symbol, provider="fmp"
            ).to_dataframe()
        if statement_type == "Balanco":
            return obb.equity.fundamental.balance(
                symbol=clean_symbol, provider="fmp"
            ).to_dataframe()
        if statement_type == "Fluxo de caixa":
            return obb.equity.fundamental.cash(symbol=clean_symbol, provider="fmp").to_dataframe()
    except Exception as exc:
        raise OpenBBClientError(
            f"Nao foi possivel buscar fundamentos para {clean_symbol}. "
            "Verifique se o provider esta configurado."
        ) from exc

    raise ValueError(f"Tipo de demonstrativo desconhecido: {statement_type}")


def fetch_financial_ratios(symbol: str) -> pd.DataFrame:
    """Busca indicadores financeiros pelo OpenBB."""
    clean_symbol = _normalize_symbol(symbol)
    _ensure_openbb_available()
    try:
        return obb.equity.fundamental.ratios(symbol=clean_symbol).to_dataframe()
    except Exception as exc:
        raise OpenBBClientError(
            f"Nao foi possivel buscar indicadores para {clean_symbol}. "
            "Verifique se o provider esta configurado."
        ) from exc


def _normalize_symbol(symbol: str) -> str:
    clean_symbol = symbol.strip().upper()
    if not clean_symbol:
        raise OpenBBClientError("Ticker vazio.")
    return clean_symbol


def _ensure_openbb_available() -> None:
    if obb is None:
        raise OpenBBClientError(
            "OpenBB nao esta instalado ou configurado neste ambiente. "
            "Instale as dependencias e configure o provider quando necessario."
        )
