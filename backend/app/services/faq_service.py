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
    answer: str
    intent: str
    confidence: float
    source: str | None = None
    question: str | None = None


def _normalize_text(text: str) -> str:
    return " ".join(TurkishTextPreprocessor.process(text or ""))


def _tokenize_text(text: str) -> list[str]:
    normalized = _normalize_text(text)
    if not normalized:
        return []
    return normalized.split()


class FaqService:
    def __init__(self, faq_repository: FaqRepository | None = None) -> None:
        self._faq_repository = faq_repository or FaqRepository()

    def find_best_match(self, message: str, intent: str) -> FaqMatch | None:
        query_tokens = set(_tokenize_text(message))
        if not query_tokens:
            return None

        normalized_query = _normalize_text(message)
        best_entry: dict | None = None
        best_score = 0.0
        best_category_boosted = False

        for entry in self._faq_repository.list_entries():
            question = str(entry.get("question", "")).strip()
            answer = str(entry.get("answer", "")).strip()
            if not question or not answer:
                continue

            question_tokens = set(_tokenize_text(question))
            if not question_tokens:
                continue

            normalized_question = _normalize_text(question)
            overlap_score = len(query_tokens.intersection(question_tokens)) / len(question_tokens)

            if normalized_query and normalized_query in normalized_question:
                overlap_score = max(overlap_score, 0.95)
            elif normalized_question and normalized_question in normalized_query:
                overlap_score = max(overlap_score, 0.85)

            entry_intent = CATEGORY_TO_INTENT.get(str(entry.get("category", "")).strip(), "unknown")
            category_boosted = intent != "unknown" and entry_intent == intent
            if category_boosted:
                overlap_score += 0.05

            if overlap_score > best_score or (
                overlap_score == best_score and category_boosted and not best_category_boosted
            ):
                best_entry = entry
                best_score = overlap_score
                best_category_boosted = category_boosted

        if best_entry is None or best_score < 0.30:
            return None

        source = best_entry.get("source")
        matched_question = str(best_entry.get("question", "")).strip() or None
        matched_intent = CATEGORY_TO_INTENT.get(
            str(best_entry.get("category", "")).strip(),
            intent,
        )

        return FaqMatch(
            answer=str(best_entry.get("answer", "")).strip(),
            intent=matched_intent,
            confidence=round(min(best_score, 1.0), 3),
            source=str(source).strip() if source else None,
            question=matched_question,
        )
