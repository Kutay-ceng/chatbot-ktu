from typing import Any

import scripts.seed_faq as seed_module


class FakeBulkWriteResult:
    def __init__(self, upserted_count: int, modified_count: int) -> None:
        self.upserted_count = upserted_count
        self.modified_count = modified_count

class FakeCollection:
    def __init__(self) -> None:
        self.operations: list[Any] = []

    def bulk_write(self, operations: list[Any]) -> FakeBulkWriteResult:
        self.operations = operations
        return FakeBulkWriteResult(upserted_count=1, modified_count=1)

class FakeDatabase:
    def __init__(self, collection: FakeCollection) -> None:
        self.collection = collection
        self.used_collection_name: str | None = None

    def __getitem__(self, collection_name: str) -> FakeCollection:
        self.used_collection_name = collection_name
        return self.collection

class FakeMongoClient:
    def __init__(self, uri: str, **kwargs: Any) -> None:
        self.uri = uri
        self.connect_timeout_ms = kwargs["connectTimeoutMS"]
        self.server_selection_timeout_ms = kwargs["serverSelectionTimeoutMS"]
        self.collection = FakeCollection()
        self.database = FakeDatabase(self.collection)
        self.used_database_name: str | None = None
        self.closed = False

    def __getitem__(self, database_name: str) -> FakeDatabase:
        self.used_database_name = database_name
        return self.database

    def close(self) -> None:
        self.closed = True

def test_seed_faq_writes_json_records_to_mongodb(monkeypatch: Any) -> None:
    created_clients: list[FakeMongoClient] = []

    def fake_mongo_client(uri: str, **kwargs: Any) -> FakeMongoClient:
        client = FakeMongoClient(uri, **kwargs)
        created_clients.append(client)
        return client

    def fake_load_faq(path: object) -> list[dict[str, str]]:
        return [
            {
                "question": "Bölüm başkanı kim?",
                "answer": "Bölüm başkanı bilgisi web sitesinde yer alır.",
                "category": "Akademik Kadro",
                "source": "https://example.edu",
            }
        ]

    monkeypatch.setattr(seed_module, "MongoClient", fake_mongo_client)
    monkeypatch.setattr(seed_module, "load_faq", fake_load_faq)

    monkeypatch.setenv("MONGODB_URI", "mongodb://test-host:27017")
    monkeypatch.setenv("MONGODB_DB", "test_db")
    monkeypatch.setenv("MONGODB_FAQ_COLLECTION", "test_faqs")
    monkeypatch.setenv("MONGODB_CONNECT_TIMEOUT_MS", "5000")
    monkeypatch.setenv("MONGODB_SERVER_SELECTION_TIMEOUT_MS", "5000")

    changed_count = seed_module.seed_faq()

    assert changed_count == 2

    client = created_clients[0]
    assert client.uri == "mongodb://test-host:27017"
    assert client.connect_timeout_ms == 5000
    assert client.server_selection_timeout_ms == 5000
    assert client.used_database_name == "test_db"
    assert client.database.used_collection_name == "test_faqs"
    assert len(client.collection.operations) == 1
    assert client.closed is True
