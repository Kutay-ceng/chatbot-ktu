from backend.app.schemas.chat import ChatResponse
from backend.app.services.session_service import InMemorySessionStore


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
    response = ChatResponse(
        answer="Bölüm Başkanı: Prof. Dr. Mustafa Ulutaş.",
        intent="academic_staff",
        confidence=1.0,
        mode="faq",
        matched_question="Bölüm başkanı kim?",
        sources=[],
        session_id="session-1",
    )

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
