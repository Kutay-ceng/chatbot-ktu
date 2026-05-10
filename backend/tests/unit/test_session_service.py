from backend.app.schemas.chat import ChatResponse
from backend.app.services import session_service as session_module
from backend.app.services.session_service import InMemorySessionStore, MongoSessionStore


class FakeUpdateResult:
    pass


class FakeCollection:
    def __init__(self) -> None:
        self.documents: dict[str, dict] = {}
        self.last_filter: dict | None = None
        self.last_update: dict | None = None
        self.last_upsert: bool | None = None

    def update_one(self, filter: dict, update: dict, upsert: bool = False) -> FakeUpdateResult:
        self.last_filter = filter
        self.last_update = update
        self.last_upsert = upsert

        session_id = filter["session_id"]
        is_new_document = session_id not in self.documents
        document = self.documents.setdefault(session_id, {"messages": []})

        if is_new_document:
            document.update(update.get("$setOnInsert", {}))
        document.update(update.get("$set", {}))

        push_spec = update["$push"]["messages"]
        document["messages"].extend(push_spec["$each"])
        slice_size = push_spec.get("$slice")
        if slice_size is not None and slice_size < 0:
            document["messages"] = document["messages"][slice_size:]

        return FakeUpdateResult()

    def find_one(self, filter: dict, projection: dict) -> dict | None:
        document = self.documents.get(filter["session_id"])
        if document is None:
            return None

        messages = list(document.get("messages", []))
        messages_projection = projection.get("messages")
        if isinstance(messages_projection, dict) and "$slice" in messages_projection:
            messages = messages[messages_projection["$slice"] :]

        return {"messages": messages}


class FakeDatabase:
    def __init__(self) -> None:
        self.collection = FakeCollection()
        self.used_collection_name: str | None = None

    def __getitem__(self, collection_name: str) -> FakeCollection:
        self.used_collection_name = collection_name
        return self.collection


def _chat_response() -> ChatResponse:
    return ChatResponse(
        answer="Bölüm Başkanı: Prof. Dr. Mustafa Ulutaş.",
        intent="academic_staff",
        confidence=1.0,
        mode="faq",
        matched_question="Bölüm başkanı kim?",
        sources=[],
        session_id="session-1",
    )


def test_resolve_session_id_keeps_existing_value():
    store = InMemorySessionStore()

    assert store.resolve_session_id(" session-1 ") == "session-1"


def test_resolve_session_id_generates_value_when_missing():
    store = InMemorySessionStore()

    session_id = store.resolve_session_id()

    assert session_id
    assert store.resolve_session_id(session_id) == session_id


def test_append_exchange_stores_user_and_assistant_messages():
    store = InMemorySessionStore()
    response = _chat_response()

    store.append_exchange("session-1", "Bölüm başkanı kim?", response)

    history = store.get_history("session-1")
    assert [message.role for message in history] == ["user", "assistant"]
    assert history[0].content == "Bölüm başkanı kim?"
    assert history[1].content == response.answer
    assert history[1].metadata["intent"] == "academic_staff"
    assert history[1].metadata["mode"] == "faq"


def test_append_exchange_trims_old_messages():
    store = InMemorySessionStore(max_messages_per_session=2)
    response = ChatResponse(
        answer="Yanıt",
        intent="unknown",
        confidence=0.0,
        mode="fallback",
        matched_question=None,
        sources=[],
        session_id="session-1",
    )

    store.append_exchange("session-1", "ilk soru", response)
    store.append_exchange("session-1", "ikinci soru", response)

    history = store.get_history("session-1")
    assert len(history) == 2
    assert history[0].content == "ikinci soru"
    assert history[1].content == "Yanıt"


def test_mongo_session_store_appends_exchange_to_session_document():
    database = FakeDatabase()
    store = MongoSessionStore(database=database, collection_name="chat_sessions")
    response = _chat_response()

    store.append_exchange("session-1", "Bölüm başkanı kim?", response)

    assert database.used_collection_name == "chat_sessions"
    collection = database.collection
    assert collection.last_filter == {"session_id": "session-1"}
    assert collection.last_upsert is True

    document = collection.documents["session-1"]
    assert document["session_id"] == "session-1"
    assert "created_at" in document
    assert "updated_at" in document
    assert [message["role"] for message in document["messages"]] == ["user", "assistant"]
    assert document["messages"][0]["content"] == "Bölüm başkanı kim?"
    assert document["messages"][1]["content"] == response.answer
    assert document["messages"][1]["metadata"] == {
        "intent": "academic_staff",
        "confidence": 1.0,
        "mode": "faq",
        "matched_question": "Bölüm başkanı kim?",
    }


def test_mongo_session_store_keeps_same_session_and_trims_messages():
    database = FakeDatabase()
    store = MongoSessionStore(
        database=database,
        collection_name="chat_sessions",
        max_messages_per_session=2,
    )
    response = _chat_response()

    store.append_exchange("session-1", "ilk soru", response)
    store.append_exchange("session-1", "ikinci soru", response)

    history = store.get_history("session-1")
    assert len(history) == 2
    assert history[0].role == "user"
    assert history[0].content == "ikinci soru"
    assert history[1].role == "assistant"
    assert history[1].metadata["matched_question"] == "Bölüm başkanı kim?"


def test_mongo_session_store_get_history_respects_limit():
    database = FakeDatabase()
    store = MongoSessionStore(database=database, collection_name="chat_sessions")
    response = _chat_response()
    store.append_exchange("session-1", "ilk soru", response)
    store.append_exchange("session-1", "ikinci soru", response)

    history = store.get_history("session-1", limit=1)

    assert len(history) == 1
    assert history[0].role == "assistant"


def test_create_default_session_store_uses_mongo_when_configured(monkeypatch):
    database = FakeDatabase()
    monkeypatch.setenv("CHAT_SESSION_STORE", "mongo")
    monkeypatch.setenv("MONGODB_SESSION_COLLECTION", "test_chat_sessions")
    monkeypatch.setattr(
        "backend.app.db.mongo.get_mongo_database",
        lambda: database,
    )

    store = session_module.create_default_session_store()

    assert isinstance(store, MongoSessionStore)
    assert database.used_collection_name == "test_chat_sessions"
