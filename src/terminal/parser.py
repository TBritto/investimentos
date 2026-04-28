from __future__ import annotations

import shlex
from dataclasses import dataclass


@dataclass
class CommandRequest:
    raw: str
    command: str
    args: list[str]


def parse_command(raw: str) -> CommandRequest:
    cleaned = raw.strip()
    if not cleaned:
        raise ValueError("Digite um comando.")

    try:
        parts = shlex.split(cleaned)
    except ValueError as exc:
        raise ValueError(f"Comando invalido: {exc}") from exc

    if not parts:
        raise ValueError("Digite um comando.")

    return CommandRequest(raw=cleaned, command=parts[0].lower(), args=parts[1:])
