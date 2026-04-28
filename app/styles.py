from __future__ import annotations

import streamlit as st


WATCHLIST = [
    ("IBOV", "Brasil"),
    ("SPY", "EUA"),
    ("PETR4", "Acoes"),
    ("VALE3", "Acoes"),
    ("BOVA11", "ETF"),
    ("MXRF11", "FII"),
]


def apply_terminal_style() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg: #080d12;
            --panel: #101821;
            --panel-2: #14202b;
            --border: #263746;
            --text: #d7e0e8;
            --muted: #8da1b3;
            --accent: #43d9ad;
            --accent-2: #f2c94c;
            --danger: #ff6b6b;
        }

        .stApp {
            background: var(--bg);
            color: var(--text);
        }

        [data-testid="stSidebar"] {
            background: #0b1219;
            border-right: 1px solid var(--border);
        }

        h1, h2, h3 {
            letter-spacing: 0;
            color: var(--text);
        }

        .stCaption, caption, p {
            color: var(--muted);
        }

        [data-testid="stMetric"],
        [data-testid="stDataFrame"],
        .stPlotlyChart,
        div[data-testid="stExpander"] {
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 10px;
        }

        div[data-testid="stMetricValue"] {
            color: var(--accent);
            font-size: 1.4rem;
        }

        .stButton > button {
            background: var(--accent);
            color: #061014;
            border: 0;
            border-radius: 4px;
            font-weight: 700;
        }

        .stTextInput input,
        .stNumberInput input,
        .stSelectbox div[data-baseweb="select"] {
            background: var(--panel-2);
            color: var(--text);
            border-color: var(--border);
        }

        .terminal-header {
            border-bottom: 1px solid var(--border);
            margin-bottom: 14px;
            padding-bottom: 10px;
        }

        .terminal-kicker {
            color: var(--accent);
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
        }

        .watchlist-row {
            display: flex;
            justify-content: space-between;
            border-bottom: 1px solid #1b2a36;
            padding: 6px 0;
            font-size: 0.86rem;
        }

        .watchlist-symbol {
            color: var(--text);
            font-weight: 700;
        }

        .watchlist-meta {
            color: var(--muted);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    render_global_shell()


def render_global_shell() -> None:
    st.sidebar.markdown("### Watchlist")
    for symbol, group in WATCHLIST:
        st.sidebar.markdown(
            f"""
            <div class="watchlist-row">
                <span class="watchlist-symbol">{symbol}</span>
                <span class="watchlist-meta">{group}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.sidebar.markdown("---")
    st.sidebar.text_input("Comando global", placeholder="help | macro selic | quote AAPL")


def render_page_header(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="terminal-header">
            <div class="terminal-kicker">Terminal de Investimentos</div>
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
