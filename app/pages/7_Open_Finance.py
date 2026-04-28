import pandas as pd
import streamlit as st

from app.styles import apply_terminal_style, render_page_header
from src.data.pluggy import (
    create_connect_token,
    get_accounts,
    get_connect_widget_url,
    get_items,
    get_transactions,
    is_configured,
)


apply_terminal_style()
render_page_header(
    "Open Finance",
    "Conecte contas bancarias reais via consentimento seguro, sem guardar senha de banco no app.",
)

st.warning(
    "Open Finance exige consentimento do usuario. Este app usa token de curta duracao para o widget "
    "Pluggy e nunca deve receber senha de internet banking."
)

configured = is_configured()
status_col, flow_col, scope_col = st.columns(3)
status_col.metric("Configuracao", "Pronta" if configured else "Pendente")
flow_col.metric("Fluxo", "Consentimento")
scope_col.metric("Escopo", "Contas e transacoes")

with st.expander("Checklist de producao", expanded=not configured):
    st.write("- Configure `PLUGGY_CLIENT_ID` e `PLUGGY_CLIENT_SECRET` no `.env`.")
    st.write("- Gere um connect token para abrir o Pluggy Connect Widget.")
    st.write("- O usuario conclui o consentimento no widget.")
    st.write("- Depois consulte conexoes, contas e transacoes recuperadas pela Pluggy.")
    st.write("- Nunca colete nem armazene senha de banco neste aplicativo.")

st.subheader("1. Gerar token de conexao")
token_col, options_col = st.columns([1, 1])
with options_col:
    client_user_id = st.text_input("Identificador interno opcional", placeholder="usuario-123")
    oauth_redirect_url = st.text_input("OAuth redirect URL opcional", placeholder="https://seu-app/callback")
    webhook_url = st.text_input("Webhook URL opcional", placeholder="https://seu-app/webhook")

with token_col:
    if st.button("Gerar connect token"):
        try:
            token = create_connect_token(
                client_user_id=client_user_id or None,
                oauth_redirect_url=oauth_redirect_url or None,
                webhook_url=webhook_url or None,
            )
        except Exception as exc:
            st.error(str(exc))
        else:
            st.session_state["pluggy_connect_token"] = token
            st.success("Connect token gerado com sucesso.")

    token = st.session_state.get("pluggy_connect_token")
    if token:
        widget_url = get_connect_widget_url(token)
        st.code(token)
        st.link_button("Abrir Pluggy Connect", widget_url)
        st.caption("O token e temporario. Gere um novo token para uma nova conexao.")

st.subheader("2. Conexoes e contas")
items_col, accounts_col = st.columns([1, 1])
with items_col:
    if st.button("Carregar conexoes"):
        try:
            st.session_state["pluggy_items"] = get_items()
        except Exception as exc:
            st.error(str(exc))

    items = st.session_state.get("pluggy_items")
    if isinstance(items, pd.DataFrame) and not items.empty:
        st.dataframe(items, use_container_width=True)
    else:
        st.info("Nenhuma conexao carregada ainda.")

with accounts_col:
    item_id = st.text_input("Filtrar contas por item_id opcional")
    if st.button("Carregar contas"):
        try:
            st.session_state["pluggy_accounts"] = get_accounts(item_id=item_id or None)
        except Exception as exc:
            st.error(str(exc))

    accounts = st.session_state.get("pluggy_accounts")
    if isinstance(accounts, pd.DataFrame) and not accounts.empty:
        st.dataframe(accounts, use_container_width=True)
    else:
        st.info("Nenhuma conta carregada ainda.")

st.subheader("3. Transacoes")
tx_col, filter_col = st.columns([1, 1])
with filter_col:
    account_id = st.text_input("account_id")
    from_date = st.text_input("Data inicial opcional", placeholder="YYYY-MM-DD")
    to_date = st.text_input("Data final opcional", placeholder="YYYY-MM-DD")

with tx_col:
    if st.button("Carregar transacoes"):
        try:
            transactions = get_transactions(
                account_id=account_id,
                from_date=from_date or None,
                to_date=to_date or None,
            )
            st.session_state["pluggy_transactions"] = transactions
        except Exception as exc:
            st.error(str(exc))

    transactions = st.session_state.get("pluggy_transactions")
    if isinstance(transactions, pd.DataFrame) and not transactions.empty:
        total = float(transactions["amount"].sum()) if "amount" in transactions else 0.0
        st.metric("Total no periodo", f"R$ {total:,.2f}")
        st.dataframe(transactions, use_container_width=True)
    else:
        st.info("Informe uma conta conectada para carregar transacoes.")
