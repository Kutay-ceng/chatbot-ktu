from __future__ import annotations

from abc import ABC, abstractmethod

from .models import RagChunk, RagDocument


class Chunker(ABC):
    """Soyut belge parçalama arayüzü."""

    @abstractmethod
    def chunk(self, document: RagDocument) -> list[RagChunk]:
        raise NotImplementedError


class SimpleChunker(Chunker):
    """Karakter tabanlı, çakışmalı basit chunker."""

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")
        if overlap < 0:
            raise ValueError("overlap cannot be negative")

        self.chunk_size = chunk_size
        self.overlap = min(overlap, chunk_size - 1)

    def chunk(self, document: RagDocument) -> list[RagChunk]:
        text = document.text.strip()
        if not text:
            return []

        chunks: list[RagChunk] = []
        step = max(1, self.chunk_size - self.overlap)
        index = 0
        chunk_index = 0

        while index < len(text):
            end_index = min(index + self.chunk_size, len(text))
            chunk_text = text[index:end_index].strip()
            if not chunk_text:
                break

            chunks.append(
                RagChunk(
                    id=f"{document.id}-{chunk_index}",
                    document_id=document.id,
                    text=chunk_text,
                    start=index,
                    end=end_index,
                    source=document.source,
                    metadata={"title": document.title},
                )
            )
            chunk_index += 1
            index += step

        return chunks
