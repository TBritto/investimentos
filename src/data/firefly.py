from __future__ import annotations

import os
from typing import Any, Optional
from urllib.parse import urljoin

import pandas as pd
import requests


class FireflyClientError(RuntimeError):
    """Erro amigavel para falhas na integracao Firefly III."""


def get_accounts(account_type: Optional[str] = None) -> pd.DataFrame:
    params = {}
    if account_type:
        params["type"] = account_type
    payload = _get_json("/api/v1/accounts", params=params)
    return _normalize_accounts(payload)


def get_transactions(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 50,
) -> pd.DataFrame:
    params: dict[str, Any] = {"limit": limit}
    if start_date:
        params["start"] = start_date
    if end_date:
        params["end"] = end_date
    payload = _get_json("/api/v1/transactions", params=params)
    return _normalize_transactions(payload)


def get_categories() -> pd.DataFrame:
    payload = _get_json("/api/v1/categories")
    return _normalize_categories(payload)


def get_finance_summary(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    transactions = get_transactions(start_date=start_date, end_date=end_date, limit=500)
    if transactions.empty:
        return pd.DataFrame(
            columns=["transaction_type", "category", "total_amount", "transaction_count"]
        )

    grouped = (
        transactions.groupby(["transaction_type", "category"], dropna=False)
        .agg(total_amount=("amount", "sum"), transaction_count=("id", "count"))
        .reset_index()
    )
    return grouped.sort_values(["transaction_type", "total_amount"]).reset_index(drop=True)


def _get_json(path: str, params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    base_url, token = _load_config()
    url = urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
    }
    try:
        response = requests.get(url, headers=headers, params=params or {}, timeout=30)
        response.raise_for_status()
    except requests.HTTPError as exc:
        status_code = exc.response.status_code if exc.response is not None else "desconhecido"
        if status_code in {401, 403}:
            raise FireflyClientError("Firefly III recusou a autenticacao. Verifique o token.") from exc
        raise FireflyClientError(f"Erro HTTP {status_code} ao consultar Firefly III.") from exc
    except requests.RequestException as exc:
        raise FireflyClientError(f"Nao foi possivel conectar ao Firefly III: {exc}") from exc

    try:
        payload = response.json()
    except ValueError as exc:
        raise FireflyClientError("Resposta invalida do Firefly III.") from exc

    if not isinstance(payload, dict):
        raise FireflyClientError("Formato inesperado na resposta do Firefly III.")
    return payload


def _load_config() -> tuple[str, str]:
    base_url = os.getenv("FIREFLY_BASE_URL", "").strip()
    token = os.getenv("FIREFLY_ACCESS_TOKEN", "").strip()
    if not base_url:
        raise FireflyClientError("Configure FIREFLY_BASE_URL no ambiente.")
    if not token:
        raise FireflyClientError("Configure FIREFLY_ACCESS_TOKEN no ambiente.")
    return base_url, token


def _extract_data(payload: dict[str, Any], context: str) -> list[dict[str, Any]]:
    data = payload.get("data", [])
    if data is None:
        return []
    if not isinstance(data, list):
        raise FireflyClientError(f"Formato inesperado em {context} do Firefly III.")
    return data


def _normalize_accounts(payload: dict[str, Any]) -> pd.DataFrame:
    rows = []
    for item in _extract_data(payload, "contas"):
        attributes = item.get("attributes", {}) or {}
        rows.append(
            {
                "id": str(item.get("id", "")),
                "name": attributes.get("name"),
                "type": attributes.get("type"),
                "currency_code": attributes.get("currency_code"),
                "current_balance": _to_float(attributes.get("current_balance")),
                "active": attributes.get("active"),
            }
        )
    return pd.DataFrame(rows, columns=["id", "name", "type", "currency_code", "current_balance", "active"])


def _normalize_categories(payload: dict[str, Any]) -> pd.DataFrame:
    rows = []
    for item in _extract_data(payload, "categorias"):
        attributes = item.get("attributes", {}) or {}
        rows.append({"id": str(item.get("id", "")), "name": attributes.get("name")})
    return pd.DataFrame(rows, columns=["id", "name"])


def _normalize_transactions(payload: dict[str, Any]) -> pd.DataFrame:
    rows = []
    for item in _extract_data(payload, "transacoes"):
        attributes = item.get("attributes", {}) or {}
        for transaction in attributes.get("transactions", []) or []:
            rows.append(
                {
                    "id": str(item.get("id", "")),
                    "transaction_journal_id": str(transaction.get("transaction_journal_id", "")),
                    "date": pd.to_datetime(transaction.get("date"), errors="coerce"),
                    "description": transaction.get("description"),
                    "amount": _to_float(transaction.get("amount")),
                    "currency_code": transaction.get("currency_code"),
                    "transaction_type": transaction.get("type"),
                    "category": transaction.get("category_name") or "Sem categoria",
                    "source_name": transaction.get("source_name"),
                    "destination_name": transaction.get("destination_name"),
                }
            )

    dataframe = pd.DataFrame(
        rows,
        columns=[
            "id",
            "transaction_journal_id",
            "date",
            "description",
            "amount",
            "currency_code",
            "transaction_type",
            "category",
            "source_name",
            "destination_name",
        ],
    )
    if not dataframe.empty and dataframe["date"].isna().any():
        raise FireflyClientError("Data invalida em transacao do Firefly III.")
    return dataframe


def _to_float(value: Any) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        return float(str(value).replace(",", "."))
    except (TypeError, ValueError) as exc:
        raise FireflyClientError(f"Valor numerico invalido recebido do Firefly III: {value}") from exc
