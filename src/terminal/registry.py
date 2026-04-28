from __future__ import annotations

from typing import Callable

from src.terminal.commands import (
    CommandResult,
    compare_command,
    finance_command,
    fund_command,
    help_command,
    macro_command,
    not_implemented_command,
    portfolio_command,
    quote_command,
)
from src.terminal.parser import CommandRequest, parse_command


CommandHandler = Callable[[CommandRequest], CommandResult]

COMMAND_REGISTRY: dict[str, CommandHandler] = {
    "help": help_command,
    "macro": macro_command,
    "quote": quote_command,
    "compare": compare_command,
    "fund": fund_command,
    "finance": finance_command,
    "portfolio": portfolio_command,
}


def execute_command(raw: str) -> CommandResult:
    request = parse_command(raw)
    handler = COMMAND_REGISTRY.get(request.command, not_implemented_command)
    return handler(request)
