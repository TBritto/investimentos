import streamlit as st

from app.styles import apply_terminal_style, render_page_header
from src.ai.document_loader import DocumentLoaderError, load_document
from src.ai.prompts import FUTURE_OPENAI_ENV_VAR
from src.ai.rag import answer_from_document, chunk_text, summarize_document


apply_terminal_style()
render_page_header("Relatorios IA", "Analise local de documentos financeiros, sem API externa.")

st.info(
    f"Esta versao usa busca e resumo heuristico local. Futuramente pode usar LLM via `{FUTURE_OPENAI_ENV_VAR}`, "
    "mas nenhuma chave e exigida agora."
)

uploaded_file = st.file_uploader("Documento financeiro", type=["pdf", "txt", "md", "markdown"])

if uploaded_file is not None:
    try:
        document = load_document(uploaded_file, uploaded_file.name)
        chunks = chunk_text(document.text)
    except DocumentLoaderError as exc:
        st.error(str(exc))
    else:
        st.success(f"Documento carregado: {document.filename}")
        st.metric("Chunks", len(chunks))

        summary, summary_evidence = summarize_document(chunks)
        st.subheader("Resumo heuristico")
        st.write(summary)

        if summary_evidence:
            with st.expander("Trechos usados no resumo"):
                for evidence in summary_evidence:
                    st.write(evidence)

        query = st.text_input("Buscar termo ou pergunta", placeholder="Ex.: margem, risco, dividendos")
        if query:
            answer, results = answer_from_document(chunks, query)
            st.subheader("Resposta baseada no documento")
            st.write(answer)

            if results:
                st.subheader("Trechos relevantes")
                for result in results:
                    with st.expander(f"Trecho {result.chunk_index + 1} | score {result.score}"):
                        st.write(result.text)
