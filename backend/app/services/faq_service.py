from dataclasses import dataclass

from backend.app.nlp import TurkishTextPreprocessor
from backend.app.repositories import FaqRepository

CATEGORY_TO_INTENT = {
    "General department information": "general_info",
    "Courses": "course_info",
    "Academic staff": "academic_staff",
    "Contact information": "contact_info",
}


@dataclass(frozen=True)
class FaqMatch:
    """SSS eşleşme sonucu."""
    answer: str
    intent: str
    confidence: float
    source: str | None = None
    question: str | None = None

class FaqService:
    """SSS arama ve eşleştirme servisi."""

    def __init__(self, faq_repository: FaqRepository | None = None) -> None:
        self._faq_repository = faq_repository or FaqRepository()

    def find_best_match(self, message: str, intent: str) -> FaqMatch | None:
        """En iyi soru eşleşmesini bulur."""
        if intent == "unknown":
            return None

        query_tokens = set(TurkishTextPreprocessor.process(message))
        if not query_tokens:
            return None

        best_entry, best_score = None, 0.0

        for entry in self._faq_repository.get_all():
            question_text = str(entry.get("question", ""))
            q_tokens = set(TurkishTextPreprocessor.process(question_text))
            if not q_tokens:
                continue

            overlap = len(query_tokens.intersection(q_tokens)) / len(q_tokens)
            
            category_str = str(entry.get("category", "")).strip()
            entry_intent = CATEGORY_TO_INTENT.get(category_str, "unknown")
            if intent != "unknown" and entry_intent == intent:
                overlap += 0.05

            if overlap > best_score:
                best_entry, best_score = entry, overlap

        if best_entry is None or best_score < 0.30:
            return None

        matched_intent = CATEGORY_TO_INTENT.get(str(best_entry.get("category")), intent)
        return FaqMatch(
            answer=str(best_entry.get("answer", "")).strip(),
            intent=matched_intent,
            confidence=round(min(best_score, 1.0), 3),
            source=str(best_entry.get("source", "rules")),
            question=str(best_entry.get("question", ""))
        )