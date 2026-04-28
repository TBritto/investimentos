from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Optional

import pandas as pd

from src.data.bcb import get_ipca, get_selic, get_usdbrl


@dataclass
class MacroCommandResult:
    command: str
    title: str
    data: pd.DataFrame


MacroFetcher = Callable[[Optional[str], Optional[str]], pd.DataFrame]

MACRO_COMMANDS: Dict[str, tuple[str, MacroFetcher]] = {
    "selic": ("Selic Meta", get_selic),
    "ipca": ("IPCA", get_ipca),
    "dolar": ("Dolar comercial", get_usdbrl),
    "dólar": ("Dolar comercial", get_usdbrl),
}


def execute_macro_command(
    command: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> MacroCommandResult:
    parts = command.strip().lower().split()
    if len(parts) != 2 or parts[0] != "macro":
        raise ValueError("Use o formato: macro selic, macro ipca ou macro dolar.")

    indicator = parts[1]
    if indicator not in MACRO_COMMANDS:
        raise ValueError("Indicador macro desconhecido. Opcoes: selic, ipca, dolar.")

    title, fetcher = MACRO_COMMANDS[indicator]
    data = fetcher(start_date=start_date, end_date=end_date)
    return MacroCommandResult(command=command, title=title, data=data)
