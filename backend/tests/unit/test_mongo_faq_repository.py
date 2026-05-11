from datetime import UTC, datetime
from typing import Any

from backend.app.repositories.mongo_faq_repository import MongoFaqRepository


class FakeCollection:
    def __init__(self, entries: list[dict[str, Any]]) -> None:
        self.entries = entries
        self.last_filter: dict[str, Any] | None = None
        self.last_projection: dict[str, int] | None = None

    def find(
        self,
        query: dict[str, Any],
        projection: dict[str, int],
    ) -> list[dict[str, Any]]:
        self.last_filter = query
        self.last_projection = projection

        return [
            entry
            for entry in self.entries
            if entry.get("is_active") is True
        ]

class FakeDatabase:
    def __init__(self, collection: FakeCollection) -> None:
        self.collection = collection
        self.last_collection_name: str | None = None

    def __getitem__(self, collection_name: str) -> FakeCollection:
        self.last_collection_name = collection_name
        return self.collection

def test_mongo_faq_repository_get_all_reads_active_entries() -> None:
    now = datetime(2026, 1, 1, tzinfo=UTC)

    entries = [
        {
            "question": "Bölüm başkanı kim?",
            "answer": "Bölüm başkanı bilgisi web sitesinde yer alır.",
            "category": "Akademik Kadro",
            "source": "https://example.edu/aktif",
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        },
        {
            "question": "Pasif soru",
            "answer": "Bu cevap dönmemeli.",
            "category": "Pasif",
            "source": "https://example.edu/pasif",
            "is_active": False,
            "created_at": now,
            "updated_at": now,
        },
    ]

    collection = FakeCollection(entries)
    database = FakeDatabase(collection)

    repository = MongoFaqRepository(database)

    result = repository.get_all()

    assert database.last_collection_name == "faqs"
    assert collection.last_filter == {"is_active": True}
    assert collection.last_projection == {
        "_id": 0,
        "question": 1,
        "answer": 1,
        "category": 1,
        "source": 1,
        "is_active": 1,
        "created_at": 1,
        "updated_at": 1,
    }
    assert result == [
        {
            "question": "Bölüm başkanı kim?",
            "answer": "Bölüm başkanı bilgisi web sitesinde yer alır.",
            "category": "Akademik Kadro",
            "source": "https://example.edu/aktif",
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        }
    ]
