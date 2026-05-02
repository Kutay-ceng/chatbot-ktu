
from backend.app.schemas.chat import ChatResponse
from backend.app.services.faq_service import FaqService
from backend.app.services.intent_service import IntentService

FALLBACK_ANSWER = (
    "Sorunu net anlayamadım. Bölüm, dersler, akademik kadro veya iletişim bilgileri "
    "hakkında daha spesifik sorabilir misin?"
)


class ChatService:
    """Ana sohbet servisi."""

    def __init__(
        self,
        intent_service: IntentService | None = None,
        faq_service: FaqService | None = None,
    ) -> None:
        self._intent_service = intent_service or IntentService()
        self._faq_service = faq_service or FaqService()

    def handle_message(self, message: str, session_id: str | None = None) -> ChatResponse:
        """Mesajı işler ve yapılandırılmış cevap döner."""
        del session_id
        intent_result = self._intent_service.predict(message)
        current_intent = intent_result["intent"]
        current_conf = intent_result["confidence"]

        match = self._faq_service.find_best_match(message=message, intent=current_intent)

        if match:
            return ChatResponse(
                answer=match.answer,
                intent=match.intent,
                confidence=match.confidence,
                mode="faq",
                matched_question=match.matched_question,
                sources=[
                    {
                        "title": match.matched_question,
                        "url": match.source or "",
                        "type": "faq",
                        "score": match.confidence,
                    }
                ],
    )
        return ChatResponse(
            answer=FALLBACK_ANSWER,
            intent=current_intent,
            confidence=current_conf,
            mode="fallback",
            sources=[{"url": "fallback"}],
        )
