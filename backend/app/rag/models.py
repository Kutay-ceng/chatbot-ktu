from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class RagSource:
    title: str
    url: str | None = None
    source_type: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class RagDocument:
    id: str
    title: str
    text: str
    source: RagSource | None = None
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)


class RagChunk:
    id: str
    document_id: str
    text: str
    start: int
    end: int
    
    chunk_id: str | None = None
    content_hash: str | None = None

    source: RagSource | None = None


@dataclass(frozen=True)
class RagSearchResult:
    query: str
    chunks: list[RagChunk]
    sources: list[RagSource]
    retrieved_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
