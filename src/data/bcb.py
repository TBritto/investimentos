from __future__ import annotations

import json
import io
from pathlib import Path
from typing import Optional
from urllib.parse import urlencode

import pandas as pd

from src.data.errors import DataParsingError, DataSourceError, DataValidationError
from src.data.http import get_url
from src.storage.cache import cache_exists, load_cache, save_cache

BCB_SGS_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados"
CACHE_DIR = Path("data/raw/bcb")
SELIC_CODE = 432
IPCA_CODE = 433
USDBRL_CODE = 1


class BCBClientError(DataSourceError):
    """Erro amigavel para falhas no Banco Central SGS."""


def get_sgs_series(
    code: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    use_cache: bool = True,
) -> pd.DataFrame:
    """Busca uma serie publica do Banco Central SGS.

    Retorna um DataFrame normalizado com as colunas `date`, `value` e `code`.
    Quando `use_cache=True`, usa e grava arquivos em `data/raw/bcb/` por codigo
    e intervalo de datas.
    """
    cache_path = _cache_path(code, start_date, end_date)
    if use_cache and cache_exists(str(cache_path)):
        return _read_cache(cache_path)

    params = {"formato": "json"}
    if start_date:
        params["dataInicial"] = _format_date_for_bcb(start_date)
    if end_date:
        params["dataFinal"] = _format_date_for_bcb(end_date)

    url = f"{BCB_SGS_URL.format(code=code)}?{urlencode(params)}"

    try:
        payload = json.loads(get_url(url, timeout=30).decode("utf-8"))
    except DataSourceError as exc:
        raise BCBClientError(f"Nao foi possivel buscar serie SGS {code}: {exc}") from exc
    except (UnicodeDecodeError, ValueError) as exc:
        raise BCBClientError(f"Resposta invalida do Banco Central para serie SGS {code}.") from exc

    data = _normalize_payload(payload, code)
    if use_cache:
        _write_cache(data, cache_path)
    return data


def get_selic(start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
    return get_sgs_series(SELIC_CODE, start_date=start_date, end_date=end_date)


def get_ipca(start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
    return get_sgs_series(IPCA_CODE, start_date=start_date, end_date=end_date)


def get_usdbrl(start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
    return get_sgs_series(USDBRL_CODE, start_date=start_date, end_date=end_date)


def _normalize_payload(payload: object, code: int) -> pd.DataFrame:
    if not isinstance(payload, list):
        raise DataParsingError(f"Formato inesperado para serie SGS {code}.")

    data = pd.DataFrame(payload)
    if data.empty:
        raise BCBClientError(f"Resposta vazia do Banco Central para serie SGS {code}.")
    if "data" not in data or "valor" not in data:
        raise DataValidationError(f"Campos obrigatorios ausentes na serie SGS {code}.")

    raw_values = data["valor"].astype(str).str.replace(",", ".", regex=False)
    normalized = pd.DataFrame(
        {
            "date": pd.to_datetime(data["data"], format="%d/%m/%Y", errors="coerce"),
            "value": pd.to_numeric(raw_values, errors="coerce"),
            "code": code,
        }
    )
    invalid_dates = int(normalized["date"].isna().sum())
    invalid_values = int(normalized["value"].isna().sum())
    if invalid_dates:
        raise BCBClientError(f"Data invalida na resposta da serie SGS {code}.")
    if invalid_values:
        raise BCBClientError(f"Valor numerico invalido na resposta da serie SGS {code}.")

    return normalized.reset_index(drop=True)


def _format_date_for_bcb(value: str) -> str:
    try:
        date = pd.to_datetime(value, errors="raise")
    except Exception as exc:
        raise BCBClientError(f"Data invalida para consulta SGS: {value}. Use YYYY-MM-DD.") from exc
    return date.strftime("%d/%m/%Y")


def _cache_path(code: int, start_date: Optional[str], end_date: Optional[str]) -> Path:
    start = _safe_cache_token(start_date or "inicio")
    end = _safe_cache_token(end_date or "fim")
    return CACHE_DIR / str(code) / f"{start}_{end}.csv"


def _safe_cache_token(value: str) -> str:
    return value.replace("/", "-").replace("\\", "-").replace(":", "-").replace(" ", "_")


def _read_cache(path: Path) -> pd.DataFrame:
    cached = load_cache(str(path))
    if cached is None:
        raise BCBClientError(f"Cache ausente para serie SGS: {path}")
    if isinstance(cached, bytes):
        data = pd.read_csv(io.BytesIO(cached))
    else:
        data = pd.read_csv(io.StringIO(cached))
    data["date"] = pd.to_datetime(data["date"])
    data["value"] = pd.to_numeric(data["value"])
    data["code"] = pd.to_numeric(data["code"]).astype(int)
    return data[["date", "value", "code"]]


def _write_cache(data: pd.DataFrame, path: Path) -> None:
    save_cache(str(path), data.to_csv(index=False))
