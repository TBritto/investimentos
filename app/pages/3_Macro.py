import streamlit as st
import plotly.express as px
import pandas as pd

from app.styles import apply_terminal_style, render_page_header
from src.analytics.macro import get_period_start, latest_value
from src.data.bcb import get_ipca, get_selic, get_usdbrl


apply_terminal_style()
render_page_header("Macro", "Series publicas do Banco Central SGS em leitura compacta.")


def render_indicator(name: str, data: pd.DataFrame) -> None:
    last_value = latest_value(data)
    st.metric(name, "Sem dados" if last_value is None else f"{last_value:.2f}")
    if data.empty:
        st.warning(f"Sem dados disponiveis para {name}.")
        return

    fig = px.line(data, x="date", y="value", title=name, labels={"date": "Data", "value": "Valor"})
    st.plotly_chart(fig, use_container_width=True)
    with st.expander(f"Dados de {name}"):
        st.dataframe(data.sort_values("date", ascending=False), use_container_width=True)


period = st.selectbox("Periodo", ["1 ano", "5 anos", "maximo"])
start_date = get_period_start(period)

indicators = [
    ("Selic", get_selic),
    ("IPCA", get_ipca),
    ("Dolar", get_usdbrl),
]

for name, fetcher in indicators:
    try:
        indicator_data = fetcher(start_date=start_date)
    except Exception as exc:
        st.error(f"Nao foi possivel carregar {name}: {exc}")
        continue

    render_indicator(name, indicator_data)
