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

    # İstenilen tüm zorunlu alanların response içinde bulunduğunu test et
    expected_keys = {
        "answer", "intent", "confidence", "mode", 
        "matched_question", "sources", "session_id"
    }
    assert set(payload.keys()) == expected_keys
    
    # Eski `source` alanının response içinde olmadığını doğrula
    assert "source" not in payload

    assert payload["answer"]
    assert payload["intent"] == "academic_staff"
    assert payload["mode"] == "faq"
    assert payload["matched_question"] is not None
    assert payload["confidence"] is not None
    
    # FAQ response için sources kontrolü
    assert isinstance(payload["sources"], list)
    assert len(payload["sources"]) > 0
    
    # FAQ source içindeki objenin alanlarını test et (title, url, type, score)
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

    # İstenilen tüm zorunlu alanların response içinde bulunduğunu test et
    expected_keys = {
        "answer", "intent", "confidence", "mode", 
        "matched_question", "sources", "session_id"
    }
    assert set(payload.keys()) == expected_keys
    
    # Eski `source` alanının response içinde olmadığını doğrula
    assert "source" not in payload

    assert payload["answer"]
    assert payload["intent"] == "unknown"
    
    # Fallback response kontrolleri
    assert payload["mode"] == "fallback"
    assert payload["sources"] == []
    assert payload["matched_question"] is None
