from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO


class DocumentLoaderError(RuntimeError):
    """Erro amigavel para arquivos de documentos financeiros."""


@dataclass
class LoadedDocument:
    filename: str
    text: str


def load_document(file: BinaryIO, filename: str) -> LoadedDocument:
    suffix = Path(filename).suffix.lower()
    raw_bytes = file.read()
    if suffix in {".txt", ".md", ".markdown"}:
        return LoadedDocument(filename=filename, text=_decode_text(raw_bytes))
    if suffix == ".pdf":
        return LoadedDocument(filename=filename, text=_extract_pdf_text(raw_bytes))

    raise DocumentLoaderError("Formato nao suportado. Envie PDF, TXT ou Markdown.")


def _decode_text(raw_bytes: bytes) -> str:
    for encoding in ("utf-8", "latin-1"):
        try:
            return raw_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise DocumentLoaderError("Nao foi possivel decodificar o arquivo de texto.")


def _extract_pdf_text(raw_bytes: bytes) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise DocumentLoaderError(
            "Leitura de PDF requer a dependencia opcional pypdf. "
            "Instale pypdf ou envie TXT/Markdown."
        ) from exc

    try:
        reader = PdfReader(raw_bytes)
        pages = [page.extract_text() or "" for page in reader.pages]
    except Exception as exc:
        raise DocumentLoaderError("Nao foi possivel extrair texto do PDF.") from exc

    text = "\n".join(pages).strip()
    if not text:
        raise DocumentLoaderError("PDF sem texto extraivel.")
    return text
