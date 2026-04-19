from backend.app.schemas.chat import ChatResponse
from backend.app.services.faq_service import FaqService
from backend.app.services.intent_service import IntentService

FALLBACK_ANSWER = (
    "Sorunu net anlayamadım. Bölüm, dersler, akademik kadro veya iletişim bilgileri "
    "hakkında daha spesifik sorabilir misin?"
)


class ChatService:
    def __init__(
        self,
        intent_service: IntentService | None = None,
        faq_service: FaqService | None = None,
    ) -> None:
        self._intent_service = intent_service or IntentService()
        self._faq_service = faq_service or FaqService()

    def handle_message(self, message: str, session_id: str | None = None) -> ChatResponse:
        del session_id  # Reserved for future conversation-state support.

        intent_result = self._intent_service.predict(message)
        
        # If intent is unknown, return fallback immediately without querying FAQ
        if intent_result.intent == "unknown":
            return ChatResponse(
                answer=FALLBACK_ANSWER,
                intent="unknown",
                confidence=intent_result.confidence,
            )
        
        match = self._faq_service.find_best_match(message=message, intent=intent_result.intent)

        if match:
            return ChatResponse(
                answer=match.answer,
                intent=match.intent,
                confidence=match.confidence,
                source=match.source,
                matched_question=match.question,
            )

        return ChatResponse(
            answer=FALLBACK_ANSWER,
            intent=intent_result.intent,
            confidence=intent_result.confidence,
        )