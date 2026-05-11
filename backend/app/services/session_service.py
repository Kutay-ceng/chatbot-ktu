import os
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Protocol
from uuid import uuid4

from backend.app.schemas.chat import ChatResponse

DEFAULT_SESSION_COLLECTION = "chat_sessions"
SESSION_STORE_ENV = "CHAT_SESSION_STORE"
MEMORY_SESSION_STORE_TYPES = {"memory", "inmemory", "in_memory"}
MONGO_SESSION_STORE_TYPES = {"mongo", "mongodb"}


@dataclass(frozen=True)
class ConversationMessage:
    """LLM/RAG baglami icin saklanan tek sohbet mesaji."""

    role: str
    content: str
    metadata: dict[str, str | float | None] = field(default_factory=dict)


class SessionStore(Protocol):
    def resolve_session_id(self, session_id: str | None = None) -> str:
        """Mevcut session_id'yi temizler veya yeni bir id üretir."""

    def append_exchange(
        self,
        session_id: str,
        user_message: str,
        response: ChatResponse,
    ) -> None:
        """Kullanıcı mesajını ve asistan cevabını aynı oturuma ekler."""

    def get_history(
        self,
        session_id: str,
        limit: int | None = None,
    ) -> list[ConversationMessage]:
        """Oturum geçmişini döndürür."""


def _clean_session_id(session_id: str | None = None) -> str:
    cleaned_session_id = (session_id or "").strip()
    if cleaned_session_id:
        return cleaned_session_id
    return str(uuid4())


def _validate_max_messages(max_messages_per_session: int) -> int:
    if max_messages_per_session <= 0:
        raise ValueError("max_messages_per_session must be greater than zero")
    return max_messages_per_session


def _assistant_metadata(response: ChatResponse) -> dict[str, str | float | None]:
    return {
        "intent": response.intent,
        "confidence": response.confidence,
        "mode": response.mode,
        "matched_question": response.matched_question,
    }


def _coerce_metadata(value: Any) -> dict[str, str | float | None]:
    if isinstance(value, dict):
        return value
    return {}


class InMemorySessionStore:
    """Gelistirme ortami icin process ici oturum gecmisi."""

    def __init__(self, max_messages_per_session: int = 20) -> None:
        self._max_messages_per_session = _validate_max_messages(max_messages_per_session)
        self._sessions: dict[str, list[ConversationMessage]] = {}

    def resolve_session_id(self, session_id: str | None = None) -> str:
        return _clean_session_id(session_id)

    def append_exchange(
        self,
        session_id: str,
        user_message: str,
        response: ChatResponse,
    ) -> None:
        messages = self._sessions.setdefault(session_id, [])
        messages.extend(
            [
                ConversationMessage(role="user", content=user_message),
                ConversationMessage(
                    role="assistant",
                    content=response.answer,
                    metadata=_assistant_metadata(response),
                ),
            ]
        )

        if len(messages) > self._max_messages_per_session:
            self._sessions[session_id] = messages[-self._max_messages_per_session :]

    def get_history(
        self,
        session_id: str,
        limit: int | None = None,
    ) -> list[ConversationMessage]:
        messages = self._sessions.get(session_id, [])
        if limit is None:
            return list(messages)
        if limit <= 0:
            return []
        return messages[-limit:]

    def clear(self) -> None:
        self._sessions.clear()


class MongoSessionStore:
    """MongoDB üzerinde kalıcı oturum geçmişi saklar.

    chat_sessions şeması:
    {
        session_id,
        created_at,
        updated_at,
        messages: [{role, content, metadata, created_at}]
    }
    """

    def __init__(
        self,
        database: Any,
        collection_name: str = DEFAULT_SESSION_COLLECTION,
        max_messages_per_session: int = 20,
    ) -> None:
        self._collection = database[collection_name]
        self._max_messages_per_session = _validate_max_messages(max_messages_per_session)

    def resolve_session_id(self, session_id: str | None = None) -> str:
        return _clean_session_id(session_id)

    def append_exchange(
        self,
        session_id: str,
        user_message: str,
        response: ChatResponse,
    ) -> None:
        now = datetime.now(UTC)
        user_record = {
            "role": "user",
            "content": user_message,
            "metadata": {},
            "created_at": now,
        }
        assistant_record = {
            "role": "assistant",
            "content": response.answer,
            "metadata": _assistant_metadata(response),
            "created_at": now,
        }

        self._collection.update_one(
            {"session_id": session_id},
            {
                "$setOnInsert": {
                    "session_id": session_id,
                    "created_at": now,
                },
                "$set": {
                    "updated_at": now,
                },
                "$push": {
                    "messages": {
                        "$each": [user_record, assistant_record],
                        "$slice": -self._max_messages_per_session,
                    }
                },
            },
            upsert=True,
        )

    def get_history(
        self,
        session_id: str,
        limit: int | None = None,
    ) -> list[ConversationMessage]:
        if limit is not None and limit <= 0:
            return []

        projection: dict[str, Any] = {"_id": 0, "messages": 1}
        if limit is not None:
            projection["messages"] = {"$slice": -limit}

        document = self._collection.find_one(
            {"session_id": session_id},
            projection,
        )
        if not document:
            return []

        return [
            ConversationMessage(
                role=str(message.get("role", "")),
                content=str(message.get("content", "")),
                metadata=_coerce_metadata(message.get("metadata")),
            )
            for message in document.get("messages", [])
        ]


def create_default_session_store() -> SessionStore:
    store_type = os.getenv(SESSION_STORE_ENV, "memory").strip().lower() or "memory"
    if store_type in MONGO_SESSION_STORE_TYPES:
        from backend.app.db.mongo import get_mongo_database

        collection_name = (
            os.getenv("MONGODB_SESSION_COLLECTION", DEFAULT_SESSION_COLLECTION).strip()
            or DEFAULT_SESSION_COLLECTION
        )
        return MongoSessionStore(
            database=get_mongo_database(),
            collection_name=collection_name,
        )

    if store_type not in MEMORY_SESSION_STORE_TYPES:
        raise ValueError(f"{SESSION_STORE_ENV} must be 'memory' or 'mongo'.")

    return InMemorySessionStore()
