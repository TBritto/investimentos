from __future__ import annotations

import io
import re
import unicodedata
import zipfile
from pathlib import Path
from typing import Optional

import pandas as pd
import requests


CVM_BASE_URL = "https://dados.cvm.gov.br/dados/FI"
FUND_REGISTRY_URL = f"{CVM_BASE_URL}/CAD/DADOS/cad_fi.csv"
DAILY_REPORT_URL_TEMPLATE = f"{CVM_BASE_URL}/DOC/INF_DIARIO/DADOS/inf_diario_fi_{{year}}{{month:02d}}.zip"
CACHE_DIR = Path("data/raw/cvm")

DAILY_REPORT_COLUMNS = [
    "cnpj_fundo",
    "data_competencia",
    "valor_cota",
    "patrimonio_liquido",
    "captacao_dia",
    "resgate_dia",
    "numero_cotistas",
]

DAILY_COLUMN_MAP = {
    "cnpj_fundo": "cnpj_fundo",
    "dt_comptc": "data_competencia",
    "data_competencia": "data_competencia",
    "vl_quota": "valor_cota",
    "valor_cota": "valor_cota",
    "vl_patrim_liq": "patrimonio_liquido",
    "patrimonio_liquido": "patrimonio_liquido",
    "captc_dia": "captacao_dia",
    "captacao_dia": "captacao_dia",
    "resg_dia": "resgate_dia",
    "resgate_dia": "resgate_dia",
    "nr_cotst": "numero_cotistas",
    "numero_cotistas": "numero_cotistas",
}


class CVMClientError(RuntimeError):
    """Erro amigavel para falhas na camada de Dados Abertos CVM."""


def normalize_cnpj(cnpj: str) -> str:
    digits = re.sub(r"\D", "", str(cnpj or ""))
    if len(digits) != 14:
        raise CVMClientError("CNPJ invalido. Informe 14 digitos.")
    return digits


def get_fund_registry(use_cache: bool = True) -> pd.DataFrame:
    cache_path = CACHE_DIR / "cad_fi.csv"
    raw_content = _get_cached_or_download(FUND_REGISTRY_URL, cache_path, use_cache)
    data = _read_csv_bytes(raw_content, context="cadastro de fundos")
    normalized = _normalize_columns(data)

    if "cnpj_fundo" not in normalized.columns:
        raise CVMClientError("CSV de cadastro CVM sem coluna esperada de CNPJ do fundo.")

    normalized["cnpj_fundo"] = normalized["cnpj_fundo"].map(normalize_cnpj)
    return normalized


def search_funds(query: str) -> pd.DataFrame:
    clean_query = str(query or "").strip()
    if not clean_query:
        return pd.DataFrame()

    registry = get_fund_registry()
    query_digits = re.sub(r"\D", "", clean_query)
    text_query = _strip_accents(clean_query).lower()

    mask = pd.Series(False, index=registry.index)
    if query_digits:
        mask = mask | registry["cnpj_fundo"].str.contains(query_digits, na=False)

    for column in ["denom_social", "nome_fantasia", "nome_comercial"]:
        if column in registry.columns:
            normalized_names = registry[column].fillna("").astype(str).map(lambda value: _strip_accents(value).lower())
            mask = mask | normalized_names.str.contains(text_query, na=False, regex=False)

    return registry.loc[mask].reset_index(drop=True)


def find_fund_by_cnpj(cnpj: str) -> pd.DataFrame:
    clean_cnpj = normalize_cnpj(cnpj)
    registry = get_fund_registry()
    return registry.loc[registry["cnpj_fundo"] == clean_cnpj].reset_index(drop=True)


def get_fund_daily_report(
    year: int,
    month: int,
    use_cache: bool = True,
) -> pd.DataFrame:
    _validate_year_month(year, month)
    url = DAILY_REPORT_URL_TEMPLATE.format(year=year, month=month)
    cache_path = CACHE_DIR / "inf_diario" / f"inf_diario_fi_{year}{month:02d}.zip"
    raw_content = _get_cached_or_download(url, cache_path, use_cache)
    csv_content = _extract_first_csv_from_zip(raw_content, f"informe diario {year}-{month:02d}")
    data = _read_csv_bytes(csv_content, context=f"informe diario {year}-{month:02d}")
    normalized = _normalize_daily_report(data)
    return normalized


def _get_cached_or_download(url: str, cache_path: Path, use_cache: bool) -> bytes:
    if use_cache and cache_path.exists():
        return cache_path.read_bytes()

    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
    except requests.HTTPError as exc:
        status_code = exc.response.status_code if exc.response is not None else "desconhecido"
        if status_code == 404:
            raise CVMClientError(f"Arquivo CVM nao encontrado: {url}") from exc
        raise CVMClientError(f"Erro HTTP {status_code} ao baixar dados CVM.") from exc
    except requests.RequestException as exc:
        raise CVMClientError(f"Nao foi possivel acessar a CVM: {exc}") from exc

    content = response.content
    if not content:
        raise CVMClientError(f"Arquivo CVM vazio: {url}")

    if use_cache:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_bytes(content)

    return content


def _read_csv_bytes(content: bytes, context: str) -> pd.DataFrame:
    errors = []
    for encoding in ("utf-8-sig", "latin1"):
        try:
            return pd.read_csv(io.BytesIO(content), sep=";", decimal=",", encoding=encoding, dtype=str)
        except UnicodeDecodeError as exc:
            errors.append(str(exc))
        except pd.errors.ParserError as exc:
            raise CVMClientError(f"CSV da CVM com formato invalido em {context}: {exc}") from exc

    raise CVMClientError(f"Nao foi possivel ler CSV da CVM em {context}: {'; '.join(errors)}")


def _extract_first_csv_from_zip(content: bytes, context: str) -> bytes:
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            csv_names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
            if not csv_names:
                raise CVMClientError(f"ZIP da CVM sem CSV em {context}.")
            return archive.read(csv_names[0])
    except zipfile.BadZipFile as exc:
        raise CVMClientError(f"ZIP invalido da CVM em {context}.") from exc


def _normalize_daily_report(data: pd.DataFrame) -> pd.DataFrame:
    normalized = _normalize_columns(data)
    normalized = normalized.rename(columns={column: DAILY_COLUMN_MAP.get(column, column) for column in normalized.columns})

    missing_columns = [column for column in DAILY_REPORT_COLUMNS if column not in normalized.columns]
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise CVMClientError(f"CSV de informe diario CVM sem colunas esperadas: {missing}.")

    result = normalized[DAILY_REPORT_COLUMNS].copy()
    result["cnpj_fundo"] = result["cnpj_fundo"].map(normalize_cnpj)
    result["data_competencia"] = pd.to_datetime(result["data_competencia"], errors="coerce")
    if result["data_competencia"].isna().any():
        raise CVMClientError("Data invalida no informe diario da CVM.")

    for column in [
        "valor_cota",
        "patrimonio_liquido",
        "captacao_dia",
        "resgate_dia",
        "numero_cotistas",
    ]:
        converted = pd.to_numeric(result[column].astype(str).str.replace(",", ".", regex=False), errors="coerce")
        if converted.isna().any() and result[column].notna().any():
            raise CVMClientError(f"Valor numerico invalido na coluna {column} do informe diario da CVM.")
        result[column] = converted

    return result.reset_index(drop=True)


def _normalize_columns(data: pd.DataFrame) -> pd.DataFrame:
    normalized = data.copy()
    normalized.columns = [_to_snake_case(column) for column in normalized.columns]
    return normalized


def _to_snake_case(value: object) -> str:
    text = _strip_accents(str(value)).lower().strip()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text


def _strip_accents(value: str) -> str:
    return "".join(
        char for char in unicodedata.normalize("NFKD", value) if not unicodedata.combining(char)
    )


def _validate_year_month(year: int, month: int) -> None:
    if year < 2000 or year > 2100:
        raise CVMClientError("Ano invalido para informe diario CVM.")
    if month < 1 or month > 12:
        raise CVMClientError("Mes invalido para informe diario CVM.")
