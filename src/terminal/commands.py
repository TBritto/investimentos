from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

import pandas as pd

from src.commands.macro import execute_macro_command
from src.commands.quote_compare import execute_market_command
from src.data.pluggy import create_connect_token, get_accounts, get_items, get_transactions
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
- openfinance connect-token
- openfinance items
- openfinance accounts
- openfinance transactions ACCOUNT_ID
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


def openfinance_command(request: CommandRequest) -> CommandResult:
    if not request.args:
        return CommandResult(
            title="Open Finance",
            message=(
                "Use openfinance connect-token, openfinance items, "
                "openfinance accounts ou openfinance transactions ACCOUNT_ID."
            ),
        )

    action = request.args[0].lower()
    try:
        if action == "connect-token":
            token = create_connect_token()
            return CommandResult(
                title="Open Finance",
                message=f"Connect token gerado. Use no Pluggy Connect Widget: {token}",
            )
        if action == "items":
            return CommandResult(title="Conexoes Open Finance", dataframe=get_items())
        if action == "accounts":
            item_id = request.args[1] if len(request.args) > 1 else None
            return CommandResult(title="Contas Open Finance", dataframe=get_accounts(item_id=item_id))
        if action == "transactions":
            if len(request.args) < 2:
                return CommandResult(
                    title="Transacoes Open Finance",
                    message="Use openfinance transactions ACCOUNT_ID.",
                )
            return CommandResult(
                title="Transacoes Open Finance",
                dataframe=get_transactions(account_id=request.args[1]),
            )
    except Exception as exc:
        return CommandResult(title="Open Finance", message=str(exc))

    return CommandResult(
        title="Open Finance",
        message=(
            "Comando desconhecido. Use connect-token, items, accounts ou transactions ACCOUNT_ID."
        ),
    )


def not_implemented_command(request: CommandRequest) -> CommandResult:
    return CommandResult(
        title="Comando nao implementado",
        message=(
            f"O comando '{request.raw}' ainda nao foi implementado. "
            "Use help para ver os comandos reconhecidos."
        ),
    )
