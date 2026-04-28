from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd
import requests


BCB_SGS_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados"
CACHE_DIR = Path("data/raw/bcb")
SELIC_CODE = 432
IPCA_CODE = 433
USDBRL_CODE = 1


class BCBClientError(RuntimeError):
    """Erro amigavel para falhas no Banco Central SGS."""


def get_sgs_series(
    code: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    cache_path = _cache_path(code, start_date, end_date)
    if cache_path.exists():
        return _read_cache(cache_path)

    params = {"formato": "json"}
    if start_date:
        params["dataInicial"] = _format_date_for_bcb(start_date)
    if end_date:
        params["dataFinal"] = _format_date_for_bcb(end_date)

    try:
        response = requests.get(BCB_SGS_URL.format(code=code), params=params, timeout=30)
        response.raise_for_status()
    except requests.HTTPError as exc:
        status_code = exc.response.status_code if exc.response is not None else "desconhecido"
        raise BCBClientError(f"Erro HTTP {status_code} ao buscar serie SGS {code}.") from exc
    except requests.RequestException as exc:
        raise BCBClientError(f"Nao foi possivel buscar serie SGS {code}: {exc}") from exc

    try:
        payload = response.json()
    except ValueError as exc:
        raise BCBClientError(f"Resposta invalida do Banco Central para serie SGS {code}.") from exc

    data = _normalize_payload(payload, code)
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
        raise BCBClientError(f"Formato inesperado para serie SGS {code}.")

    data = pd.DataFrame(payload)
    if data.empty:
        return pd.DataFrame(columns=["date", "value", "code"])
    if "data" not in data or "valor" not in data:
        raise BCBClientError(f"Campos obrigatorios ausentes na serie SGS {code}.")

    normalized = pd.DataFrame(
        {
            "date": pd.to_datetime(data["data"], format="%d/%m/%Y", errors="coerce"),
            "value": pd.to_numeric(data["valor"].str.replace(",", ".", regex=False), errors="coerce"),
            "code": code,
        }
    )
    return normalized.dropna(subset=["date", "value"]).reset_index(drop=True)


def _format_date_for_bcb(value: str) -> str:
    date = pd.to_datetime(value, errors="raise")
    return date.strftime("%d/%m/%Y")


def _cache_path(code: int, start_date: Optional[str], end_date: Optional[str]) -> Path:
    start = _safe_cache_token(start_date or "inicio")
    end = _safe_cache_token(end_date or "fim")
    return CACHE_DIR / str(code) / f"{start}_{end}.csv"


def _safe_cache_token(value: str) -> str:
    return value.replace("/", "-").replace("\\", "-").replace(":", "-").replace(" ", "_")


def _read_cache(path: Path) -> pd.DataFrame:
    data = pd.read_csv(path)
    data["date"] = pd.to_datetime(data["date"])
    data["value"] = pd.to_numeric(data["value"])
    data["code"] = pd.to_numeric(data["code"]).astype(int)
    return data[["date", "value", "code"]]


def _write_cache(data: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(path, index=False)
