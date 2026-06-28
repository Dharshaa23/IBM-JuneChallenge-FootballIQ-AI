"""
rag.py
-------
Retrieval-Augmented Generation layer over the football knowledge base
(FIFA Laws of the Game, glossary, tournament rules).

Pipeline:
    1. Docling parses source documents (PDF/DOCX/MD/HTML) in `docs/` into
       clean text, regardless of original format.
    2. The text is chunked and embedded.
    3. FAISS indexes the embeddings for fast similarity search.
    4. `retrieve_rules_context()` returns the most relevant chunks for a
       given user question, to be inserted into the Granite prompt.

If `docling`, `langchain`, `faiss-cpu`, or an embeddings backend are not
installed/available, this module falls back to simple keyword search over
the same source documents so the Ask FootballIQ feature still works without
any extra dependencies installed.
"""

from __future__ import annotations

import os
import re
from functools import lru_cache
from typing import Optional

DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs")


# --------------------------------------------------------------------------- #
# Document ingestion (Docling, with graceful fallback to plain text reading)
# --------------------------------------------------------------------------- #
def _load_documents_with_docling() -> list[str]:
    """
    Use Docling to parse every supported document in docs/ into plain text
    chunks. Docling handles PDF, DOCX, HTML, images, and more transparently.
    """
    from docling.document_converter import DocumentConverter  # lazy import

    converter = DocumentConverter()
    texts = []
    for fname in os.listdir(DOCS_DIR):
        path = os.path.join(DOCS_DIR, fname)
        if not os.path.isfile(path):
            continue
        try:
            result = converter.convert(path)
            texts.append(result.document.export_to_markdown())
        except Exception as exc:  # noqa: BLE001
            print(f"[rag.py] Docling failed on {fname}, skipping: {exc}")
    return texts


def _load_documents_plain() -> list[str]:
    """Fallback: read every text-like file in docs/ directly (no Docling)."""
    texts = []
    for fname in os.listdir(DOCS_DIR):
        path = os.path.join(DOCS_DIR, fname)
        if not os.path.isfile(path):
            continue
        if fname.lower().endswith((".md", ".txt")):
            with open(path, "r", encoding="utf-8") as f:
                texts.append(f.read())
        # PDFs/DOCX without Docling installed are simply skipped here --
        # install `docling` to enable full ingestion of those formats.
    return texts


def _chunk_text(text: str, chunk_size: int = 600, overlap: int = 100) -> list[str]:
    """Simple sliding-window chunking by characters, splitting on paragraph breaks where possible."""
    paragraphs = re.split(r"\n\s*\n", text)
    chunks, current = [], ""
    for para in paragraphs:
        if len(current) + len(para) <= chunk_size:
            current += para + "\n\n"
        else:
            if current.strip():
                chunks.append(current.strip())
            current = para + "\n\n"
    if current.strip():
        chunks.append(current.strip())
    return chunks


@lru_cache(maxsize=1)
def _get_all_chunks() -> tuple[str, ...]:
    """Load and chunk all knowledge base documents (Docling first, plain text fallback)."""
    try:
        docs = _load_documents_with_docling()
        if not docs:
            docs = _load_documents_plain()
    except Exception:
        docs = _load_documents_plain()

    chunks = []
    for doc in docs:
        chunks.extend(_chunk_text(doc))
    return tuple(chunks)


# --------------------------------------------------------------------------- #
# Vector index (FAISS, with graceful fallback to keyword search)
# --------------------------------------------------------------------------- #
class _FaissIndex:
    """Lazily-built FAISS index over the knowledge base chunks."""

    def __init__(self):
        self.index = None
        self.chunks: list[str] = []
        self.embeddings = None

    def build(self):
        chunks = list(_get_all_chunks())
        if not chunks:
            return

        try:
            import faiss
            import numpy as np
            from langchain_community.embeddings import HuggingFaceEmbeddings

            embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            vectors = np.array(embedder.embed_documents(chunks)).astype("float32")
            dim = vectors.shape[1]
            index = faiss.IndexFlatL2(dim)
            index.add(vectors)

            self.index = index
            self.chunks = chunks
            self.embeddings = embedder
        except Exception as exc:  # noqa: BLE001
            print(f"[rag.py] FAISS/embeddings unavailable, using keyword search fallback: {exc}")
            self.index = None
            self.chunks = chunks

    def search(self, query: str, k: int = 3) -> list[str]:
        if self.index is not None and self.embeddings is not None:
            import numpy as np

            query_vec = np.array([self.embeddings.embed_query(query)]).astype("float32")
            _, indices = self.index.search(query_vec, k)
            return [self.chunks[i] for i in indices[0] if 0 <= i < len(self.chunks)]

        # Keyword fallback: rank chunks by overlapping word count with the query.
        query_words = set(re.findall(r"[a-zA-Z']+", query.lower()))
        scored = []
        for chunk in self.chunks:
            chunk_words = set(re.findall(r"[a-zA-Z']+", chunk.lower()))
            overlap = len(query_words & chunk_words)
            if overlap > 0:
                scored.append((overlap, chunk))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [c for _, c in scored[:k]]


_faiss_index: Optional[_FaissIndex] = None


def _get_index() -> _FaissIndex:
    global _faiss_index
    if _faiss_index is None:
        _faiss_index = _FaissIndex()
        _faiss_index.build()
    return _faiss_index


def retrieve_rules_context(query: str, k: int = 3) -> str:
    """
    Retrieve the top-k most relevant knowledge base chunks for a query and
    return them concatenated as a single context string for the prompt.
    """
    index = _get_index()
    results = index.search(query, k=k)
    if not results:
        return ""
    return "\n\n---\n\n".join(results)
