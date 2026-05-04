from backend.app.services.chat_service import ChatService
from backend.app.services.session_service import InMemorySessionStore


def test_chat_service_appends_exchange_to_session_history():
    session_store = InMemorySessionStore()
    chat_service = ChatService(session_store=session_store)

    response = chat_service.handle_message("Bölüm başkanı kim?")

    assert response.session_id
    history = session_store.get_history(response.session_id)
    assert [message.role for message in history] == ["user", "assistant"]
    assert history[0].content == "Bölüm başkanı kim?"
    assert history[1].content == response.answer
    assert history[1].metadata["matched_question"] == "Bölüm başkanı kim?"
