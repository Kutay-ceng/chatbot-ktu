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

    assert payload["answer"]
    assert payload["intent"] == "academic_staff"
    assert payload["mode"] == "faq"
    assert payload["matched_question"] == "Bölüm başkanı kim?"
    assert payload["session_id"] == "session-faq-1"
    assert "source" not in payload

    assert len(payload["sources"]) == 1
    source = payload["sources"][0]
    assert set(source) == {"title", "url", "type", "score"}
    assert source["title"] == payload["matched_question"]
    assert source["url"] == "https://www.ktu.edu.tr/bilgisayar/yonetim"
    assert source["type"] == "faq"
    assert source["score"] == payload["confidence"]


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

    assert payload["answer"]
    assert payload["intent"] == "unknown"
    assert payload["mode"] == "fallback"
    assert payload["sources"] == []
    assert payload["matched_question"] is None
    assert payload["session_id"] == "session-fallback-1"
    assert "source" not in payload
