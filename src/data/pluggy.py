from __future__ import annotations

import os
from typing import Any, Optional
from urllib.parse import urljoin

import pandas as pd
import requests


PLUGGY_BASE_URL = "https://api.pluggy.ai"


class PluggyClientError(RuntimeError):
    """Erro amigavel para falhas na integracao Pluggy/Open Finance."""


def create_api_key() -> str:
    client_id, client_secret = _load_credentials()
    payload = {"clientId": client_id, "clientSecret": client_secret}
    response = _request("POST", "/auth", json=payload, api_key=None)
    api_key = response.get("apiKey") or response.get("accessToken")
    if not api_key:
        raise PluggyClientError("Resposta da Pluggy sem API key.")
    return str(api_key)


def create_connect_token(
    client_user_id: Optional[str] = None,
    item_id: Optional[str] = None,
    oauth_redirect_url: Optional[str] = None,
    webhook_url: Optional[str] = None,
) -> str:
    body: dict[str, Any] = {}
    options: dict[str, Any] = {}
    if item_id:
        body["itemId"] = item_id
    if client_user_id:
        options["clientUserId"] = client_user_id
    if oauth_redirect_url:
        options["oauthRedirectUrl"] = oauth_redirect_url
    if webhook_url:
        options["webhookUrl"] = webhook_url
    if options:
        body["options"] = options

    response = _request("POST", "/connect_token", json=body, api_key=create_api_key())
    connect_token = response.get("connectToken")
    if not connect_token:
        raise PluggyClientError("Resposta da Pluggy sem connect token.")
    return str(connect_token)


def get_items() -> pd.DataFrame:
    payload = _request("GET", "/items", api_key=create_api_key())
    return _normalize_items(payload)


def get_accounts(item_id: Optional[str] = None) -> pd.DataFrame:
    params = {}
    if item_id:
        params["itemId"] = item_id
    payload = _request("GET", "/accounts", params=params, api_key=create_api_key())
    return _normalize_accounts(payload)


def get_transactions(
    account_id: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    page_size: int = 100,
) -> pd.DataFrame:
    if not account_id:
        raise PluggyClientError("Informe account_id para consultar transacoes.")

    params: dict[str, Any] = {"accountId": account_id, "pageSize": page_size}
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date
    payload = _request("GET", "/transactions", params=params, api_key=create_api_key())
    return _normalize_transactions(payload)


def _request(
    method: str,
    path: str,
    params: Optional[dict[str, Any]] = None,
    json: Optional[dict[str, Any]] = None,
    api_key: Optional[str] = None,
) -> dict[str, Any]:
    url = urljoin(_base_url().rstrip("/") + "/", path.lstrip("/"))
    headers = {"Accept": "application/json"}
    if api_key:
        headers["X-API-KEY"] = api_key

    try:
        response = requests.request(
            method,
            url,
            headers=headers,
            params=params or {},
            json=json,
            timeout=30,
        )
        response.raise_for_status()
    except requests.HTTPError as exc:
        status_code = exc.response.status_code if exc.response is not None else "desconhecido"
        if status_code in {401, 403}:
            raise PluggyClientError("Pluggy recusou autenticacao. Verifique credenciais e escopos.") from exc
        raise PluggyClientError(f"Erro HTTP {status_code} ao consultar Pluggy.") from exc
    except requests.RequestException as exc:
        raise PluggyClientError(f"Nao foi possivel conectar a Pluggy: {exc}") from exc

    try:
        payload = response.json()
    except ValueError as exc:
        raise PluggyClientError("Resposta invalida da Pluggy.") from exc

    if not isinstance(payload, dict):
        raise PluggyClientError("Formato inesperado na resposta da Pluggy.")
    return payload


def _load_credentials() -> tuple[str, str]:
    client_id = os.getenv("PLUGGY_CLIENT_ID", "").strip()
    client_secret = os.getenv("PLUGGY_CLIENT_SECRET", "").strip()
    if not client_id:
        raise PluggyClientError("Configure PLUGGY_CLIENT_ID no ambiente.")
    if not client_secret:
        raise PluggyClientError("Configure PLUGGY_CLIENT_SECRET no ambiente.")
    return client_id, client_secret


def _base_url() -> str:
    return os.getenv("PLUGGY_BASE_URL", PLUGGY_BASE_URL).strip() or PLUGGY_BASE_URL


def _extract_results(payload: dict[str, Any], context: str) -> list[dict[str, Any]]:
    results = payload.get("results", payload.get("data", []))
    if results is None:
        return []
    if not isinstance(results, list):
        raise PluggyClientError(f"Formato inesperado em {context} da Pluggy.")
    return results


def _normalize_items(payload: dict[str, Any]) -> pd.DataFrame:
    rows = []
    for item in _extract_results(payload, "items"):
        connector = item.get("connector", {}) or {}
        rows.append(
            {
                "id": item.get("id"),
                "connector_id": connector.get("id") or item.get("connectorId"),
                "connector_name": connector.get("name"),
                "status": item.get("status"),
                "execution_status": item.get("executionStatus"),
                "last_updated_at": pd.to_datetime(item.get("lastUpdatedAt"), errors="coerce"),
                "client_user_id": item.get("clientUserId"),
            }
        )
    return pd.DataFrame(
        rows,
        columns=[
            "id",
            "connector_id",
            "connector_name",
            "status",
            "execution_status",
            "last_updated_at",
            "client_user_id",
        ],
    )


def _normalize_accounts(payload: dict[str, Any]) -> pd.DataFrame:
    rows = []
    for account in _extract_results(payload, "accounts"):
        balance = account.get("balance") or {}
        rows.append(
            {
                "id": account.get("id"),
                "item_id": account.get("itemId"),
                "type": account.get("type"),
                "subtype": account.get("subtype"),
                "name": account.get("name"),
                "marketing_name": account.get("marketingName"),
                "currency_code": account.get("currencyCode"),
                "balance": _to_float(balance.get("current") if isinstance(balance, dict) else account.get("balance")),
                "balance_date": pd.to_datetime(balance.get("date") if isinstance(balance, dict) else None, errors="coerce"),
            }
        )
    return pd.DataFrame(
        rows,
        columns=[
            "id",
            "item_id",
            "type",
            "subtype",
            "name",
            "marketing_name",
            "currency_code",
            "balance",
            "balance_date",
        ],
    )


def _normalize_transactions(payload: dict[str, Any]) -> pd.DataFrame:
    rows = []
    for transaction in _extract_results(payload, "transactions"):
        merchant = transaction.get("merchant") or {}
        rows.append(
            {
                "id": transaction.get("id"),
                "account_id": transaction.get("accountId"),
                "date": pd.to_datetime(transaction.get("date"), errors="coerce"),
                "description": transaction.get("description"),
                "description_raw": transaction.get("descriptionRaw"),
                "amount": _to_float(transaction.get("amount")),
                "currency_code": transaction.get("currencyCode"),
                "category": transaction.get("category"),
                "status": transaction.get("status"),
                "type": transaction.get("type"),
                "balance": _to_float(transaction.get("balance")),
                "merchant_name": merchant.get("name") if isinstance(merchant, dict) else None,
                "merchant_cnpj": merchant.get("cnpj") if isinstance(merchant, dict) else None,
            }
        )
    dataframe = pd.DataFrame(
        rows,
        columns=[
            "id",
            "account_id",
            "date",
            "description",
            "description_raw",
            "amount",
            "currency_code",
            "category",
            "status",
            "type",
            "balance",
            "merchant_name",
            "merchant_cnpj",
        ],
    )
    if not dataframe.empty and dataframe["date"].isna().any():
        raise PluggyClientError("Data invalida em transacao da Pluggy.")
    return dataframe


def _to_float(value: Any) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise PluggyClientError(f"Valor numerico invalido recebido da Pluggy: {value}") from exc
