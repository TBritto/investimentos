from __future__ import annotations

import datetime as dt
import os
from typing import Optional

import pandas as pd

try:
    from openbb import obb
except ImportError:
    obb = None


class OpenBBClientError(RuntimeError):
    """Erro amigavel para falhas na camada OpenBB."""


NORMALIZED_COLUMNS = ["date", "symbol", "open", "high", "low", "close", "volume"]
COLUMN_ALIASES = {
    "datetime": "date",
    "timestamp": "date",
    "time": "date",
    "ticker": "symbol",
    "adj close": "adjusted_close",
    "adj_close": "adjusted_close",
}
CREDENTIAL_ENV_MAP = {
    "FMP_API_KEY": "fmp_api_key",
}


def get_equity_quote(symbol: str) -> pd.DataFrame:
    clean_symbol = _normalize_symbol(symbol)
    _ensure_openbb_available()
    kwargs = {"symbol": clean_symbol}
    provider = _resolve_provider(None)
    if provider:
        kwargs["provider"] = provider

    try:
        data = _to_dataframe(obb.equity.price.quote(**kwargs))
    except Exception as exc:
        raise _wrap_openbb_error("cotacao", clean_symbol, provider, exc) from exc

    return _normalize_market_frame(data, clean_symbol, "cotacao")


def get_equity_history(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    provider: Optional[str] = None,
) -> pd.DataFrame:
    clean_symbol = _normalize_symbol(symbol)
    _ensure_openbb_available()
    kwargs = {"symbol": clean_symbol}
    if start_date:
        kwargs["start_date"] = start_date
    if end_date:
        kwargs["end_date"] = end_date
    resolved_provider = _resolve_provider(provider)
    if resolved_provider:
        kwargs["provider"] = resolved_provider

    try:
        data = _to_dataframe(obb.equity.price.historical(**kwargs))
    except Exception as exc:
        raise _wrap_openbb_error("historico", clean_symbol, resolved_provider, exc) from exc

    return _normalize_market_frame(data, clean_symbol, "historico")


def compare_equities(
    symbols: list[str],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    provider: Optional[str] = None,
) -> pd.DataFrame:
    clean_symbols = [_normalize_symbol(symbol) for symbol in symbols if symbol.strip()]
    if len(clean_symbols) < 2:
        raise OpenBBClientError("Informe ao menos dois tickers para comparar.")

    frames = [
        get_equity_history(symbol, start_date=start_date, end_date=end_date, provider=provider)
        for symbol in clean_symbols
    ]
    return pd.concat(frames, ignore_index=True)


def fetch_price_history(
    symbol: str,
    start_date: dt.date,
    end_date: dt.date,
    provider: Optional[str] = None,
) -> pd.DataFrame:
    """Busca historico de precos pelo OpenBB."""
    try:
        return get_equity_history(
            symbol=_normalize_symbol(symbol),
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            provider=provider,
        )
    except OpenBBClientError:
        raise


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
    _apply_openbb_credentials()


def _resolve_provider(provider: Optional[str]) -> Optional[str]:
    resolved = provider or os.getenv("OPENBB_PROVIDER")
    if resolved is None:
        return None
    resolved = resolved.strip()
    return resolved or None


def _apply_openbb_credentials() -> None:
    credentials = getattr(getattr(obb, "user", None), "credentials", None)
    if credentials is None:
        return

    for env_name, attribute_name in CREDENTIAL_ENV_MAP.items():
        value = os.getenv(env_name)
        if value:
            setattr(credentials, attribute_name, value)


def _to_dataframe(result: object) -> pd.DataFrame:
    if hasattr(result, "to_dataframe"):
        data = result.to_dataframe()
    else:
        data = result

    if not isinstance(data, pd.DataFrame):
        raise OpenBBClientError("Resposta inesperada do OpenBB: nao foi retornado um DataFrame.")
    return data


def _normalize_market_frame(data: pd.DataFrame, symbol: str, context: str) -> pd.DataFrame:
    if data.empty:
        raise OpenBBClientError(f"Resposta vazia do OpenBB para {context} de {symbol}.")

    normalized = data.copy()
    normalized = _promote_index_to_date(normalized)
    normalized = _rename_known_columns(normalized)

    if "symbol" not in normalized.columns:
        normalized.insert(0, "symbol", symbol)
    else:
        normalized["symbol"] = normalized["symbol"].fillna(symbol).astype(str).str.upper()

    if "date" in normalized.columns:
        normalized["date"] = pd.to_datetime(normalized["date"], errors="coerce")
        if normalized["date"].isna().any():
            raise OpenBBClientError(f"Data invalida na resposta do OpenBB para {symbol}.")

    for column in ["open", "high", "low", "close", "volume"]:
        if column in normalized.columns:
            original = normalized[column]
            converted = pd.to_numeric(original, errors="coerce")
            if (converted.isna() & original.notna()).any():
                raise OpenBBClientError(
                    f"Valor numerico invalido na coluna {column} da resposta do OpenBB para {symbol}."
                )
            normalized[column] = converted

    ordered_columns = [column for column in NORMALIZED_COLUMNS if column in normalized.columns]
    extra_columns = [column for column in normalized.columns if column not in ordered_columns]
    return normalized[ordered_columns + extra_columns].reset_index(drop=True)


def _promote_index_to_date(data: pd.DataFrame) -> pd.DataFrame:
    if "date" in {str(column).lower() for column in data.columns}:
        return data

    index_name = data.index.name
    if isinstance(data.index, pd.DatetimeIndex) or (
        index_name is not None and index_name.lower() in {"date", "datetime", "timestamp"}
    ):
        promoted = data.reset_index()
        return promoted.rename(columns={promoted.columns[0]: "date"})

    return data.reset_index(drop=True)


def _rename_known_columns(data: pd.DataFrame) -> pd.DataFrame:
    rename_map = {}
    seen_columns = set()
    for column in data.columns:
        key = str(column).strip().lower()
        canonical = COLUMN_ALIASES.get(key, key.replace(" ", "_"))
        if canonical in seen_columns:
            continue
        seen_columns.add(canonical)
        if canonical != column:
            rename_map[column] = canonical
    return data.rename(columns=rename_map)


def _wrap_openbb_error(
    context: str,
    symbol: str,
    provider: Optional[str],
    exc: Exception,
) -> OpenBBClientError:
    provider_message = f" com provider '{provider}'" if provider else ""
    raw_message = str(exc) or exc.__class__.__name__
    lowered = raw_message.lower()
    if "not found" in lowered or "no results" in lowered or "empty" in lowered:
        return OpenBBClientError(f"Ticker {symbol} nao encontrado no OpenBB{provider_message}.")
    if "provider" in lowered or "credential" in lowered or "api key" in lowered:
        return OpenBBClientError(
            f"Provider OpenBB indisponivel ou nao configurado{provider_message}: {raw_message}"
        )
    return OpenBBClientError(f"Nao foi possivel buscar {context} para {symbol}{provider_message}: {raw_message}")
