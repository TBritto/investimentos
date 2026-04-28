import pandas as pd
import pytest
import requests

from src.data import pluggy
from src.data.pluggy import (
    PluggyClientError,
    create_api_key,
    create_connect_token,
    get_accounts,
    get_items,
    get_transactions,
)


class FakeResponse:
    def __init__(self, payload=None, status_code=200):
        self.payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            error = requests.HTTPError("http error")
            error.response = self
            raise error

    def json(self):
        if isinstance(self.payload, Exception):
            raise self.payload
        return self.payload


def configure_env(monkeypatch):
    monkeypatch.setenv("PLUGGY_CLIENT_ID", "client-id")
    monkeypatch.setenv("PLUGGY_CLIENT_SECRET", "client-secret")
    monkeypatch.delenv("PLUGGY_BASE_URL", raising=False)


def test_create_api_key_uses_credentials(monkeypatch):
    configure_env(monkeypatch)
    calls = []

    def fake_request(method, url, headers, params, json, timeout):
        calls.append((method, url, headers, params, json, timeout))
        return FakeResponse({"apiKey": "api-key"})

    monkeypatch.setattr(pluggy.requests, "request", fake_request)

    assert create_api_key() == "api-key"
    assert calls == [
        (
            "POST",
            "https://api.pluggy.ai/auth",
            {"Accept": "application/json"},
            {},
            {"clientId": "client-id", "clientSecret": "client-secret"},
            30,
        )
    ]


def test_create_connect_token_uses_api_key(monkeypatch):
    calls = []

    def fake_request(method, url, headers, params, json, timeout):
        calls.append((method, url, headers, params, json, timeout))
        return FakeResponse({"connectToken": "connect-token"})

    monkeypatch.setattr(pluggy, "create_api_key", lambda: "api-key")
    monkeypatch.setattr(pluggy.requests, "request", fake_request)

    token = create_connect_token(client_user_id="user-1", oauth_redirect_url="https://app.local/callback")

    assert token == "connect-token"
    assert calls[0][1] == "https://api.pluggy.ai/connect_token"
    assert calls[0][2]["X-API-KEY"] == "api-key"
    assert calls[0][4] == {
        "options": {
            "clientUserId": "user-1",
            "oauthRedirectUrl": "https://app.local/callback",
        }
    }


def test_get_items_normalizes_response(monkeypatch):
    monkeypatch.setattr(pluggy, "create_api_key", lambda: "api-key")

    def fake_request(method, url, headers, params, json, timeout):
        return FakeResponse(
            {
                "results": [
                    {
                        "id": "item-1",
                        "connector": {"id": 201, "name": "Banco Teste"},
                        "status": "UPDATED",
                        "executionStatus": "SUCCESS",
                        "lastUpdatedAt": "2026-04-28T12:00:00Z",
                        "clientUserId": "user-1",
                    }
                ]
            }
        )

    monkeypatch.setattr(pluggy.requests, "request", fake_request)

    data = get_items()

    assert data.iloc[0]["id"] == "item-1"
    assert data.iloc[0]["connector_name"] == "Banco Teste"
    assert data.iloc[0]["execution_status"] == "SUCCESS"


def test_get_accounts_normalizes_response(monkeypatch):
    monkeypatch.setattr(pluggy, "create_api_key", lambda: "api-key")
    calls = []

    def fake_request(method, url, headers, params, json, timeout):
        calls.append(params)
        return FakeResponse(
            {
                "results": [
                    {
                        "id": "account-1",
                        "itemId": "item-1",
                        "type": "BANK",
                        "subtype": "CHECKING_ACCOUNT",
                        "name": "Conta Corrente",
                        "marketingName": "Conta",
                        "currencyCode": "BRL",
                        "balance": {"current": 1234.56, "date": "2026-04-28"},
                    }
                ]
            }
        )

    monkeypatch.setattr(pluggy.requests, "request", fake_request)

    data = get_accounts(item_id="item-1")

    assert calls == [{"itemId": "item-1"}]
    assert data.iloc[0]["balance"] == 1234.56
    assert data.iloc[0]["balance_date"] == pd.Timestamp("2026-04-28")


def test_get_transactions_normalizes_response(monkeypatch):
    monkeypatch.setattr(pluggy, "create_api_key", lambda: "api-key")
    calls = []

    def fake_request(method, url, headers, params, json, timeout):
        calls.append(params)
        return FakeResponse(
            {
                "results": [
                    {
                        "id": "tx-1",
                        "accountId": "account-1",
                        "date": "2026-04-28T12:00:00Z",
                        "description": "Mercado",
                        "descriptionRaw": "MERCADO TESTE",
                        "amount": -150.25,
                        "currencyCode": "BRL",
                        "category": "Food",
                        "status": "POSTED",
                        "type": "DEBIT",
                        "balance": 1000.0,
                        "merchant": {"name": "Mercado", "cnpj": "00.000.000/0001-91"},
                    }
                ]
            }
        )

    monkeypatch.setattr(pluggy.requests, "request", fake_request)

    data = get_transactions("account-1", from_date="2026-04-01", to_date="2026-04-30")

    assert calls == [
        {"accountId": "account-1", "pageSize": 100, "from": "2026-04-01", "to": "2026-04-30"}
    ]
    assert data.iloc[0]["amount"] == -150.25
    assert data.iloc[0]["merchant_name"] == "Mercado"


def test_missing_credentials_raise_friendly_error(monkeypatch):
    monkeypatch.delenv("PLUGGY_CLIENT_ID", raising=False)
    monkeypatch.delenv("PLUGGY_CLIENT_SECRET", raising=False)

    with pytest.raises(PluggyClientError, match="PLUGGY_CLIENT_ID"):
        create_api_key()


def test_auth_error_is_friendly(monkeypatch):
    configure_env(monkeypatch)

    def fake_request(method, url, headers, params, json, timeout):
        return FakeResponse(status_code=403)

    monkeypatch.setattr(pluggy.requests, "request", fake_request)

    with pytest.raises(PluggyClientError, match="autenticacao"):
        create_api_key()


def test_invalid_json_is_friendly(monkeypatch):
    configure_env(monkeypatch)

    def fake_request(method, url, headers, params, json, timeout):
        return FakeResponse(payload=ValueError("bad json"))

    monkeypatch.setattr(pluggy.requests, "request", fake_request)

    with pytest.raises(PluggyClientError, match="Resposta invalida"):
        create_api_key()
