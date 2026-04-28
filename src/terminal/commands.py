from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

import pandas as pd

from src.commands.macro import execute_macro_command
from src.commands.quote_compare import execute_market_command
from src.data.cvm import find_fund_by_cnpj
from src.terminal.parser import CommandRequest


@dataclass
class CommandResult:
    title: str
    message: Optional[str] = None
    dataframe: Optional[pd.DataFrame] = None
    chart: Optional[Any] = None


HELP_TEXT = """
Comandos disponiveis:
- help
- macro selic
- macro ipca
- macro dolar
- quote TICKER
- compare TICKER1 TICKER2 ...
- fund CNPJ
- portfolio risco
""".strip()


def help_command(request: CommandRequest) -> CommandResult:
    return CommandResult(title="Ajuda", message=HELP_TEXT)


def macro_command(request: CommandRequest) -> CommandResult:
    if not request.args:
        return CommandResult(
            title="Macro",
            message="Use macro selic, macro ipca ou macro dolar.",
        )

    indicator = request.args[0].lower()
    if indicator not in {"selic", "ipca", "dolar", "dólar"}:
        return CommandResult(
            title="Macro",
            message=f"Indicador macro ainda nao implementado: {indicator}.",
        )

    try:
        result = execute_macro_command(request.raw)
    except Exception as exc:
        return CommandResult(title=f"Macro {indicator}", message=str(exc))

    return CommandResult(title=result.title, dataframe=result.data)


def quote_command(request: CommandRequest) -> CommandResult:
    if len(request.args) != 1:
        return CommandResult(title="Cotacao", message="Use quote TICKER.")

    symbol = request.args[0].upper()
    try:
        result = execute_market_command(request.raw)
    except Exception as exc:
        return CommandResult(title=f"Cotacao {symbol}", message=str(exc))

    return CommandResult(title=result.title, dataframe=result.data)


def compare_command(request: CommandRequest) -> CommandResult:
    if len(request.args) < 2:
        return CommandResult(title="Comparacao", message="Use compare TICKER1 TICKER2 ...")

    symbols = ", ".join(symbol.upper() for symbol in request.args)
    try:
        result = execute_market_command(request.raw)
    except Exception as exc:
        return CommandResult(title=f"Comparacao {symbols}", message=str(exc))

    return CommandResult(title=result.title, dataframe=result.data)


def portfolio_command(request: CommandRequest) -> CommandResult:
    if request.args and request.args[0].lower() == "risco":
        return CommandResult(
            title="Portfolio risco",
            message="Modulo de risco de portfolio sera implementado em uma etapa propria.",
        )

    return CommandResult(title="Portfolio", message="Use portfolio risco.")


def fund_command(request: CommandRequest) -> CommandResult:
    if len(request.args) != 1:
        return CommandResult(title="Fundos CVM", message="Use fund CNPJ.")

    cnpj = request.args[0]
    try:
        data = find_fund_by_cnpj(cnpj)
    except Exception as exc:
        return CommandResult(title="Fundos CVM", message=str(exc))

    if data.empty:
        return CommandResult(title="Fundos CVM", message="Nenhum fundo encontrado para o CNPJ informado.")

    return CommandResult(title="Fundos CVM", dataframe=data)


def not_implemented_command(request: CommandRequest) -> CommandResult:
    return CommandResult(
        title="Comando nao implementado",
        message=(
            f"O comando '{request.raw}' ainda nao foi implementado. "
            "Use help para ver os comandos reconhecidos."
        ),
    )
