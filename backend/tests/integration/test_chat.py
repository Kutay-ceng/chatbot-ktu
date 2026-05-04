from uuid import UUID

from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_chat_returns_structured_response_with_source_when_matched():
    response = client.post(
        "/chat",
        json={"message": "Bölüm başkanı kim?", "session_id": "session-faq-1"},
    )

    assert response.status_code == 200
    payload = response.json()

    expected_keys = {
        "answer",
        "intent",
        "confidence",
        "mode",
        "matched_question",
        "sources",
        "session_id",
    }
    assert set(payload.keys()) == expected_keys
    assert "source" not in payload

    assert payload["answer"]
    assert payload["intent"] == "academic_staff"
    assert payload["mode"] == "faq"
    assert payload["matched_question"] is not None
    assert payload["confidence"] is not None

    assert isinstance(payload["sources"], list)
    assert len(payload["sources"]) > 0

    source_item = payload["sources"][0]
    expected_source_keys = {"title", "url", "type", "score"}
    assert set(source_item.keys()) == expected_source_keys
    assert source_item["type"] == "faq"


def test_chat_returns_400_for_empty_message():
    response = client.post("/chat", json={"message": "   "})

    assert response.status_code == 400
    assert response.json()["detail"] == "message must not be empty"


def test_chat_returns_fallback_when_no_match():
    response = client.post(
        "/chat",
        json={"message": "Mars üssüne nasıl gidebilirim?", "session_id": "session-fallback-1"},
    )

    assert response.status_code == 200
    payload = response.json()

    expected_keys = {
        "answer",
        "intent",
        "confidence",
        "mode",
        "matched_question",
        "sources",
        "session_id",
    }
    assert set(payload.keys()) == expected_keys
    assert "source" not in payload

    assert payload["answer"]
    assert payload["intent"] == "unknown"

    assert payload["mode"] == "fallback"
    assert payload["sources"] == []
    assert payload["matched_question"] is None
    assert payload["session_id"] == "session-fallback-1"


def test_chat_generates_session_id_when_missing():
    response = client.post("/chat", json={"message": "Bölüm başkanı kim?"})

    assert response.status_code == 200
    payload = response.json()

    assert payload["session_id"]
    UUID(payload["session_id"])
