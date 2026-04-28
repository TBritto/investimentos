from __future__ import annotations

import streamlit as st

from app.styles import apply_terminal_style, render_page_header


def main() -> None:
    st.set_page_config(page_title="Terminal de Investimentos", layout="wide")
    apply_terminal_style()
    render_page_header(
        "Terminal de Investimentos",
        "MVP em portugues do Brasil para dados, analytics, carteira, macro e documentos.",
    )

    st.warning(
        "Ferramenta de apoio a decisao. Nao e recomendacao de compra, venda ou manutencao de ativos."
    )

    col_terminal, col_macro, col_docs = st.columns(3)
    col_terminal.metric("Terminal", "Comandos")
    col_macro.metric("Macro", "BCB SGS")
    col_docs.metric("Testes", "46 passed")

    st.subheader("Modulos disponiveis")
    st.write(
        "- Terminal de comandos\n"
        "- Carteira CSV\n"
        "- Dashboard macroeconomico\n"
        "- Simulador de renda fixa\n"
        "- Acoes e FIIs\n"
        "- Relatorios IA locais"
    )

    st.info("Use o menu lateral para navegar pelas paginas do MVP.")


if __name__ == "__main__":
    main()
