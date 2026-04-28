import pandas as pd
import pytest
from types import SimpleNamespace

from src.data import openbb_client
from src.data.openbb_client import OpenBBClientError, compare_equities, get_equity_history, get_equity_quote


class FakeOpenBBResult:
    def __init__(self, data):
        self.data = data

    def to_dataframe(self):
        return self.data


def test_get_equity_quote_normalizes_symbol(monkeypatch):
    calls = []

    def fake_quote(**kwargs):
        calls.append(kwargs)
        return FakeOpenBBResult(pd.DataFrame({"symbol": [kwargs["symbol"].lower()], "price": [10.0]}))

    monkeypatch.delenv("OPENBB_PROVIDER", raising=False)
    monkeypatch.setattr(
        openbb_client,
        "obb",
        SimpleNamespace(equity=SimpleNamespace(price=SimpleNamespace(quote=fake_quote))),
    )

    data = get_equity_quote(" aapl ")

    assert calls == [{"symbol": "AAPL"}]
    assert "date" not in data.columns
    assert data.iloc[0]["symbol"] == "AAPL"
    assert data.iloc[0]["price"] == 10.0


def test_get_equity_history_normalizes_ohlcv_columns(monkeypatch):
    frame = pd.DataFrame(
        {
            "open": ["9.0", "10.0"],
            "high": [11.0, 12.0],
            "low": [8.5, 9.5],
            "close": [10.0, 11.0],
            "volume": [1000, 2000],
        },
        index=pd.to_datetime(["2024-01-01", "2024-01-02"]),
    )
    calls = []

    def fake_historical(**kwargs):
        calls.append(kwargs)
        return FakeOpenBBResult(frame)

    monkeypatch.delenv("OPENBB_PROVIDER", raising=False)
    monkeypatch.setattr(
        openbb_client,
        "obb",
        SimpleNamespace(equity=SimpleNamespace(price=SimpleNamespace(historical=fake_historical))),
    )

    data = get_equity_history("msft", start_date="2024-01-01", end_date="2024-01-02")

    assert calls == [{"symbol": "MSFT", "start_date": "2024-01-01", "end_date": "2024-01-02"}]
    assert list(data.columns) == ["date", "symbol", "open", "high", "low", "close", "volume"]
    assert data["symbol"].tolist() == ["MSFT", "MSFT"]
    assert data["date"].tolist() == [pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-02")]
    assert data["open"].tolist() == [9.0, 10.0]
    assert data["close"].tolist() == [10.0, 11.0]


def test_get_equity_history_uses_provider_from_argument(monkeypatch):
    calls = []

    def fake_historical(**kwargs):
        calls.append(kwargs)
        return FakeOpenBBResult(
            pd.DataFrame({"date": ["2024-01-01"], "close": [10.0]})
        )

    monkeypatch.setattr(
        openbb_client,
        "obb",
        SimpleNamespace(equity=SimpleNamespace(price=SimpleNamespace(historical=fake_historical))),
    )

    data = get_equity_history("aapl", provider="fmp")

    assert calls == [{"symbol": "AAPL", "provider": "fmp"}]
    assert data["symbol"].tolist() == ["AAPL"]


def test_get_equity_history_uses_provider_from_environment(monkeypatch):
    calls = []

    def fake_historical(**kwargs):
        calls.append(kwargs)
        return FakeOpenBBResult(
            pd.DataFrame({"date": ["2024-01-01"], "close": [10.0]})
        )

    monkeypatch.setenv("OPENBB_PROVIDER", "yfinance")
    monkeypatch.setattr(
        openbb_client,
        "obb",
        SimpleNamespace(equity=SimpleNamespace(price=SimpleNamespace(historical=fake_historical))),
    )

    get_equity_history("aapl")

    assert calls == [{"symbol": "AAPL", "provider": "yfinance"}]


def test_compare_equities_combines_history(monkeypatch):
    def fake_history(symbol, start_date=None, end_date=None, provider=None):
        return pd.DataFrame(
            {
                "date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
                "symbol": [symbol, symbol],
                "close": [10.0, 11.0],
            }
        )

    monkeypatch.setattr(openbb_client, "get_equity_history", fake_history)

    data = compare_equities(["AAPL", "MSFT"], start_date="2024-01-01", provider="fmp")

    assert list(data.columns) == ["date", "symbol", "close"]
    assert data["symbol"].tolist() == ["AAPL", "AAPL", "MSFT", "MSFT"]
    assert len(data) == 4


def test_openbb_errors_are_wrapped(monkeypatch):
    def fake_quote(**kwargs):
        raise RuntimeError("provider missing")

    monkeypatch.delenv("OPENBB_PROVIDER", raising=False)
    monkeypatch.setattr(
        openbb_client,
        "obb",
        SimpleNamespace(equity=SimpleNamespace(price=SimpleNamespace(quote=fake_quote))),
    )

    with pytest.raises(OpenBBClientError, match="Provider OpenBB indisponivel"):
        get_equity_quote("AAPL")


def test_openbb_not_installed_raises_friendly_error(monkeypatch):
    monkeypatch.setattr(openbb_client, "obb", None)

    with pytest.raises(OpenBBClientError, match="OpenBB nao esta instalado"):
        get_equity_quote("AAPL")


def test_empty_openbb_response_raises_friendly_error(monkeypatch):
    def fake_historical(**kwargs):
        return FakeOpenBBResult(pd.DataFrame())

    monkeypatch.delenv("OPENBB_PROVIDER", raising=False)
    monkeypatch.setattr(
        openbb_client,
        "obb",
        SimpleNamespace(equity=SimpleNamespace(price=SimpleNamespace(historical=fake_historical))),
    )

    with pytest.raises(OpenBBClientError, match="Resposta vazia"):
        get_equity_history("AAPL")


def test_invalid_numeric_value_raises_friendly_error(monkeypatch):
    def fake_historical(**kwargs):
        return FakeOpenBBResult(pd.DataFrame({"date": ["2024-01-01"], "close": ["abc"]}))

    monkeypatch.delenv("OPENBB_PROVIDER", raising=False)
    monkeypatch.setattr(
        openbb_client,
        "obb",
        SimpleNamespace(equity=SimpleNamespace(price=SimpleNamespace(historical=fake_historical))),
    )

    with pytest.raises(OpenBBClientError, match="Valor numerico invalido"):
        get_equity_history("AAPL")
