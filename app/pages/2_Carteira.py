import streamlit as st
import pandas as pd
import plotly.express as px

from app.styles import apply_terminal_style, render_page_header
from src.analytics.portfolio import calculate_portfolio_composition


apply_terminal_style()
render_page_header("Carteira", "Upload de CSV e composicao consolidada por ativo e classe.")

uploaded_file = st.file_uploader("CSV da carteira", type=["csv"])

st.caption("Colunas obrigatorias: ativo, quantidade, preco_medio, classe. Coluna opcional: data_compra.")

if uploaded_file is not None:
    try:
        raw_data = pd.read_csv(uploaded_file)
        normalized, by_asset, by_class, total_invested = calculate_portfolio_composition(raw_data)
    except Exception as exc:
        st.error(str(exc))
    else:
        count_col, total_col, class_col = st.columns(3)
        count_col.metric("Ativos", len(by_asset))
        total_col.metric("Total investido", f"R$ {total_invested:,.2f}")
        class_col.metric("Classes", len(by_class))

        st.subheader("Tabela normalizada")
        st.dataframe(normalized, use_container_width=True)

        asset_col, class_col = st.columns(2)
        with asset_col:
            st.subheader("Composicao por ativo")
            fig_asset = px.bar(
                by_asset,
                x="ativo",
                y="valor_investido",
                text=by_asset["percentual"].map(lambda value: f"{value:.1%}"),
                labels={"ativo": "Ativo", "valor_investido": "Valor investido"},
            )
            st.plotly_chart(fig_asset, use_container_width=True)

        with class_col:
            st.subheader("Composicao por classe")
            fig_class = px.pie(
                by_class,
                names="classe",
                values="valor_investido",
                hole=0.45,
            )
            st.plotly_chart(fig_class, use_container_width=True)
