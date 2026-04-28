from __future__ import annotations

import datetime as dt

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.analytics.portfolio import (
    calculate_portfolio_returns,
    calculate_risk_metrics,
    parse_weights,
    validate_portfolio_inputs,
)
from src.analytics.technical import add_bollinger_bands, add_moving_averages, add_rsi
from src.data.openbb_client import (
    fetch_financial_ratios,
    fetch_fundamental_statement,
    fetch_price_history,
)
from src.storage.settings import load_settings


def main() -> None:
    load_settings()
    st.set_page_config(page_title="Terminal de Investimentos", layout="wide")

    st.title("Terminal de Investimentos")
    st.caption("MVP em portugues do Brasil para consulta e analise de ativos com OpenBB.")

    ticker, start_date, end_date, moving_average_periods = render_sidebar()
    stock_data = load_price_history(ticker, start_date, end_date)

    render_price_section(ticker, stock_data, moving_average_periods)
    render_fundamentals_section(ticker)
    render_portfolio_section(start_date, end_date)
    render_disclaimer()


def render_sidebar() -> tuple[str, dt.date, dt.date, list[int]]:
    st.sidebar.title("Parametros")
    ticker = st.sidebar.text_input("Ticker", value="AAPL").strip().upper()
    start_date = st.sidebar.date_input("Data inicial", dt.date(2023, 1, 1))
    end_date = st.sidebar.date_input("Data final", dt.date.today())
    moving_average_periods = st.sidebar.multiselect(
        "Medias moveis",
        [5, 10, 20, 50, 100, 200],
        default=[20, 50],
    )
    return ticker, start_date, end_date, moving_average_periods


@st.cache_data
def load_price_history(ticker: str, start_date: dt.date, end_date: dt.date) -> pd.DataFrame:
    try:
        return fetch_price_history(ticker, start_date, end_date)
    except Exception as exc:
        st.error(f"Nao foi possivel buscar dados para {ticker}: {exc}")
        st.stop()


def render_price_section(ticker: str, stock_data: pd.DataFrame, periods: list[int]) -> None:
    st.header(f"Analise de precos: {ticker}")

    fig_price = px.line(
        stock_data,
        x=stock_data.index,
        y="close",
        labels={"close": "Preco de fechamento", "index": "Data"},
    )
    st.plotly_chart(fig_price, use_container_width=True)

    with st.expander("Indicadores tecnicos", expanded=True):
        data_with_indicators = add_rsi(add_bollinger_bands(add_moving_averages(stock_data, periods)))

        fig_ma = go.Figure()
        fig_ma.add_trace(
            go.Scatter(x=data_with_indicators.index, y=data_with_indicators["close"], name="Fechamento")
        )
        for period in periods:
            fig_ma.add_trace(
                go.Scatter(
                    x=data_with_indicators.index,
                    y=data_with_indicators[f"MM_{period}"],
                    name=f"MM {period}",
                )
            )
        st.plotly_chart(fig_ma, use_container_width=True)

        col_bollinger, col_rsi = st.columns(2)
        with col_bollinger:
            fig_bb = go.Figure()
            fig_bb.add_trace(
                go.Scatter(
                    x=data_with_indicators.index,
                    y=data_with_indicators["BB_superior"],
                    name="Banda superior",
                )
            )
            fig_bb.add_trace(
                go.Scatter(
                    x=data_with_indicators.index,
                    y=data_with_indicators["BB_inferior"],
                    name="Banda inferior",
                    fill="tonexty",
                )
            )
            fig_bb.add_trace(
                go.Scatter(x=data_with_indicators.index, y=data_with_indicators["close"], name="Fechamento")
            )
            st.plotly_chart(fig_bb, use_container_width=True)

        with col_rsi:
            fig_rsi = px.line(
                data_with_indicators,
                x=data_with_indicators.index,
                y="RSI",
                labels={"index": "Data", "RSI": "RSI"},
            )
            fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
            fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
            st.plotly_chart(fig_rsi, use_container_width=True)


def render_fundamentals_section(ticker: str) -> None:
    st.header("Fundamentos")
    statement_type = st.selectbox("Demonstrativo", ["DRE", "Balanco", "Fluxo de caixa"])

    fundamentals_col, ratios_col = st.columns(2)
    with fundamentals_col:
        try:
            st.dataframe(fetch_fundamental_statement(ticker, statement_type), use_container_width=True)
        except Exception as exc:
            st.warning(f"Demonstrativo indisponivel no provedor configurado: {exc}")

    with ratios_col:
        try:
            st.dataframe(fetch_financial_ratios(ticker), use_container_width=True)
        except Exception as exc:
            st.warning(f"Indicadores fundamentalistas indisponiveis: {exc}")


def render_portfolio_section(start_date: dt.date, end_date: dt.date) -> None:
    st.header("Simulacao de carteira")
    tickers_input = st.text_input("Ativos separados por virgula", value="AAPL,MSFT,GOOGL")
    weights_input = st.text_input("Pesos separados por virgula", value="0.4,0.3,0.3")

    tickers = [ticker.strip().upper() for ticker in tickers_input.split(",") if ticker.strip()]
    try:
        weights = parse_weights(weights_input)
        validate_portfolio_inputs(tickers, weights)
        portfolio_prices = fetch_portfolio_prices(tickers, start_date, end_date)
        portfolio_returns = calculate_portfolio_returns(portfolio_prices, weights)
        cumulative_returns = (1 + portfolio_returns).cumprod()
        metrics = calculate_risk_metrics(portfolio_returns)
    except Exception as exc:
        st.warning(f"Nao foi possivel simular a carteira: {exc}")
        return

    st.plotly_chart(
        px.line(cumulative_returns, labels={"index": "Data", "value": "Retorno acumulado"}),
        use_container_width=True,
    )
    col_return, col_volatility, col_sharpe = st.columns(3)
    col_return.metric("Retorno anualizado", f"{metrics['annual_return']:.2%}")
    col_volatility.metric("Volatilidade anualizada", f"{metrics['annual_volatility']:.2%}")
    col_sharpe.metric("Sharpe", f"{metrics['sharpe_ratio']:.2f}")


@st.cache_data
def fetch_portfolio_prices(tickers: list[str], start_date: dt.date, end_date: dt.date) -> pd.DataFrame:
    prices = pd.DataFrame()
    for ticker in tickers:
        data = fetch_price_history(ticker, start_date, end_date)
        prices[ticker] = data["close"]
    return prices


def render_disclaimer() -> None:
    st.markdown("---")
    st.caption(
        "Conteudo informativo e educacional. Este MVP nao realiza recomendacao automatica "
        "de compra, venda ou manutencao de ativos."
    )
