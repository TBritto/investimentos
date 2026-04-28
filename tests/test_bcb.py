import pandas as pd
import pytest

from src.data import bcb
from src.data.bcb import BCBClientError, get_ipca, get_selic, get_sgs_series, get_usdbrl


def test_get_sgs_series_normalizes_payload_and_writes_cache(monkeypatch, tmp_path):
    calls = []

    def fake_get_url(url, timeout):
        calls.append((url, timeout))
        return (
            b'[{"data": "01/01/2024", "valor": "10,50"},'
            b'{"data": "02/01/2024", "valor": "10.75"}]'
        )

    monkeypatch.setattr(bcb, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(bcb, "get_url", fake_get_url)

    data = get_sgs_series(432, start_date="2024-01-01", end_date="2024-01-02")

    assert list(data.columns) == ["date", "value", "code"]
    assert data["date"].tolist() == [pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-02")]
    assert data["value"].tolist() == [10.5, 10.75]
    assert data["code"].tolist() == [432, 432]
    assert calls[0][0].startswith("https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados?")
    assert "formato=json" in calls[0][0]
    assert "dataInicial=01%2F01%2F2024" in calls[0][0]
    assert "dataFinal=02%2F01%2F2024" in calls[0][0]

    cached = get_sgs_series(432, start_date="2024-01-01", end_date="2024-01-02")

    assert len(calls) == 1
    pd.testing.assert_frame_equal(cached, data, check_dtype=False)


def test_get_sgs_series_raises_friendly_http_error(monkeypatch, tmp_path):
    def fake_get_url(url, timeout):
        raise bcb.BCBClientError("Erro HTTP 500 ao acessar fonte de dados")

    monkeypatch.setattr(bcb, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(bcb, "get_url", fake_get_url)

    with pytest.raises(BCBClientError, match="Erro HTTP 500"):
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
