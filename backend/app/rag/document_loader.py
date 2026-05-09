from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .models import RagDocument, RagSource


class DocumentLoader(ABC):
    """Soyut belge yükleyici arayüzü."""

    @abstractmethod
    def load(self) -> list[RagDocument]:
        raise NotImplementedError


class SimpleDocumentLoader(DocumentLoader):
    """Basit belge listesini RagDocument nesnelerine çevirir."""

    def __init__(self, entries: list[dict[str, Any]]) -> None:
        self._entries = entries

    def load(self) -> list[RagDocument]:
        documents: list[RagDocument] = []

        for index, entry in enumerate(self._entries, start=1):
            document_id = str(entry.get("id", index))
            title = str(entry.get("title", "")).strip()
            text = str(entry.get("text", "")).strip()
            source_data = entry.get("source") or {}
            source = None

            if isinstance(source_data, dict):
                source = RagSource(
                    title=str(source_data.get("title", "")).strip(),
                    url=str(source_data.get("url", "")).strip() or None,
                    source_type=str(source_data.get("type", "")).strip() or None,
                    metadata=source_data.get("metadata"),
                )

            if text:
                documents.append(
                    RagDocument(
                        id=document_id,
                        title=title or f"document-{document_id}",
                        text=text,
                        source=source,
                        metadata=entry.get("metadata"),
                    )
                )

        return documents
