import streamlit as st

from app.styles import apply_terminal_style, render_page_header
from src.terminal.registry import execute_command


apply_terminal_style()
render_page_header("Terminal", "Comandos reconhecidos, historico de sessao e respostas compactas.")

if "terminal_history" not in st.session_state:
    st.session_state["terminal_history"] = []

command = st.text_input("Comando", value="help", key="terminal_command_input")

if st.button("Executar"):
    try:
        result = execute_command(command)
    except Exception as exc:
        st.error(str(exc))
    else:
        st.session_state["terminal_history"].insert(0, {"raw": command, "result": result})

for item in st.session_state["terminal_history"]:
    result = item["result"]
    with st.container():
        st.markdown(f"**> {item['raw']}**")
        st.subheader(result.title)
        if result.message:
            st.write(result.message)
        if result.dataframe is not None:
            st.dataframe(result.dataframe, use_container_width=True)
        if result.chart is not None:
            st.plotly_chart(result.chart, use_container_width=True)
        st.markdown("---")
