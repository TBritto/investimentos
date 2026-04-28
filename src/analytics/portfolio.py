from __future__ import annotations

import math

import pandas as pd


REQUIRED_PORTFOLIO_COLUMNS = {"ativo", "quantidade", "preco_medio", "classe"}
OPTIONAL_PORTFOLIO_COLUMNS = {"data_compra"}


def parse_weights(raw_weights: str) -> list[float]:
    return [float(weight.strip()) for weight in raw_weights.split(",") if weight.strip()]


def validate_portfolio_inputs(tickers: list[str], weights: list[float]) -> None:
    if len(tickers) != len(weights):
        raise ValueError("A quantidade de ativos e pesos precisa ser igual.")
    if not math.isclose(sum(weights), 1.0, rel_tol=1e-9, abs_tol=1e-9):
        raise ValueError("A soma dos pesos precisa ser 1.")


def calculate_portfolio_returns(prices: pd.DataFrame, weights: list[float]) -> pd.Series:
    returns = prices.pct_change().dropna()
    return returns.dot(weights)


def calculate_risk_metrics(portfolio_returns: pd.Series) -> dict[str, float]:
    volatility = portfolio_returns.std() * (252 ** 0.5)
    annual_return = portfolio_returns.mean() * 252
    sharpe_ratio = annual_return / volatility if volatility else 0.0
    return {
        "annual_return": annual_return,
        "annual_volatility": volatility,
        "sharpe_ratio": sharpe_ratio,
    }


def validate_portfolio_csv_columns(data: pd.DataFrame) -> None:
    missing_columns = REQUIRED_PORTFOLIO_COLUMNS - set(data.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"CSV sem colunas obrigatorias: {missing}.")


def normalize_portfolio_csv(data: pd.DataFrame) -> pd.DataFrame:
    validate_portfolio_csv_columns(data)
    normalized = data.copy()
    normalized.columns = [column.strip() for column in normalized.columns]
    normalized["ativo"] = normalized["ativo"].astype(str).str.strip().str.upper()
    normalized["classe"] = normalized["classe"].astype(str).str.strip()
    normalized["quantidade"] = pd.to_numeric(normalized["quantidade"], errors="coerce")
    normalized["preco_medio"] = pd.to_numeric(normalized["preco_medio"], errors="coerce")

    invalid_rows = normalized["ativo"].eq("") | normalized["quantidade"].isna() | normalized["preco_medio"].isna()
    if invalid_rows.any():
        raise ValueError("CSV possui linhas com ativo vazio, quantidade invalida ou preco_medio invalido.")

    if (normalized["quantidade"] < 0).any() or (normalized["preco_medio"] < 0).any():
        raise ValueError("Quantidade e preco_medio devem ser maiores ou iguais a zero.")

    if "data_compra" in normalized.columns:
        normalized["data_compra"] = pd.to_datetime(normalized["data_compra"], errors="coerce")

    return normalized


def calculate_portfolio_composition(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, float]:
    normalized = normalize_portfolio_csv(data)
    normalized["valor_investido"] = normalized["quantidade"] * normalized["preco_medio"]
    total_invested = float(normalized["valor_investido"].sum())
    if total_invested <= 0:
        raise ValueError("Total investido precisa ser maior que zero.")

    by_asset = (
        normalized.groupby("ativo", as_index=False)
        .agg(valor_investido=("valor_investido", "sum"), classe=("classe", "first"))
        .sort_values("valor_investido", ascending=False)
        .reset_index(drop=True)
    )
    by_asset["percentual"] = by_asset["valor_investido"] / total_invested

    by_class = (
        normalized.groupby("classe", as_index=False)
        .agg(valor_investido=("valor_investido", "sum"))
        .sort_values("valor_investido", ascending=False)
        .reset_index(drop=True)
    )
    by_class["percentual"] = by_class["valor_investido"] / total_invested

    normalized["percentual"] = normalized["valor_investido"] / total_invested
    return normalized, by_asset, by_class, total_invested
