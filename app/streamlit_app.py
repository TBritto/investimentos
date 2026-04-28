from __future__ import annotations

import streamlit as st

from app.styles import apply_terminal_style, render_badge_row, render_feature_grid, render_page_header


def main() -> None:
    st.set_page_config(page_title="Terminal de Investimentos", layout="wide")
    apply_terminal_style()
    render_page_header(
        "Terminal de Investimentos",
        "MVP em portugues do Brasil para dados, analytics, carteira, macro e documentos.",
    )

    render_badge_row(
        [
            "Dados publicos",
            "Sem recomendacao automatica",
            "OpenBB opcional",
            "Testes automatizados",
        ]
    )

    st.warning(
        "Ferramenta de apoio a decisao. Nao e recomendacao de compra, venda ou manutencao de ativos."
    )

    col_terminal, col_macro, col_docs = st.columns(3)
    col_terminal.metric("Terminal", "Comandos")
    col_macro.metric("Macro", "BCB SGS")
    col_docs.metric("Testes", "46 passed")

    render_feature_grid(
        [
            (
                "Terminal de comandos",
                "Execute consultas macro, mercado e rotinas analiticas em uma interface compacta.",
                "Operacao",
            ),
            (
                "Carteira CSV",
                "Importe ativos, classes e preco medio para visualizar composicao e concentracao.",
                "Portfolio",
            ),
            (
                "Macro Brasil",
                "Acompanhe Selic, IPCA e dolar a partir de series publicas do Banco Central.",
                "Dados",
            ),
            (
                "Renda Fixa",
                "Simule prefixado, IPCA+ e CDI com marcacao a mercado simplificada.",
                "Analytics",
            ),
            (
                "Relatorios IA",
                "Analise documentos locais com busca por termos e resumo heuristico rastreavel.",
                "Documentos",
            ),
            (
                "Acoes e FIIs",
                "Espaco preparado para evoluir consultas de mercado e comparativos de ativos.",
                "Mercado",
            ),
        ]
    )

    st.info("Use o menu lateral para navegar pelas paginas do MVP.")


if __name__ == "__main__":
    main()
