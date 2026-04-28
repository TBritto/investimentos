import pytest
import requests

from src.data.errors import (
    DataParsingError,
    DataSourceError,
    DataUnavailableError,
    DataValidationError,
)
from src.data.http import get_url


class FakeResponse:
    def __init__(self, content=b"ok", status_code=200):
        self.content = content
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            error = requests.HTTPError("http error")
            error.response = self
            raise error


def test_common_errors_share_base_class():
    assert issubclass(DataUnavailableError, DataSourceError)
    assert issubclass(DataParsingError, DataSourceError)
    assert issubclass(DataValidationError, DataSourceError)


def test_get_url_returns_bytes(monkeypatch):
    calls = []

    def fake_get(url, timeout, headers):
        calls.append((url, timeout, headers))
        return FakeResponse(b"payload")

    monkeypatch.setattr("src.data.http.requests.get", fake_get)

    content = get_url("https://example.test/data.csv", timeout=10, headers={"X-Test": "1"})

    assert content == b"payload"
    assert calls == [("https://example.test/data.csv", 10, {"X-Test": "1"})]


def test_get_url_wraps_http_error(monkeypatch):
    def fake_get(url, timeout, headers):
        return FakeResponse(status_code=500)

    monkeypatch.setattr("src.data.http.requests.get", fake_get)

    with pytest.raises(DataUnavailableError, match="Erro HTTP 500"):
        get_url("https://example.test/data.csv")


def test_get_url_wraps_connection_error(monkeypatch):
    def fake_get(url, timeout, headers):
        raise requests.ConnectionError("offline")

    monkeypatch.setattr("src.data.http.requests.get", fake_get)

    with pytest.raises(DataUnavailableError, match="Fonte de dados indisponivel"):
        get_url("https://example.test/data.csv")


def test_get_url_rejects_empty_response(monkeypatch):
    def fake_get(url, timeout, headers):
        return FakeResponse(b"")

    monkeypatch.setattr("src.data.http.requests.get", fake_get)

    with pytest.raises(DataUnavailableError, match="Resposta vazia"):
        get_url("https://example.test/data.csv")
