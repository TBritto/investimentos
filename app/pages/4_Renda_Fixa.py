import streamlit as st

from app.styles import apply_terminal_style, render_page_header
from src.analytics.fixed_income import simulate_fixed_income


apply_terminal_style()
render_page_header("Renda Fixa", "Simulador educacional com marcacao a mercado simplificada.")

st.warning(
    "Esta e uma simulacao aproximada para fins educacionais. "
    "Nao use como recomendacao de compra, venda ou manutencao."
)

indexer = st.selectbox("Indexador", ["prefixado", "IPCA+", "percentual CDI"])
invested_amount = st.number_input("Valor investido", min_value=0.0, value=10000.0, step=500.0)
contracted_annual_rate_pct = st.number_input("Taxa contratada anual (%)", value=10.0, step=0.1)
current_annual_rate_pct = st.number_input("Taxa atual anual (%)", value=11.0, step=0.1)
years_to_maturity = st.number_input("Anos ate vencimento", min_value=0.1, value=3.0, step=0.5)
income_tax_rate_pct = st.number_input("Aliquota IR opcional (%)", min_value=0.0, max_value=100.0, value=15.0)

expected_ipca_pct = 0.0
expected_cdi_pct = 0.0
if indexer == "IPCA+":
    expected_ipca_pct = st.number_input("IPCA anual esperado (%)", value=4.0, step=0.1)
elif indexer == "percentual CDI":
    expected_cdi_pct = st.number_input("CDI anual esperado (%)", value=10.5, step=0.1)
    st.caption("Para CDI, informe a taxa contratada como percentual do CDI. Ex.: 100 para 100% do CDI.")

if st.button("Simular"):
    try:
        result = simulate_fixed_income(
            invested_amount=invested_amount,
            contracted_annual_rate=contracted_annual_rate_pct / 100,
            current_annual_rate=current_annual_rate_pct / 100,
            years_to_maturity=years_to_maturity,
            indexer=indexer,
            income_tax_rate=income_tax_rate_pct / 100,
            expected_ipca_annual_rate=expected_ipca_pct / 100,
            expected_cdi_annual_rate=expected_cdi_pct / 100,
        )
    except Exception as exc:
        st.error(str(exc))
    else:
        gross_col, net_col, price_col, impact_col = st.columns(4)
        gross_col.metric("Valor bruto estimado", f"R$ {result.gross_value:,.2f}")
        net_col.metric("Valor liquido estimado", f"R$ {result.net_value:,.2f}")
        price_col.metric("Preco estimado hoje", f"R$ {result.estimated_price_today:,.2f}")
        impact_col.metric("Impacto da taxa", f"R$ {result.rate_change_impact:,.2f}")

        st.subheader("Observacoes")
        for note in result.educational_notes:
            st.write(f"- {note}")
