from dataclasses import dataclass

from backend.app.nlp import IntentClassifier


@dataclass(frozen=True)
class IntentResult:
    intent: str
    confidence: float | None = None


class IntentService:
    def predict(self, text: str) -> IntentResult:
        intent = IntentClassifier.predict(text)
        return IntentResult(intent=intent)
