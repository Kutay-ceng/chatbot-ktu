from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_chat_returns_structured_response_with_source_when_matched():
    response = client.post("/chat", json={"message": "Bölüm başkanı kim?"})

    assert response.status_code == 200
    payload = response.json()

    assert payload["answer"]
    assert payload["intent"] == "academic_staff"
    assert payload["mode"] == "faq"
    assert len(payload["sources"]) > 0


def test_chat_returns_400_for_empty_message():
    response = client.post("/chat", json={"message": "   "})

    assert response.status_code == 400
    assert response.json()["detail"] == "message must not be empty"


def test_chat_returns_fallback_when_no_match():
    response = client.post("/chat", json={"message": "Mars üssüne nasıl gidebilirim?"})

    assert response.status_code == 200
    payload = response.json()

    assert payload["answer"]
    assert payload["intent"] == "unknown"
    # BURASI DÜZELTİLDİ: Yeni modele göre güncellendi
    assert payload["mode"] == "fallback"
    assert payload["sources"][0]["url"] == "fallback"