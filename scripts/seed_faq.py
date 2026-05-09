import os
from datetime import UTC, datetime

from pymongo import MongoClient, UpdateOne

from backend.app.services.faq_loader import DEFAULT_FAQ_PATH, load_faq

DEFAULT_MONGODB_URI = "mongodb://localhost:27017"
DEFAULT_DATABASE_NAME = "chatbot_ktu"
DEFAULT_COLLECTION_NAME = "faqs"

def seed_faq() -> int:
    """FAQ JSON verisini MongoDB'ye aktarır."""
    mongodb_uri = os.getenv("MONGODB_URI", DEFAULT_MONGODB_URI)
    database_name = os.getenv("MONGODB_DB", DEFAULT_DATABASE_NAME)
    collection_name = os.getenv("MONGODB_FAQ_COLLECTION", DEFAULT_COLLECTION_NAME)

    faq_records = load_faq(DEFAULT_FAQ_PATH)

    client = MongoClient(mongodb_uri)
    collection = client[database_name][collection_name]

    operations = [
        UpdateOne(
            {"question": record["question"]},
            {
                "$set": {
                    "answer": record["answer"],
                    "category": record["category"],
                    "source": record["source"],
                    "is_active": True,
                    "updated_at": datetime.now(UTC),
                },
                "$setOnInsert": {
                    "created_at": datetime.now(UTC),
                },
            },
            upsert=True,
        )
        for record in faq_records
    ]

    if not operations:
        client.close()
        return 0

    result = collection.bulk_write(operations)
    client.close()

    return result.upserted_count + result.modified_count

if __name__ == "__main__":
    changed_count = seed_faq()
    print(f"FAQ seed tamamlandı. Eklenen/güncellenen kayıt sayısı: {changed_count}")
