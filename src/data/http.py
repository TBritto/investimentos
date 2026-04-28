from __future__ import annotations

from typing import Optional

import requests

from src.data.errors import DataUnavailableError


def get_url(
    url: str,
    timeout: int = 30,
    headers: Optional[dict] = None,
) -> bytes:
    """Baixa uma URL e retorna o corpo em bytes com erros amigaveis."""
    try:
        response = requests.get(url, timeout=timeout, headers=headers)
        response.raise_for_status()
    except requests.HTTPError as exc:
        status_code = exc.response.status_code if exc.response is not None else "desconhecido"
        raise DataUnavailableError(f"Erro HTTP {status_code} ao acessar fonte de dados: {url}") from exc
    except requests.RequestException as exc:
        raise DataUnavailableError(f"Fonte de dados indisponivel: {url}. Detalhe: {exc}") from exc

    if not response.content:
        raise DataUnavailableError(f"Resposta vazia da fonte de dados: {url}")

    return response.content
