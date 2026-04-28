from __future__ import annotations

import io
import re
import unicodedata
from pathlib import Path
from typing import Optional

import pandas as pd
import requests


CKAN_PACKAGE_URL = (
    "https://www.tesourotransparente.gov.br/ckan/api/3/action/package_show"
    "?id=taxas-dos-titulos-ofertados-pelo-tesouro-direto"
)
CACHE_DIR = Path("data/raw/tesouro")
PRICE_HISTORY_CACHE = CACHE_DIR / "precotaxatesourodireto.csv"

NORMALIZED_COLUMNS = [
    "nome",
    "tipo",
    "vencimento",
    "taxa_compra",
    "taxa_venda",
    "preco_compra",
    "preco_venda",
    "data_base",
]

COLUMN_ALIASES = {
    "tipo_titulo": "tipo",
    "titulo": "nome",
    "nome_titulo": "nome",
    "nome": "nome",
    "data_vencimento": "vencimento",
    "vencimento": "vencimento",
    "taxa_compra_manha": "taxa_compra",
    "taxa_compra": "taxa_compra",
    "taxa_venda_manha": "taxa_venda",
    "taxa_venda": "taxa_venda",
    "pu_compra_manha": "preco_compra",
    "preco_compra": "preco_compra",
    "pu_venda_manha": "preco_venda",
    "preco_venda": "preco_venda",
    "data_base": "data_base",
}


class TesouroClientError(RuntimeError):
    """Erro amigavel para falhas na camada de dados do Tesouro Direto."""


def get_treasury_bonds(use_cache: bool = True) -> pd.DataFrame:
    history = get_treasury_price_history(use_cache=use_cache)
    if history.empty:
        raise TesouroClientError("Resposta vazia do Tesouro Direto.")
    latest_date = history["data_base"].max()
    return history.loc[history["data_base"] == latest_date].reset_index(drop=True)


def get_treasury_price_history(
    year: Optional[int] = None,
    use_cache: bool = True,
) -> pd.DataFrame:
    raw_content = _get_price_history_content(use_cache=use_cache)
    raw_data = _read_csv(raw_content)
    normalized = normalize_treasury_bonds(raw_data)

    if year is not None:
        if year < 2002 or year > 2100:
            raise TesouroClientError("Ano invalido para historico do Tesouro Direto.")
        normalized = normalized.loc[normalized["data_base"].dt.year == year].reset_index(drop=True)

    if normalized.empty:
        raise TesouroClientError("Resposta vazia do Tesouro Direto.")
    return normalized


def normalize_treasury_bonds(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        raise TesouroClientError("Resposta vazia do Tesouro Direto.")

    normalized = df.copy()
    normalized.columns = [_normalize_column_name(column) for column in normalized.columns]
    normalized = normalized.rename(columns={column: COLUMN_ALIASES.get(column, column) for column in normalized.columns})

    if "tipo" in normalized.columns and "vencimento" in normalized.columns and "nome" not in normalized.columns:
        normalized["nome"] = normalized["tipo"].astype(str) + " " + normalized["vencimento"].astype(str)

    missing = [column for column in NORMALIZED_COLUMNS if column not in normalized.columns]
    if missing:
        raise TesouroClientError(
            "CSV do Tesouro Direto sem colunas esperadas: " + ", ".join(missing) + "."
        )

    result = normalized[NORMALIZED_COLUMNS].copy()
    result["nome"] = result["nome"].astype(str).str.strip()
    result["tipo"] = result["tipo"].astype(str).str.strip()
    result["vencimento"] = _parse_date_series(result["vencimento"], "vencimento")
    result["data_base"] = _parse_date_series(result["data_base"], "data_base")

    for column in ["taxa_compra", "taxa_venda", "preco_compra", "preco_venda"]:
        result[column] = _parse_number_series(result[column], column)

    return result.sort_values(["data_base", "tipo", "vencimento"]).reset_index(drop=True)


def search_treasury_bonds(query: str) -> pd.DataFrame:
    clean_query = str(query or "").strip()
    if not clean_query:
        return pd.DataFrame(columns=NORMALIZED_COLUMNS)

    bonds = get_treasury_bonds()
    normalized_query = _strip_accents(clean_query).lower()
    haystack = (
        bonds["nome"].fillna("").astype(str) + " " + bonds["tipo"].fillna("").astype(str)
    ).map(lambda value: _strip_accents(value).lower())
    return bonds.loc[haystack.str.contains(normalized_query, na=False, regex=False)].reset_index(drop=True)


def _get_price_history_content(use_cache: bool) -> bytes:
    if use_cache and PRICE_HISTORY_CACHE.exists():
        return PRICE_HISTORY_CACHE.read_bytes()

    csv_url = _get_price_history_csv_url()
    try:
        response = requests.get(csv_url, timeout=60)
        response.raise_for_status()
    except requests.HTTPError as exc:
        status_code = exc.response.status_code if exc.response is not None else "desconhecido"
        raise TesouroClientError(f"Erro HTTP {status_code} ao baixar dados do Tesouro Direto.") from exc
    except requests.RequestException as exc:
        raise TesouroClientError(f"Fonte do Tesouro Direto indisponivel: {exc}") from exc

    if not response.content:
        raise TesouroClientError("Resposta vazia do Tesouro Direto.")

    if use_cache:
        PRICE_HISTORY_CACHE.parent.mkdir(parents=True, exist_ok=True)
        PRICE_HISTORY_CACHE.write_bytes(response.content)

    return response.content


def _get_price_history_csv_url() -> str:
    try:
        response = requests.get(CKAN_PACKAGE_URL, timeout=30)
        response.raise_for_status()
    except requests.HTTPError as exc:
        status_code = exc.response.status_code if exc.response is not None else "desconhecido"
        raise TesouroClientError(f"Erro HTTP {status_code} ao consultar metadados do Tesouro Direto.") from exc
    except requests.RequestException as exc:
        raise TesouroClientError(f"Fonte do Tesouro Direto indisponivel: {exc}") from exc

    try:
        payload = response.json()
    except ValueError as exc:
        raise TesouroClientError("Metadados do Tesouro Direto em formato inesperado.") from exc

    resources = payload.get("result", {}).get("resources", []) if isinstance(payload, dict) else []
    for resource in resources:
        if str(resource.get("format", "")).upper() == "CSV" and resource.get("url"):
            return str(resource["url"])

    raise TesouroClientError("Metadados do Tesouro Direto sem recurso CSV esperado.")


def _read_csv(content: bytes) -> pd.DataFrame:
    errors = []
    for encoding in ("utf-8-sig", "latin1"):
        try:
            return pd.read_csv(io.BytesIO(content), sep=";", decimal=",", encoding=encoding, dtype=str)
        except UnicodeDecodeError as exc:
            errors.append(str(exc))
        except pd.errors.ParserError as exc:
            raise TesouroClientError(f"CSV do Tesouro Direto em formato inesperado: {exc}") from exc

    raise TesouroClientError(
        "Nao foi possivel ler CSV do Tesouro Direto: " + "; ".join(errors)
    )


def _parse_date_series(series: pd.Series, column: str) -> pd.Series:
    parsed = pd.to_datetime(series, dayfirst=True, errors="coerce")
    if parsed.isna().any():
        raise TesouroClientError(f"Data invalida na coluna {column} do Tesouro Direto.")
    return parsed


def _parse_number_series(series: pd.Series, column: str) -> pd.Series:
    normalized = (
        series.astype(str)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.replace("%", "", regex=False)
        .str.strip()
    )
    parsed = pd.to_numeric(normalized, errors="coerce")
    if (parsed.isna() & series.notna()).any():
        raise TesouroClientError(f"Valor numerico invalido na coluna {column} do Tesouro Direto.")
    return parsed


def _normalize_column_name(column: object) -> str:
    text = _strip_accents(str(column)).lower().strip()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text


def _strip_accents(value: str) -> str:
    return "".join(
        char for char in unicodedata.normalize("NFKD", value) if not unicodedata.combining(char)
    )
