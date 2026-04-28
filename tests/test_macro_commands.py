import pandas as pd
import pytest

from src.commands import macro
from src.commands.macro import execute_macro_command


def test_execute_macro_command_routes_to_indicator(monkeypatch):
    def fake_fetcher(start_date=None, end_date=None):
        assert start_date == "2024-01-01"
        assert end_date == "2024-01-31"
        return pd.DataFrame(
            {
                "date": [pd.Timestamp("2024-01-01")],
                "value": [10.5],
                "code": [432],
            }
        )

    monkeypatch.setitem(macro.MACRO_COMMANDS, "selic", ("Selic teste", fake_fetcher))

    result = execute_macro_command("macro selic", start_date="2024-01-01", end_date="2024-01-31")

    assert result.command == "macro selic"
    assert result.title == "Selic teste"
    assert result.data.iloc[0]["value"] == 10.5


def test_execute_macro_command_rejects_unknown_indicator():
    with pytest.raises(ValueError, match="Indicador macro desconhecido"):
        execute_macro_command("macro pib")
