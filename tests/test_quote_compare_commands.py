import pandas as pd
import pytest

from src.commands import quote_compare
from src.commands.quote_compare import execute_market_command


def test_execute_quote_command(monkeypatch):
    def fake_quote(symbol):
        assert symbol == "AAPL"
        return pd.DataFrame({"symbol": ["AAPL"], "price": [10.0]})

    monkeypatch.setattr(quote_compare, "get_equity_quote", fake_quote)

    result = execute_market_command("quote aapl")

    assert result.title == "Cotacao: AAPL"
    assert result.data.iloc[0]["price"] == 10.0


def test_execute_compare_command(monkeypatch):
    def fake_compare(symbols, start_date=None, end_date=None):
        assert symbols == ["AAPL", "MSFT"]
        assert start_date == "2024-01-01"
        return pd.DataFrame({"date": [pd.Timestamp("2024-01-01")], "AAPL": [10.0], "MSFT": [9.0]})

    monkeypatch.setattr(quote_compare, "compare_equities", fake_compare)

    result = execute_market_command("compare aapl msft", start_date="2024-01-01")

    assert result.title == "Comparacao: AAPL, MSFT"
    assert list(result.data.columns) == ["date", "AAPL", "MSFT"]


def test_execute_market_command_rejects_unknown_command():
    with pytest.raises(ValueError, match="Comando desconhecido"):
        execute_market_command("macro selic")
