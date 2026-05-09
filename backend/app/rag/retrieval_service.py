from __future__ import annotations

from typing import Iterable

from .chunker import Chunker, SimpleChunker
from .models import RagDocument, RagSearchResult, RagSource
from .vector_store import VectorStore


class RetrievalService:
    """RAG belge arama ve geri getirme hizmeti."""

    def __init__(self, vector_store: VectorStore, chunker: Chunker | None = None) -> None:
        self._vector_store = vector_store
        self._chunker = chunker or SimpleChunker()

    def index_documents(self, documents: Iterable[RagDocument]) -> None:
        chunks = []
        for document in documents:
            chunks.extend(self._chunker.chunk(document))
        self._vector_store.add_chunks(chunks)

    def retrieve(self, query: str, top_k: int = 3) -> RagSearchResult:
        chunks = self._vector_store.search(query, top_k=top_k)

        sources: list[RagSource] = []
        seen_source_keys: set[tuple[str, str | None, str | None]] = set()

        for chunk in chunks:
            if chunk.source is None:
                continue

            key = (chunk.source.title, chunk.source.url, chunk.source.source_type)
            if key not in seen_source_keys:
                seen_source_keys.add(key)
                sources.append(chunk.source)

        return RagSearchResult(query=query, chunks=chunks, sources=sources)
