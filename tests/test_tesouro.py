import io

import pandas as pd
import pytest
import requests

from src.data import tesouro
from src.data.tesouro import (
    TesouroClientError,
    get_treasury_bonds,
    get_treasury_price_history,
    normalize_treasury_bonds,
    search_treasury_bonds,
)


class FakeResponse:
    def __init__(self, content=b"", payload=None, status_code=200):
        self.content = content
        self.payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            error = requests.HTTPError("http error")
            error.response = self
            raise error

    def json(self):
        if self.payload is None:
            raise ValueError("no json")
        return self.payload


def package_payload(csv_url="https://example.test/precotaxatesourodireto.csv"):
    return {
        "success": True,
        "result": {
            "resources": [
                {"format": "PDF", "url": "https://example.test/meta.pdf"},
                {"format": "CSV", "url": csv_url},
            ]
        },
    }


def sample_csv():
    return (
        "Tipo Titulo;Data Vencimento;Taxa Compra Manha;Taxa Venda Manha;"
        "PU Compra Manha;PU Venda Manha;Data Base\n"
        "Tesouro Selic;01/03/2027;0,01;0,02;15000,50;14990,25;28/04/2026\n"
        "Tesouro IPCA+;15/05/2035;6,10;6,20;2500,75;2490,10;28/04/2026\n"
        "Tesouro Prefixado;01/01/2029;12,50;12,60;700,00;690,00;27/04/2026\n"
    ).encode("latin1")


def test_normalize_treasury_bonds_parses_dates_rates_and_prices():
    raw = pd.DataFrame(
        {
            "Tipo Titulo": ["Tesouro IPCA+"],
            "Data Vencimento": ["15/05/2035"],
            "Taxa Compra Manha": ["6,10"],
            "Taxa Venda Manha": ["6,20"],
            "PU Compra Manha": ["2.500,75"],
            "PU Venda Manha": ["2.490,10"],
            "Data Base": ["28/04/2026"],
        }
    )

    data = normalize_treasury_bonds(raw)

    assert list(data.columns) == tesouro.NORMALIZED_COLUMNS
    assert data.iloc[0]["nome"] == "Tesouro IPCA+ 15/05/2035"
    assert data.iloc[0]["vencimento"] == pd.Timestamp("2035-05-15")
    assert data.iloc[0]["data_base"] == pd.Timestamp("2026-04-28")
    assert data.iloc[0]["taxa_compra"] == 6.10
    assert data.iloc[0]["preco_compra"] == 2500.75


def test_get_treasury_price_history_downloads_and_caches(monkeypatch, tmp_path):
    calls = []

    def fake_get(url, timeout):
        calls.append((url, timeout))
        if url == tesouro.CKAN_PACKAGE_URL:
            return FakeResponse(payload=package_payload())
        return FakeResponse(content=sample_csv())

    monkeypatch.setattr(tesouro, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(tesouro, "PRICE_HISTORY_CACHE", tmp_path / "precotaxatesourodireto.csv")
    monkeypatch.setattr(tesouro.requests, "get", fake_get)

    first = get_treasury_price_history()
    second = get_treasury_price_history()

    assert len(calls) == 2
    assert calls[0] == (tesouro.CKAN_PACKAGE_URL, 30)
    assert len(first) == 3
    pd.testing.assert_frame_equal(first, second)


def test_get_treasury_price_history_filters_year(monkeypatch, tmp_path):
    def fake_get(url, timeout):
        if url == tesouro.CKAN_PACKAGE_URL:
            return FakeResponse(payload=package_payload())
        return FakeResponse(content=sample_csv())

    monkeypatch.setattr(tesouro, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(tesouro, "PRICE_HISTORY_CACHE", tmp_path / "precotaxatesourodireto.csv")
    monkeypatch.setattr(tesouro.requests, "get", fake_get)

    data = get_treasury_price_history(year=2026)

    assert set(data["data_base"].dt.year) == {2026}


def test_get_treasury_bonds_returns_latest_date(monkeypatch):
    history = normalize_treasury_bonds(pd.read_csv(io.BytesIO(sample_csv()), sep=";", dtype=str))

    monkeypatch.setattr(tesouro, "get_treasury_price_history", lambda use_cache=True: history)

    data = get_treasury_bonds()

    assert data["data_base"].nunique() == 1
    assert data["data_base"].iloc[0] == pd.Timestamp("2026-04-28")
    assert set(data["tipo"]) == {"Tesouro Selic", "Tesouro IPCA+"}


def test_search_treasury_bonds_filters_by_name(monkeypatch):
    bonds = normalize_treasury_bonds(pd.read_csv(io.BytesIO(sample_csv()), sep=";", dtype=str))
    latest = bonds.loc[bonds["data_base"] == pd.Timestamp("2026-04-28")].reset_index(drop=True)

    monkeypatch.setattr(tesouro, "get_treasury_bonds", lambda: latest)

    data = search_treasury_bonds("ipca")

    assert data["tipo"].tolist() == ["Tesouro IPCA+"]


def test_source_unavailable_returns_friendly_error(monkeypatch, tmp_path):
    def fake_get(url, timeout):
        raise requests.ConnectionError("offline")

    monkeypatch.setattr(tesouro, "PRICE_HISTORY_CACHE", tmp_path / "precotaxatesourodireto.csv")
    monkeypatch.setattr(tesouro.requests, "get", fake_get)

    with pytest.raises(TesouroClientError, match="Fonte do Tesouro Direto indisponivel"):
        get_treasury_price_history()


def test_unexpected_metadata_raises_friendly_error(monkeypatch, tmp_path):
    def fake_get(url, timeout):
        return FakeResponse(payload={"success": True, "result": {"resources": []}})

    monkeypatch.setattr(tesouro, "PRICE_HISTORY_CACHE", tmp_path / "precotaxatesourodireto.csv")
    monkeypatch.setattr(tesouro.requests, "get", fake_get)

    with pytest.raises(TesouroClientError, match="sem recurso CSV esperado"):
        get_treasury_price_history()


def test_unexpected_csv_columns_raise_friendly_error():
    with pytest.raises(TesouroClientError, match="sem colunas esperadas"):
        normalize_treasury_bonds(pd.DataFrame({"foo": ["bar"]}))


def test_empty_response_raises_friendly_error(monkeypatch, tmp_path):
    def fake_get(url, timeout):
        if url == tesouro.CKAN_PACKAGE_URL:
            return FakeResponse(payload=package_payload())
        return FakeResponse(content=b"")

    monkeypatch.setattr(tesouro, "PRICE_HISTORY_CACHE", tmp_path / "precotaxatesourodireto.csv")
    monkeypatch.setattr(tesouro.requests, "get", fake_get)

    with pytest.raises(TesouroClientError, match="Resposta vazia"):
        get_treasury_price_history()
