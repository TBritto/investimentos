from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pandas as pd

from src.data.openbb_client import compare_equities, get_equity_quote


@dataclass
class MarketCommandResult:
    command: str
    title: str
    data: pd.DataFrame


def execute_market_command(
    command: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> MarketCommandResult:
    parts = command.strip().split()
    if not parts:
        raise ValueError("Digite um comando.")

    action = parts[0].lower()
    if action == "quote":
        if len(parts) != 2:
            raise ValueError("Use o formato: quote TICKER.")
        symbol = parts[1].upper()
        return MarketCommandResult(
            command=command,
            title=f"Cotacao: {symbol}",
            data=get_equity_quote(symbol),
        )

    if action == "compare":
        if len(parts) < 3:
            raise ValueError("Use o formato: compare TICKER1 TICKER2 ...")
        symbols = [part.upper() for part in parts[1:]]
        return MarketCommandResult(
            command=command,
            title=f"Comparacao: {', '.join(symbols)}",
            data=compare_equities(symbols, start_date=start_date, end_date=end_date),
        )

    raise ValueError("Comando desconhecido. Use quote ou compare.")
