import pandas as pd
import plotly.express as px
import streamlit as st

from app.styles import apply_terminal_style, render_page_header
from src.analytics.portfolio import calculate_portfolio_composition


ATIVOS_INOVAR = [
    {"ativo": "PETR4", "classe": "Acoes"},
    {"ativo": "VALE3", "classe": "Acoes"},
    {"ativo": "ITUB4", "classe": "Acoes"},
    {"ativo": "BBAS3", "classe": "Acoes"},
    {"ativo": "BOVA11", "classe": "ETF"},
    {"ativo": "SMAL11", "classe": "ETF"},
    {"ativo": "HGLG11", "classe": "FII"},
    {"ativo": "KNRI11", "classe": "FII"},
    {"ativo": "MXRF11", "classe": "FII"},
    {"ativo": "TESOURO-SELIC", "classe": "Renda fixa"},
    {"ativo": "CDB-DI", "classe": "Renda fixa"},
]


apply_terminal_style()
render_page_header(
    "Carteira",
    "Monte sua carteira com ativos da lista INOVAR ou carregue um CSV para ver a composicao consolidada.",
)


def render_portfolio_analysis(raw_data: pd.DataFrame) -> None:
    normalized, by_asset, by_class, total_invested = calculate_portfolio_composition(raw_data)

    count_col, total_col, class_col = st.columns(3)
    count_col.metric("Ativos", len(by_asset))
    total_col.metric("Total investido", f"R$ {total_invested:,.2f}")
    class_col.metric("Classes", len(by_class))

    st.subheader("Tabela normalizada")
    st.dataframe(normalized, use_container_width=True)

    asset_col, class_col_chart = st.columns(2)
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

    with class_col_chart:
        st.subheader("Composicao por classe")
        fig_class = px.pie(
            by_class,
            names="classe",
            values="valor_investido",
            hole=0.45,
        )
        st.plotly_chart(fig_class, use_container_width=True)


tab_create, tab_upload = st.tabs(["Criar carteira (INOVAR)", "Upload CSV"])

with tab_create:
    st.caption("Selecione ativos da lista INOVAR e informe quantidade/preco medio para montar sua carteira.")

    inovar_catalog = pd.DataFrame(ATIVOS_INOVAR)
    default_table = inovar_catalog.assign(quantidade=0.0, preco_medio=0.0)

    edited = st.data_editor(
        default_table,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        column_config={
            "ativo": st.column_config.TextColumn(disabled=True),
            "classe": st.column_config.TextColumn(disabled=True),
            "quantidade": st.column_config.NumberColumn(min_value=0.0, step=1.0),
            "preco_medio": st.column_config.NumberColumn(min_value=0.0, step=0.01, format="R$ %.2f"),
        },
    )

    include_zero_qty = st.checkbox("Incluir ativos com quantidade zero", value=False)
    carteira_manual = edited.copy()

    if not include_zero_qty:
        carteira_manual = carteira_manual[carteira_manual["quantidade"] > 0]

    if st.button("Gerar analise da carteira", type="primary"):
        if carteira_manual.empty:
            st.warning("Informe ao menos um ativo com quantidade maior que zero para gerar a analise.")
        else:
            try:
                render_portfolio_analysis(carteira_manual)
            except Exception as exc:
                st.error(str(exc))

with tab_upload:
    uploaded_file = st.file_uploader("CSV da carteira", type=["csv"])

    st.caption(
        "Colunas obrigatorias: ativo, quantidade, preco_medio, classe. Coluna opcional: data_compra."
    )

    if uploaded_file is not None:
        try:
            raw_data = pd.read_csv(uploaded_file)
            render_portfolio_analysis(raw_data)
        except Exception as exc:
            st.error(str(exc))
