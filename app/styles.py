from __future__ import annotations

import html

import streamlit as st


WATCHLIST = [
    ("IBOV", "Brasil", "+0,42%"),
    ("SPY", "EUA", "-0,18%"),
    ("PETR4", "Acoes", "+1,10%"),
    ("VALE3", "Acoes", "-0,33%"),
    ("BOVA11", "ETF", "+0,39%"),
    ("MXRF11", "FII", "+0,05%"),
]

THEMES = {
    "Noite premium": {
        "bg": "#080b0f",
        "bg_2": "#0d1218",
        "panel": "#121a24",
        "panel_2": "#172331",
        "border": "#263545",
        "text": "#e6edf4",
        "muted": "#92a4b5",
        "accent": "#5ee6bd",
        "accent_2": "#ffd166",
        "danger": "#ff6b6b",
        "shadow": "rgba(0, 0, 0, 0.38)",
        "button_text": "#051014",
    },
    "Claro executivo": {
        "bg": "#f4f7fb",
        "bg_2": "#edf2f7",
        "panel": "#ffffff",
        "panel_2": "#f6f9fc",
        "border": "#d8e1ea",
        "text": "#17212b",
        "muted": "#607180",
        "accent": "#007a78",
        "accent_2": "#9a6a00",
        "danger": "#c24141",
        "shadow": "rgba(30, 42, 56, 0.12)",
        "button_text": "#ffffff",
    },
    "Grafite alto contraste": {
        "bg": "#050505",
        "bg_2": "#101010",
        "panel": "#171717",
        "panel_2": "#202020",
        "border": "#3c3c3c",
        "text": "#f5f5f5",
        "muted": "#c0c0c0",
        "accent": "#7cffc4",
        "accent_2": "#ffe66d",
        "danger": "#ff7b7b",
        "shadow": "rgba(0, 0, 0, 0.55)",
        "button_text": "#000000",
    },
}


def apply_terminal_style() -> None:
    theme_name = render_theme_selector()
    theme = THEMES[theme_name]
    st.markdown(_css(theme), unsafe_allow_html=True)
    render_global_shell()


def render_theme_selector() -> str:
    if "ui_theme" not in st.session_state:
        st.session_state["ui_theme"] = "Noite premium"

    selected = st.sidebar.selectbox(
        "Tema",
        list(THEMES),
        index=list(THEMES).index(st.session_state["ui_theme"]),
        key="ui_theme_selector",
    )
    st.session_state["ui_theme"] = selected
    return selected


def render_global_shell() -> None:
    st.sidebar.markdown(
        """
        <div class="brand-block">
            <div class="brand-mark">TI</div>
            <div>
                <div class="brand-title">Terminal</div>
                <div class="brand-subtitle">Investimentos</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("### Watchlist")
    for symbol, group, change in WATCHLIST:
        change_class = "positive" if change.startswith("+") else "negative"
        st.sidebar.markdown(
            f"""
            <div class="watchlist-row">
                <span>
                    <span class="watchlist-symbol">{html.escape(symbol)}</span>
                    <span class="watchlist-meta">{html.escape(group)}</span>
                </span>
                <span class="watchlist-change {change_class}">{html.escape(change)}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.sidebar.markdown("---")
    st.sidebar.text_input("Comando global", placeholder="help | macro selic | quote AAPL")


def render_page_header(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <section class="terminal-header">
            <div>
                <div class="terminal-kicker">Terminal de Investimentos</div>
                <h1>{html.escape(title)}</h1>
                <p>{html.escape(subtitle)}</p>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_feature_grid(features: list[tuple[str, str, str]]) -> None:
    cards = []
    for title, description, meta in features:
        cards.append(
            f"""
            <article class="feature-card">
                <div class="feature-meta">{html.escape(meta)}</div>
                <h3>{html.escape(title)}</h3>
                <p>{html.escape(description)}</p>
            </article>
            """
        )
    st.markdown(f"<div class='feature-grid'>{''.join(cards)}</div>", unsafe_allow_html=True)


def render_badge_row(labels: list[str]) -> None:
    badges = "".join(f"<span class='premium-badge'>{html.escape(label)}</span>" for label in labels)
    st.markdown(f"<div class='badge-row'>{badges}</div>", unsafe_allow_html=True)


def _css(theme: dict[str, str]) -> str:
    return f"""
    <style>
    :root {{
        --bg: {theme["bg"]};
        --bg-2: {theme["bg_2"]};
        --panel: {theme["panel"]};
        --panel-2: {theme["panel_2"]};
        --border: {theme["border"]};
        --text: {theme["text"]};
        --muted: {theme["muted"]};
        --accent: {theme["accent"]};
        --accent-2: {theme["accent_2"]};
        --danger: {theme["danger"]};
        --shadow: {theme["shadow"]};
        --button-text: {theme["button_text"]};
    }}

    .stApp {{
        background:
            radial-gradient(circle at 10% -10%, color-mix(in srgb, var(--accent) 18%, transparent), transparent 34%),
            linear-gradient(135deg, var(--bg), var(--bg-2));
        color: var(--text);
    }}

    .block-container {{
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1280px;
    }}

    [data-testid="stSidebar"] {{
        background: color-mix(in srgb, var(--panel) 82%, var(--bg));
        border-right: 1px solid var(--border);
        box-shadow: 10px 0 28px var(--shadow);
    }}

    [data-testid="stSidebar"] section {{
        padding-top: 1rem;
    }}

    h1, h2, h3, h4, label, .stMarkdown, .stText {{
        color: var(--text);
        letter-spacing: 0;
    }}

    h1 {{
        font-size: 2.45rem;
        line-height: 1.05;
        margin-bottom: 0.4rem;
    }}

    h2 {{
        font-size: 1.32rem;
        margin-top: 1.2rem;
    }}

    p, .stCaption, caption {{
        color: var(--muted);
    }}

    .brand-block {{
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.9rem 0.2rem 1rem;
        border-bottom: 1px solid var(--border);
        margin-bottom: 1rem;
    }}

    .brand-mark {{
        width: 42px;
        height: 42px;
        display: grid;
        place-items: center;
        border-radius: 8px;
        color: var(--button-text);
        background: linear-gradient(135deg, var(--accent), var(--accent-2));
        font-weight: 800;
        box-shadow: 0 12px 30px var(--shadow);
    }}

    .brand-title {{
        color: var(--text);
        font-weight: 800;
        line-height: 1;
    }}

    .brand-subtitle {{
        color: var(--muted);
        font-size: 0.82rem;
    }}

    .terminal-header {{
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        border: 1px solid var(--border);
        border-radius: 8px;
        background: linear-gradient(135deg, color-mix(in srgb, var(--panel) 92%, var(--accent)), var(--panel));
        box-shadow: 0 18px 48px var(--shadow);
        margin-bottom: 1.1rem;
        padding: 1.4rem 1.5rem;
    }}

    .terminal-header p {{
        max-width: 760px;
        margin: 0;
        color: var(--muted);
    }}

    .terminal-kicker {{
        color: var(--accent);
        font-size: 0.74rem;
        font-weight: 800;
        text-transform: uppercase;
        margin-bottom: 0.4rem;
    }}

    [data-testid="stMetric"],
    [data-testid="stDataFrame"],
    .stPlotlyChart,
    div[data-testid="stExpander"],
    div[data-testid="stAlert"] {{
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 8px;
        box-shadow: 0 12px 34px var(--shadow);
    }}

    [data-testid="stMetric"] {{
        padding: 0.95rem 1rem;
    }}

    div[data-testid="stMetricValue"] {{
        color: var(--accent);
        font-size: 1.55rem;
    }}

    .stButton > button {{
        background: linear-gradient(135deg, var(--accent), color-mix(in srgb, var(--accent) 72%, var(--accent-2)));
        color: var(--button-text);
        border: 0;
        border-radius: 6px;
        font-weight: 800;
        min-height: 2.45rem;
        box-shadow: 0 12px 28px var(--shadow);
    }}

    .stButton > button:hover {{
        filter: brightness(1.05);
        border: 0;
    }}

    .stTextInput input,
    .stNumberInput input,
    .stDateInput input,
    .stFileUploader,
    .stSelectbox div[data-baseweb="select"],
    .stMultiSelect div[data-baseweb="select"] {{
        background: var(--panel-2);
        color: var(--text);
        border-color: var(--border);
        border-radius: 6px;
    }}

    .watchlist-row {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid color-mix(in srgb, var(--border) 70%, transparent);
        padding: 0.5rem 0;
        font-size: 0.86rem;
    }}

    .watchlist-symbol {{
        color: var(--text);
        font-weight: 800;
        margin-right: 0.35rem;
    }}

    .watchlist-meta {{
        color: var(--muted);
    }}

    .watchlist-change {{
        font-weight: 800;
        font-size: 0.8rem;
    }}

    .positive {{ color: var(--accent); }}
    .negative {{ color: var(--danger); }}

    .feature-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 0.85rem;
        margin: 1rem 0 1.2rem;
    }}

    .feature-card {{
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 8px;
        box-shadow: 0 14px 36px var(--shadow);
        padding: 1rem;
        min-height: 150px;
    }}

    .feature-card h3 {{
        font-size: 1rem;
        margin: 0.35rem 0;
    }}

    .feature-card p {{
        margin: 0;
        font-size: 0.9rem;
    }}

    .feature-meta {{
        color: var(--accent);
        font-size: 0.72rem;
        font-weight: 800;
        text-transform: uppercase;
    }}

    .badge-row {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
        margin: 0.85rem 0;
    }}

    .premium-badge {{
        border: 1px solid var(--border);
        border-radius: 999px;
        background: var(--panel-2);
        color: var(--text);
        padding: 0.28rem 0.62rem;
        font-size: 0.78rem;
        font-weight: 700;
    }}

    hr {{
        border-color: var(--border);
    }}
    </style>
    """
