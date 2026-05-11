from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from .models import RagChunk


class VectorStore(ABC):
    """Soyut vektör deposu arayüzü."""

    @abstractmethod
    def add_chunks(self, chunks: Iterable[RagChunk]) -> None:
        raise NotImplementedError

    @abstractmethod
    def search(self, query: str, top_k: int = 3) -> list[RagChunk]:
        raise NotImplementedError


class InMemoryVectorStore(VectorStore):
    """Gerçek vektör arama yerine basit kelime benzerliği kullanan in-memory depolama."""

    def __init__(self) -> None:
        self._chunks: list[RagChunk] = []

    def add_chunks(self, chunks: Iterable[RagChunk]) -> None:
        self._chunks.extend(chunks)

    def search(self, query: str, top_k: int = 3) -> list[RagChunk]:
        if not query or top_k <= 0:
            return []

        query_tokens = {token.lower() for token in query.split() if token}
        scored_chunks: list[tuple[int, int, RagChunk]] = []

        for index, chunk in enumerate(self._chunks):
            chunk_tokens = {token.lower() for token in chunk.text.split() if token}
            score = len(query_tokens.intersection(chunk_tokens))
            if score > 0:
                scored_chunks.append((score, index, chunk))

        scored_chunks.sort(key=lambda item: (item[0], -item[1]), reverse=True)
        return [chunk for _, _, chunk in scored_chunks[:top_k]]
