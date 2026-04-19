from backend.app.nlp import IntentClassifier

class IntentService:
    """Niyet işleme servisi."""

    def predict(self, text: str) -> dict:
        """Metni analiz eder ve niyet sonucunu sözlük yapısında döner."""
        intent, confidence = IntentClassifier.predict(text)

        if intent == "unknown":
            return {
                "intent": "unknown",
                "confidence": confidence,
                "answer": "Sorunuzu anlayamadım.",
                "source": "fallback"
            }

        return {
            "intent": intent,
            "confidence": confidence,
            "answer": f"{intent} kategorisinde bir eşleşme bulundu.",
            "source": "rules"
        }