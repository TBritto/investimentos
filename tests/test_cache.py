from pathlib import Path

import pytest

from src.data.errors import DataSourceError
from src.storage import cache
from src.storage.cache import cache_exists, get_cache_path, load_cache, save_cache


def test_save_and_load_text_cache_creates_directories(tmp_path):
    path = tmp_path / "nested" / "data.csv"

    save_cache(str(path), "a,b\n1,2\n")

    assert cache_exists(str(path))
    assert load_cache(str(path)) == "a,b\n1,2\n"


def test_save_and_load_binary_cache(tmp_path):
    path = tmp_path / "nested" / "data.zip"

    save_cache(str(path), b"zip-bytes")

    assert load_cache(str(path)) == b"zip-bytes"


def test_load_cache_returns_none_when_missing(tmp_path):
    assert load_cache(str(tmp_path / "missing.csv")) is None


def test_get_cache_path_sanitizes_source_and_key(monkeypatch, tmp_path):
    monkeypatch.setattr(cache, "CACHE_ROOT", tmp_path)

    path = get_cache_path("Banco Central/SGS", "selic 432:2024/01", "csv")

    assert path == tmp_path / "banco_central_sgs" / "selic_432_2024_01.csv"


def test_get_cache_path_rejects_invalid_extension(monkeypatch, tmp_path):
    monkeypatch.setattr(cache, "CACHE_ROOT", tmp_path)

    with pytest.raises(DataSourceError, match="Extensao de cache invalida"):
        get_cache_path("source", "key", "../csv")
