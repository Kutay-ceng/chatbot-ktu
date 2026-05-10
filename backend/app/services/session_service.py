import os
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Protocol
from uuid import uuid4

from backend.app.schemas.chat import ChatResponse

DEFAULT_SESSION_COLLECTION = "chat_sessions"
SESSION_STORE_ENV = "CHAT_SESSION_STORE"


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


class InMemorySessionStore:
    """Gelistirme ortami icin process ici oturum gecmisi."""

    def __init__(self, max_messages_per_session: int = 20) -> None:
        self._max_messages_per_session = max_messages_per_session
        self._sessions: dict[str, list[ConversationMessage]] = {}

    def resolve_session_id(self, session_id: str | None = None) -> str:
        cleaned_session_id = (session_id or "").strip()
        if cleaned_session_id:
            return cleaned_session_id
        return str(uuid4())

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
                    metadata={
                        "intent": response.intent,
                        "confidence": response.confidence,
                        "mode": response.mode,
                        "matched_question": response.matched_question,
                    },
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
        self._max_messages_per_session = max_messages_per_session

    def resolve_session_id(self, session_id: str | None = None) -> str:
        cleaned_session_id = (session_id or "").strip()
        if cleaned_session_id:
            return cleaned_session_id
        return str(uuid4())
