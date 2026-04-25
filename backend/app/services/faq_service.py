from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from backend.app.nlp import TurkishTextPreprocessor
from backend.app.repositories import FaqRepository

CATEGORY_TO_INTENT = {
    "General department information": "general_info",
    "Courses": "course_info",
    "Academic staff": "academic_staff",
    "Contact information": "contact_info",
}
DEFAULT_MATCH_THRESHOLD = 0.40
INTENT_MATCH_BONUS = 0.05


@dataclass(frozen=True)
class FaqMatch:
    answer: str
    intent: str
    confidence: float
    source: str | None = None
    matched_question: str | None = None


def _normalize_text(text: str) -> str:
    return " ".join(TurkishTextPreprocessor.process(text or ""))


class FaqService:
    def __init__(
        self,
        faq_repository: FaqRepository | None = None,
        match_threshold: float = DEFAULT_MATCH_THRESHOLD,
    ) -> None:
        self._faq_repository = faq_repository or FaqRepository()
        self._match_threshold = match_threshold

    def find_best_match(self, message: str, intent: str) -> FaqMatch | None:
        normalized_query = _normalize_text(message)
        if not normalized_query:
            return None

        valid_entries: list[dict] = []
        normalized_questions: list[str] = []

        for entry in self._faq_repository.list_entries():
            question = str(entry.get("question", "")).strip()
            answer = str(entry.get("answer", "")).strip()
            if not question or not answer:
                continue

            normalized_question = _normalize_text(question)
            if not normalized_question:
                continue

            valid_entries.append(entry)
            normalized_questions.append(normalized_question)

        if not valid_entries:
            return None

        vectorizer = TfidfVectorizer(
            tokenizer=str.split,
            token_pattern=None,
            lowercase=False,
            ngram_range=(1, 2),
        )
        question_matrix = vectorizer.fit_transform(normalized_questions)
        query_vector = vectorizer.transform([normalized_query])
        cosine_scores = cosine_similarity(query_vector, question_matrix).ravel()

        best_index = -1
        best_score = 0.0
        best_category_boosted = False

        for index, (entry, cosine_score) in enumerate(zip(valid_entries, cosine_scores)):
            adjusted_score = float(cosine_score)
            entry_intent = CATEGORY_TO_INTENT.get(str(entry.get("category", "")).strip(), "unknown")
            category_boosted = intent != "unknown" and entry_intent == intent
            if category_boosted:
                adjusted_score += INTENT_MATCH_BONUS

            if adjusted_score > best_score or (
                adjusted_score == best_score and category_boosted and not best_category_boosted
            ):
                best_index = index
                best_score = adjusted_score
                best_category_boosted = category_boosted

        if best_index == -1 or best_score < self._match_threshold:
            return None

        best_entry = valid_entries[best_index]
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
            matched_question=matched_question,
        )
