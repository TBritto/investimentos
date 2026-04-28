from __future__ import annotations

import re
from dataclasses import dataclass

from src.ai.prompts import NO_RESULT_MESSAGE, SUMMARY_TERMS


@dataclass
class SearchResult:
    chunk_index: int
    score: int
    text: str


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 120) -> list[str]:
    normalized = re.sub(r"\s+", " ", text).strip()
    if not normalized:
        return []
    if chunk_size <= 0:
        raise ValueError("chunk_size precisa ser maior que zero.")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap precisa ser maior ou igual a zero e menor que chunk_size.")

    chunks = []
    start = 0
    while start < len(normalized):
        end = start + chunk_size
        chunks.append(normalized[start:end].strip())
        if end >= len(normalized):
            break
        start = end - overlap
    return chunks


def search_chunks(chunks: list[str], query: str, limit: int = 5) -> list[SearchResult]:
    terms = _tokenize(query)
    if not terms:
        return []

    results = []
    for index, chunk in enumerate(chunks):
        chunk_terms = _tokenize(chunk)
        score = sum(chunk_terms.count(term) for term in terms)
        if score > 0:
            results.append(SearchResult(chunk_index=index, score=score, text=chunk))

    return sorted(results, key=lambda result: result.score, reverse=True)[:limit]


def summarize_document(chunks: list[str], max_sentences: int = 8) -> tuple[str, list[str]]:
    sentences = _split_sentences(" ".join(chunks))
    selected = []
    for sentence in sentences:
        lower_sentence = _normalize(sentence)
        if any(term in lower_sentence for term in SUMMARY_TERMS):
            selected.append(sentence.strip())
        if len(selected) >= max_sentences:
            break

    if not selected:
        return NO_RESULT_MESSAGE, []

    return " ".join(selected), selected


def answer_from_document(chunks: list[str], query: str, limit: int = 5) -> tuple[str, list[SearchResult]]:
    results = search_chunks(chunks, query, limit=limit)
    if not results:
        return NO_RESULT_MESSAGE, []

    answer = " ".join(result.text for result in results)
    return answer, results


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[\wÀ-ÿ]+", _normalize(text))


def _normalize(text: str) -> str:
    return text.lower()


def _split_sentences(text: str) -> list[str]:
    return [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", text) if sentence.strip()]
