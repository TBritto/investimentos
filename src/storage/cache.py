from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Union

from src.data.errors import DataSourceError


CACHE_ROOT = Path("data/raw")
TEXT_EXTENSIONS = {".csv", ".json", ".txt", ".md", ".html", ".xml"}
CacheContent = Union[bytes, str]


def save_cache(path: str, content: CacheContent) -> None:
    cache_path = Path(path)
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            cache_path.write_bytes(content)
        else:
            cache_path.write_text(content, encoding="utf-8")
    except OSError as exc:
        raise DataSourceError(f"Nao foi possivel salvar cache em {cache_path}: {exc}") from exc


def load_cache(path: str) -> CacheContent | None:
    cache_path = Path(path)
    if not cache_path.exists():
        return None

    try:
        if cache_path.suffix.lower() in TEXT_EXTENSIONS:
            return cache_path.read_text(encoding="utf-8")
        return cache_path.read_bytes()
    except OSError as exc:
        raise DataSourceError(f"Nao foi possivel ler cache em {cache_path}: {exc}") from exc


def cache_exists(path: str) -> bool:
    return Path(path).exists()


def get_cache_path(source: str, key: str, extension: str) -> Path:
    safe_source = _safe_filename_token(source)
    safe_key = _safe_filename_token(key)
    safe_extension = extension.lower().lstrip(".")
    if not safe_extension or not re.fullmatch(r"[a-z0-9]+", safe_extension):
        raise DataSourceError("Extensao de cache invalida.")
    return CACHE_ROOT / safe_source / f"{safe_key}.{safe_extension}"


def _safe_filename_token(value: str) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = re.sub(r"[^a-zA-Z0-9._-]+", "_", text).strip("._-")
    text = re.sub(r"_+", "_", text)
    return text.lower() or "cache"
