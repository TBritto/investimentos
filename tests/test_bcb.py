import pandas as pd
import pytest
import requests

from src.data import bcb
from src.data.bcb import BCBClientError, get_ipca, get_selic, get_sgs_series, get_usdbrl


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self.payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            error = requests.HTTPError("http error")
            error.response = self
            raise error

    def json(self):
        return self.payload


def test_get_sgs_series_normalizes_payload_and_writes_cache(monkeypatch, tmp_path):
    calls = []

    def fake_get(url, params, timeout):
        calls.append((url, params, timeout))
        return FakeResponse(
            [
                {"data": "01/01/2024", "valor": "10,50"},
                {"data": "02/01/2024", "valor": "10.75"},
            ]
        )

    monkeypatch.setattr(bcb, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(bcb.requests, "get", fake_get)

    data = get_sgs_series(432, start_date="2024-01-01", end_date="2024-01-02")

    assert list(data.columns) == ["date", "value", "code"]
    assert data["date"].tolist() == [pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-02")]
    assert data["value"].tolist() == [10.5, 10.75]
    assert data["code"].tolist() == [432, 432]
    assert calls[0][1] == {
        "formato": "json",
        "dataInicial": "01/01/2024",
        "dataFinal": "02/01/2024",
    }

    cached = get_sgs_series(432, start_date="2024-01-01", end_date="2024-01-02")

    assert len(calls) == 1
    pd.testing.assert_frame_equal(cached, data, check_dtype=False)


def test_get_sgs_series_can_bypass_cache(monkeypatch, tmp_path):
    calls = []

    def fake_get(url, params, timeout):
        calls.append(params)
        return FakeResponse([{"data": "01/01/2024", "valor": str(len(calls))}])

    monkeypatch.setattr(bcb, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(bcb.requests, "get", fake_get)

    first = get_sgs_series(432, use_cache=False)
    second = get_sgs_series(432, use_cache=False)

    assert len(calls) == 2
    assert first["value"].tolist() == [1.0]
    assert second["value"].tolist() == [2.0]
    assert not list(tmp_path.rglob("*.csv"))


def test_get_sgs_series_raises_friendly_http_error(monkeypatch, tmp_path):
    def fake_get(url, params, timeout):
        return FakeResponse([], status_code=500)

    monkeypatch.setattr(bcb, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(bcb.requests, "get", fake_get)

    with pytest.raises(BCBClientError, match="Erro HTTP 500"):
        get_sgs_series(432)


def test_get_sgs_series_raises_for_empty_response(monkeypatch, tmp_path):
    def fake_get(url, params, timeout):
        return FakeResponse([])

    monkeypatch.setattr(bcb, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(bcb.requests, "get", fake_get)

    with pytest.raises(BCBClientError, match="Resposta vazia"):
        get_sgs_series(432)


def test_get_sgs_series_raises_for_invalid_request_date(monkeypatch, tmp_path):
    def fail_if_called(url, params, timeout):
        raise AssertionError("requests.get nao deveria ser chamado com data invalida")

    monkeypatch.setattr(bcb, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(bcb.requests, "get", fail_if_called)

    with pytest.raises(BCBClientError, match="Data invalida"):
        get_sgs_series(432, start_date="nao-e-data")


def test_get_sgs_series_raises_for_invalid_payload_date(monkeypatch, tmp_path):
    def fake_get(url, params, timeout):
        return FakeResponse([{"data": "2024-01-01", "valor": "10,5"}])

    monkeypatch.setattr(bcb, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(bcb.requests, "get", fake_get)

    with pytest.raises(BCBClientError, match="Data invalida"):
        get_sgs_series(432)


def test_get_sgs_series_raises_for_invalid_numeric_value(monkeypatch, tmp_path):
    def fake_get(url, params, timeout):
        return FakeResponse([{"data": "01/01/2024", "valor": "abc"}])

    monkeypatch.setattr(bcb, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(bcb.requests, "get", fake_get)

    with pytest.raises(BCBClientError, match="Valor numerico invalido"):
        get_sgs_series(432)


def test_bcb_helpers_use_expected_codes(monkeypatch, tmp_path):
    requested_codes = []

    def fake_get_sgs_series(code, start_date=None, end_date=None):
        requested_codes.append((code, start_date, end_date))
        return pd.DataFrame({"date": [pd.Timestamp("2024-01-01")], "value": [1.0], "code": [code]})

    monkeypatch.setattr(bcb, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(bcb, "get_sgs_series", fake_get_sgs_series)

    get_selic("2024-01-01", "2024-01-31")
    get_ipca()
    get_usdbrl()

    assert requested_codes == [
        (bcb.SELIC_CODE, "2024-01-01", "2024-01-31"),
        (bcb.IPCA_CODE, None, None),
        (bcb.USDBRL_CODE, None, None),
    ]
