import io
import zipfile

import pandas as pd
import pytest
import requests

from src.data import cvm
from src.data.cvm import (
    CVMClientError,
    find_fund_by_cnpj,
    get_fund_daily_report,
    get_fund_registry,
    normalize_cnpj,
    search_funds,
)


class FakeResponse:
    def __init__(self, content, status_code=200):
        self.content = content
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            error = requests.HTTPError("http error")
            error.response = self
            raise error


def make_zip(csv_text):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("inf_diario.csv", csv_text.encode("latin1"))
    return buffer.getvalue()


def test_normalize_cnpj_strips_punctuation():
    assert normalize_cnpj("00.000.000/0001-91") == "00000000000191"


def test_normalize_cnpj_rejects_invalid_value():
    with pytest.raises(CVMClientError, match="CNPJ invalido"):
        normalize_cnpj("123")


def test_get_fund_registry_downloads_normalizes_and_caches(monkeypatch, tmp_path):
    calls = []
    csv_text = (
        "CNPJ_FUNDO;DENOM_SOCIAL;SIT\n"
        "00.000.000/0001-91;Fundo Alpha;EM FUNCIONAMENTO NORMAL\n"
        "11.111.111/1111-11;Fundo Beta;CANCELADA\n"
    )

    def fake_get(url, timeout):
        calls.append((url, timeout))
        return FakeResponse(csv_text.encode("latin1"))

    monkeypatch.setattr(cvm, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(cvm.requests, "get", fake_get)

    data = get_fund_registry()

    assert calls == [(cvm.FUND_REGISTRY_URL, 60)]
    assert list(data.columns) == ["cnpj_fundo", "denom_social", "sit"]
    assert data["cnpj_fundo"].tolist() == ["00000000000191", "11111111111111"]

    cached = get_fund_registry()

    assert len(calls) == 1
    pd.testing.assert_frame_equal(cached, data)


def test_search_and_find_funds_use_registry(monkeypatch):
    registry = pd.DataFrame(
        {
            "cnpj_fundo": ["00000000000191", "11111111111111"],
            "denom_social": ["Fundo Crédito Alpha", "Fundo Beta"],
        }
    )

    monkeypatch.setattr(cvm, "get_fund_registry", lambda: registry)

    by_name = search_funds("credito")
    by_cnpj_fragment = search_funds("1111")
    exact = find_fund_by_cnpj("00.000.000/0001-91")

    assert by_name["cnpj_fundo"].tolist() == ["00000000000191"]
    assert by_cnpj_fragment["cnpj_fundo"].tolist() == ["11111111111111"]
    assert exact["denom_social"].tolist() == ["Fundo Crédito Alpha"]


def test_get_fund_daily_report_parses_mocked_zip(monkeypatch, tmp_path):
    csv_text = (
        "CNPJ_FUNDO;DT_COMPTC;VL_QUOTA;VL_PATRIM_LIQ;CAPTC_DIA;RESG_DIA;NR_COTST\n"
        "00.000.000/0001-91;2024-01-31;1,2345;1000,50;10,00;5,00;123\n"
    )
    calls = []

    def fake_get(url, timeout):
        calls.append((url, timeout))
        return FakeResponse(make_zip(csv_text))

    monkeypatch.setattr(cvm, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(cvm.requests, "get", fake_get)

    data = get_fund_daily_report(2024, 1)

    assert calls == [(cvm.DAILY_REPORT_URL_TEMPLATE.format(year=2024, month=1), 60)]
    assert list(data.columns) == cvm.DAILY_REPORT_COLUMNS
    assert data.iloc[0]["cnpj_fundo"] == "00000000000191"
    assert data.iloc[0]["data_competencia"] == pd.Timestamp("2024-01-31")
    assert data.iloc[0]["valor_cota"] == 1.2345
    assert data.iloc[0]["patrimonio_liquido"] == 1000.50
    assert data.iloc[0]["numero_cotistas"] == 123


def test_get_fund_daily_report_uses_cache(monkeypatch, tmp_path):
    csv_text = (
        "CNPJ_FUNDO;DT_COMPTC;VL_QUOTA;VL_PATRIM_LIQ;CAPTC_DIA;RESG_DIA;NR_COTST\n"
        "00.000.000/0001-91;2024-01-31;1,0;1000,0;0,0;0,0;10\n"
    )
    calls = []

    def fake_get(url, timeout):
        calls.append(url)
        return FakeResponse(make_zip(csv_text))

    monkeypatch.setattr(cvm, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(cvm.requests, "get", fake_get)

    first = get_fund_daily_report(2024, 1)
    second = get_fund_daily_report(2024, 1)

    assert len(calls) == 1
    pd.testing.assert_frame_equal(first, second)


def test_get_fund_daily_report_rejects_invalid_zip(monkeypatch, tmp_path):
    def fake_get(url, timeout):
        return FakeResponse(b"not a zip")

    monkeypatch.setattr(cvm, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(cvm.requests, "get", fake_get)

    with pytest.raises(CVMClientError, match="ZIP invalido"):
        get_fund_daily_report(2024, 1)


def test_get_fund_daily_report_rejects_unexpected_columns(monkeypatch, tmp_path):
    def fake_get(url, timeout):
        return FakeResponse(make_zip("CNPJ_FUNDO;DT_COMPTC\n00.000.000/0001-91;2024-01-31\n"))

    monkeypatch.setattr(cvm, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(cvm.requests, "get", fake_get)

    with pytest.raises(CVMClientError, match="sem colunas esperadas"):
        get_fund_daily_report(2024, 1)


def test_download_http_404_returns_friendly_error(monkeypatch, tmp_path):
    def fake_get(url, timeout):
        return FakeResponse(b"", status_code=404)

    monkeypatch.setattr(cvm, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(cvm.requests, "get", fake_get)

    with pytest.raises(CVMClientError, match="Arquivo CVM nao encontrado"):
        get_fund_registry()
