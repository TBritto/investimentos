from io import BytesIO

import pytest

from src.ai.document_loader import DocumentLoaderError, load_document
from src.ai.prompts import NO_RESULT_MESSAGE
from src.ai.rag import answer_from_document, chunk_text, search_chunks, summarize_document


def test_load_text_document_decodes_utf8() -> None:
    document = load_document(BytesIO("Receita e margem cresceram.".encode("utf-8")), "relatorio.txt")

    assert document.filename == "relatorio.txt"
    assert "Receita" in document.text


def test_load_document_rejects_unknown_extension() -> None:
    with pytest.raises(DocumentLoaderError, match="Formato nao suportado"):
        load_document(BytesIO(b"abc"), "relatorio.csv")


def test_chunk_text_uses_overlap() -> None:
    chunks = chunk_text("abcdefghij", chunk_size=6, overlap=2)

    assert chunks == ["abcdef", "efghij"]


def test_search_chunks_returns_relevant_matches() -> None:
    chunks = ["receita cresceu e caixa subiu", "sem informacao relevante"]

    results = search_chunks(chunks, "receita caixa")

    assert len(results) == 1
    assert results[0].chunk_index == 0
    assert results[0].score == 2


def test_summarize_document_uses_financial_terms_and_evidence() -> None:
    chunks = ["A receita subiu. O clima estava bom. A divida caiu e caixa aumentou."]

    summary, evidence = summarize_document(chunks)

    assert "receita" in summary.lower()
    assert len(evidence) == 2


def test_answer_from_document_is_clear_when_no_match() -> None:
    answer, evidence = answer_from_document(["Receita subiu."], "capex")

    assert answer == NO_RESULT_MESSAGE
    assert evidence == []
