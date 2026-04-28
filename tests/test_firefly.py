import pandas as pd
import pytest
import requests

from src.data import firefly
from src.data.firefly import (
    FireflyClientError,
    get_accounts,
    get_categories,
    get_finance_summary,
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
    monkeypatch.setenv("FIREFLY_BASE_URL", "https://firefly.local")
    monkeypatch.setenv("FIREFLY_ACCESS_TOKEN", "secret-token")


def test_get_accounts_normalizes_firefly_response(monkeypatch):
    configure_env(monkeypatch)
    calls = []

    def fake_get(url, headers, params, timeout):
        calls.append((url, headers, params, timeout))
        return FakeResponse(
            {
                "data": [
                    {
                        "id": "1",
                        "attributes": {
                            "name": "Conta Corrente",
                            "type": "asset",
                            "currency_code": "BRL",
                            "current_balance": "1234.56",
                            "active": True,
                        },
                    }
                ]
            }
        )

    monkeypatch.setattr(firefly.requests, "get", fake_get)

    data = get_accounts()

    assert calls[0][0] == "https://firefly.local/api/v1/accounts"
    assert calls[0][1]["Authorization"] == "Bearer secret-token"
    assert data.iloc[0]["name"] == "Conta Corrente"
    assert data.iloc[0]["current_balance"] == 1234.56


def test_get_transactions_normalizes_nested_transactions(monkeypatch):
    configure_env(monkeypatch)

    def fake_get(url, headers, params, timeout):
        assert params == {"limit": 50, "start": "2026-04-01", "end": "2026-04-30"}
        return FakeResponse(
            {
                "data": [
                    {
                        "id": "10",
                        "attributes": {
                            "transactions": [
                                {
                                    "transaction_journal_id": "99",
                                    "date": "2026-04-28T10:00:00-03:00",
                                    "description": "Mercado",
                                    "amount": "-150.25",
                                    "currency_code": "BRL",
                                    "type": "withdrawal",
                                    "category_name": "Alimentacao",
                                    "source_name": "Conta",
                                    "destination_name": "Supermercado",
                                }
                            ]
                        },
                    }
                ]
            }
        )

    monkeypatch.setattr(firefly.requests, "get", fake_get)

    data = get_transactions(start_date="2026-04-01", end_date="2026-04-30")

    assert list(data.columns) == [
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
    ]
    assert data.iloc[0]["amount"] == -150.25
    assert data.iloc[0]["category"] == "Alimentacao"


def test_get_categories_normalizes_response(monkeypatch):
    configure_env(monkeypatch)

    def fake_get(url, headers, params, timeout):
        return FakeResponse({"data": [{"id": "1", "attributes": {"name": "Moradia"}}]})

    monkeypatch.setattr(firefly.requests, "get", fake_get)

    data = get_categories()

    assert data.to_dict("records") == [{"id": "1", "name": "Moradia"}]


def test_get_finance_summary_groups_transactions(monkeypatch):
    transactions = pd.DataFrame(
        {
            "id": ["1", "2", "3"],
            "transaction_type": ["withdrawal", "withdrawal", "deposit"],
            "category": ["Mercado", "Mercado", "Salario"],
            "amount": [-100.0, -50.0, 1000.0],
        }
    )

    monkeypatch.setattr(firefly, "get_transactions", lambda start_date=None, end_date=None, limit=500: transactions)

    data = get_finance_summary()

    assert {"withdrawal", "deposit"} == set(data["transaction_type"])
    mercado = data.loc[data["category"] == "Mercado"].iloc[0]
    assert mercado["total_amount"] == -150.0
    assert mercado["transaction_count"] == 2


def test_missing_configuration_raises_friendly_error(monkeypatch):
    monkeypatch.delenv("FIREFLY_BASE_URL", raising=False)
    monkeypatch.delenv("FIREFLY_ACCESS_TOKEN", raising=False)

    with pytest.raises(FireflyClientError, match="FIREFLY_BASE_URL"):
        get_accounts()


def test_http_auth_error_is_friendly(monkeypatch):
    configure_env(monkeypatch)

    def fake_get(url, headers, params, timeout):
        return FakeResponse(status_code=401)

    monkeypatch.setattr(firefly.requests, "get", fake_get)

    with pytest.raises(FireflyClientError, match="autenticacao"):
        get_accounts()


def test_invalid_json_is_friendly(monkeypatch):
    configure_env(monkeypatch)

    def fake_get(url, headers, params, timeout):
        return FakeResponse(payload=ValueError("bad json"))

    monkeypatch.setattr(firefly.requests, "get", fake_get)

    with pytest.raises(FireflyClientError, match="Resposta invalida"):
        get_accounts()
