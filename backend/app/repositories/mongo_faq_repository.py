from datetime import UTC, datetime
from typing import Any

from pymongo.collection import Collection
from pymongo.database import Database


class MongoFaqRepository:
    """FAQ verilerini MongoDB koleksiyonundan okuyan repository."""

    def __init__(
        self,
        database: Database,
        collection_name: str = "faqs",
    ) -> None:
        self._collection: Collection = database[collection_name]

    def get_all(self) -> list[dict[str, Any]]:
        """Aktif FAQ kayıtlarını MongoDB'den döndürür."""

        cursor = self._collection.find(
            {"is_active": True},
            {
                "_id": 0,
                "question": 1,
                "answer": 1,
                "category": 1,
                "source": 1,
                "is_active": 1,
                "created_at": 1,
                "updated_at": 1,
            },
        )

        sonuclar = []
        for entry in cursor:
            temiz_entry = self._normalize_entry(entry)
            sonuclar.append(temiz_entry)

        return sonuclar

    def _normalize_entry(self, entry: dict[str, Any]) -> dict[str, Any]:
        """MongoDB'den gelen FAQ kaydını servis formatına uygun hale getirir."""

        now = datetime.now(UTC)

        return {
            "question": str(entry.get("question", "")).strip(),
            "answer": str(entry.get("answer", "")).strip(),
            "category": str(entry.get("category", "")).strip(),
            "source": str(entry.get("source", "")).strip(),
            "is_active": bool(entry.get("is_active", True)),
            "created_at": entry.get("created_at", now),
            "updated_at": entry.get("updated_at", now),
        }