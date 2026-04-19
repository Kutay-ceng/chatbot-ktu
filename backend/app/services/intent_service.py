# -*- coding: utf-8 -*-
from dataclasses import dataclass

from backend.app.nlp import IntentClassifier


@dataclass(frozen=True)
class IntentResult:
    """Niyet sınıflandırma sonucunu tutan veri yapısı."""
    intent: str
    confidence: float | None = None
    answer: str | None = None
    source: str | None = None


class IntentService:
    """NLP niyetlerini işleyen servis katmanı."""

    def predict(self, text: str) -> IntentResult:
        """
        Metni analiz eder ve yapılandırılmış niyet sonucu döner.
        """
        # 1. NLP modülünden ham verileri alıyoruz
        intent, confidence = IntentClassifier.predict(text)

        # 2. Bilinmeyen niyet durumu (Testlerin beklediği fallback senaryosu)
        if intent == "unknown":
            return IntentResult(
                intent="unknown",
                confidence=confidence,
                answer="Üzgünüm, sorunuzu tam olarak anlayamadım.",
                source="fallback"
            )

        # 3. Başarılı eşleşme durumu (Testlerin beklediği rules senaryosu)
        return IntentResult(
            intent=intent,
            confidence=confidence,
            answer=f"{intent} kategorisinde bir eşleşme bulundu.",
            source="rules"
        )