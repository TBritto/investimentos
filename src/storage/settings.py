from __future__ import annotations

from dotenv import load_dotenv


def load_settings() -> None:
    """Carrega variaveis do .env sem acoplar storage a providers externos."""
    load_dotenv()
