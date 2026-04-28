import pytest
import pandas as pd
from types import SimpleNamespace

import src.terminal.commands as terminal_commands
from src.terminal.parser import parse_command
from src.terminal.registry import execute_command


def test_parse_command_extracts_command_and_args() -> None:
    request = parse_command("compare AAPL MSFT")

    assert request.raw == "compare AAPL MSFT"
    assert request.command == "compare"
    assert request.args == ["AAPL", "MSFT"]


def test_parse_command_rejects_empty_command() -> None:
    with pytest.raises(ValueError, match="Digite um comando"):
        parse_command(" ")


def test_help_command_lists_initial_commands() -> None:
    result = execute_command("help")

    assert result.title == "Ajuda"
    assert "macro selic" in result.message
    assert "openfinance accounts" in result.message
    assert "portfolio risco" in result.message


def test_macro_command_uses_bcb_command_layer(monkeypatch) -> None:
    data = pd.DataFrame({"date": pd.to_datetime(["2024-01-01"]), "value": [10.5], "code": [432]})

    def fake_execute_macro_command(command: str):
        assert command == "macro selic"
        return SimpleNamespace(title="Selic Meta", data=data)

    monkeypatch.setattr(terminal_commands, "execute_macro_command", fake_execute_macro_command)

    result = execute_command("macro selic")

    assert result.title == "Selic Meta"
    assert result.dataframe is data


def test_quote_command_uses_market_command_layer(monkeypatch) -> None:
    data = pd.DataFrame({"symbol": ["PETR4"], "price": [38.5]})

    def fake_execute_market_command(command: str):
        assert command == "quote PETR4"
        return SimpleNamespace(title="Cotacao: PETR4", data=data)

    monkeypatch.setattr(terminal_commands, "execute_market_command", fake_execute_market_command)

    result = execute_command("quote PETR4")

    assert result.title == "Cotacao: PETR4"
    assert result.dataframe is data


def test_compare_command_requires_two_tickers() -> None:
    result = execute_command("compare AAPL")

    assert result.title == "Comparacao"
    assert "TICKER1 TICKER2" in result.message


def test_openfinance_accounts_uses_pluggy_layer(monkeypatch) -> None:
    data = pd.DataFrame({"id": ["account-1"], "name": ["Conta Corrente"]})

    monkeypatch.setattr(terminal_commands, "get_accounts", lambda item_id=None: data)

    result = execute_command("openfinance accounts")

    assert result.title == "Contas Open Finance"
    assert result.dataframe is data


def test_unknown_command_returns_friendly_message() -> None:
    result = execute_command("foo bar")

    assert result.title == "Comando nao implementado"
    assert "ainda nao foi implementado" in result.message
