import streamlit as st

from src.commands.macro import execute_macro_command


st.title("Terminal")
st.caption("Execute comandos iniciais do MVP.")

command = st.text_input("Comando", value="macro selic")
start_date = st.text_input("Data inicial", placeholder="YYYY-MM-DD")
end_date = st.text_input("Data final", placeholder="YYYY-MM-DD")

if st.button("Executar"):
    try:
        result = execute_macro_command(
            command,
            start_date=start_date or None,
            end_date=end_date or None,
        )
    except Exception as exc:
        st.error(str(exc))
    else:
        st.subheader(result.title)
        st.dataframe(result.data, use_container_width=True)
        if not result.data.empty:
            st.line_chart(result.data.set_index("date")["value"])
