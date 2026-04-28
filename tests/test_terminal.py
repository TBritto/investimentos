import pytest

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
    assert "portfolio risco" in result.message


def test_macro_command_recognizes_selic_with_friendly_pending_message() -> None:
    result = execute_command("macro selic")

    assert result.title == "Macro selic"
    assert "Banco Central SGS" in result.message


def test_quote_command_recognizes_ticker() -> None:
    result = execute_command("quote PETR4")

    assert result.title == "Cotacao PETR4"
    assert "OpenBB" in result.message


def test_compare_command_requires_two_tickers() -> None:
    result = execute_command("compare AAPL")

    assert result.title == "Comparacao"
    assert "TICKER1 TICKER2" in result.message


def test_unknown_command_returns_friendly_message() -> None:
    result = execute_command("foo bar")

    assert result.title == "Comando nao implementado"
    assert "ainda nao foi implementado" in result.message
