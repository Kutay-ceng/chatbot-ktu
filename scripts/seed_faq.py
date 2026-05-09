import os
from datetime import UTC, datetime

from pymongo import MongoClient, UpdateOne

from backend.app.db.config import MongoSettings
from backend.app.services.faq_loader import DEFAULT_FAQ_PATH, load_faq

DEFAULT_COLLECTION_NAME = "faqs"

def _faq_collection_name() -> str:
    collection_name = os.getenv("MONGODB_FAQ_COLLECTION", DEFAULT_COLLECTION_NAME)
    return collection_name.strip() or DEFAULT_COLLECTION_NAME

def seed_faq() -> int:
    """FAQ JSON verisini MongoDB'ye aktarır."""

    faq_records = load_faq(DEFAULT_FAQ_PATH)

    operations = []
    for record in faq_records:
        now = datetime.now(UTC)

        operations.append(
            UpdateOne(
                {"question": record["question"]},
                {
                    "$set": {
                        "answer": record["answer"],
                        "category": record["category"],
                        "source": record["source"],
                        "is_active": True,
                        "updated_at": now,
                    },
                    "$setOnInsert": {
                        "created_at": now,
                    },
                },
                upsert=True,
            )
        )
    if not operations:
        return 0

    settings = MongoSettings.from_env()
    client = MongoClient(
        settings.require_uri(),
        connectTimeoutMS=settings.connect_timeout_ms,
        serverSelectionTimeoutMS=settings.server_selection_timeout_ms,
    )
    try:
        collection = client[settings.database_name][_faq_collection_name()]
        result = collection.bulk_write(operations)
        return result.upserted_count + result.modified_count
    finally:
        client.close()

if __name__ == "__main__":
    changed_count = seed_faq()
    print(f"FAQ seed tamamlandı. Eklenen/güncellenen kayıt sayısı: {changed_count}")
