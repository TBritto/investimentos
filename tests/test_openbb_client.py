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

    def fake_quote(symbol):
        calls.append(symbol)
        return FakeOpenBBResult(pd.DataFrame({"symbol": [symbol], "price": [10.0]}))

    monkeypatch.setattr(
        openbb_client,
        "obb",
        SimpleNamespace(equity=SimpleNamespace(price=SimpleNamespace(quote=fake_quote))),
    )

    data = get_equity_quote(" aapl ")

    assert calls == ["AAPL"]
    assert data.iloc[0]["symbol"] == "AAPL"


def test_get_equity_history_returns_date_and_symbol_columns(monkeypatch):
    frame = pd.DataFrame(
        {"close": [10.0, 11.0]},
        index=pd.to_datetime(["2024-01-01", "2024-01-02"]),
    )
    calls = []

    def fake_historical(**kwargs):
        calls.append(kwargs)
        return FakeOpenBBResult(frame)

    monkeypatch.setattr(
        openbb_client,
        "obb",
        SimpleNamespace(equity=SimpleNamespace(price=SimpleNamespace(historical=fake_historical))),
    )

    data = get_equity_history("msft", start_date="2024-01-01", end_date="2024-01-02")

    assert calls == [{"symbol": "MSFT", "start_date": "2024-01-01", "end_date": "2024-01-02"}]
    assert list(data.columns) == ["date", "MSFT"]
    assert data["MSFT"].tolist() == [10.0, 11.0]


def test_compare_equities_combines_history(monkeypatch):
    def fake_history(symbol, start_date=None, end_date=None):
        return pd.DataFrame(
            {
                "date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
                symbol: [10.0, 11.0],
            }
        )

    monkeypatch.setattr(openbb_client, "get_equity_history", fake_history)

    data = compare_equities(["AAPL", "MSFT"], start_date="2024-01-01")

    assert list(data.columns) == ["date", "AAPL", "MSFT"]
    assert len(data) == 2


def test_openbb_errors_are_wrapped(monkeypatch):
    def fake_quote(symbol):
        raise RuntimeError("provider missing")

    monkeypatch.setattr(
        openbb_client,
        "obb",
        SimpleNamespace(equity=SimpleNamespace(price=SimpleNamespace(quote=fake_quote))),
    )

    with pytest.raises(OpenBBClientError, match="Nao foi possivel buscar cotacao"):
        get_equity_quote("AAPL")
