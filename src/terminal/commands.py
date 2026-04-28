from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

import pandas as pd

from src.commands.macro import execute_macro_command
from src.commands.quote_compare import execute_market_command
from src.data.firefly import get_accounts, get_categories, get_finance_summary, get_transactions
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
- finance accounts
- finance transactions
- finance categories
- finance summary
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


def finance_command(request: CommandRequest) -> CommandResult:
    if not request.args:
        return CommandResult(
            title="Financas pessoais",
            message="Use finance accounts, finance transactions, finance categories ou finance summary.",
        )

    action = request.args[0].lower()
    try:
        if action == "accounts":
            return CommandResult(title="Contas Firefly III", dataframe=get_accounts())
        if action == "transactions":
            return CommandResult(title="Transacoes Firefly III", dataframe=get_transactions())
        if action == "categories":
            return CommandResult(title="Categorias Firefly III", dataframe=get_categories())
        if action == "summary":
            return CommandResult(title="Resumo Firefly III", dataframe=get_finance_summary())
    except Exception as exc:
        return CommandResult(title="Financas pessoais", message=str(exc))

    return CommandResult(
        title="Financas pessoais",
        message="Comando desconhecido. Use finance accounts, transactions, categories ou summary.",
    )


def not_implemented_command(request: CommandRequest) -> CommandResult:
    return CommandResult(
        title="Comando nao implementado",
        message=(
            f"O comando '{request.raw}' ainda nao foi implementado. "
            "Use help para ver os comandos reconhecidos."
        ),
    )
