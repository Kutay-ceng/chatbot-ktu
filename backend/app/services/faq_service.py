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

# Char n-gram kullanıldığı için eşik değeri hafif düşürüldü.
DEFAULT_MATCH_THRESHOLD = 0.30
INTENT_MATCH_BONUS = 0.30       # Intent eşleşirse güçlü bonus
INTENT_MISMATCH_PENALTY = 0.20  # Intent uyuşmazsa ceza (Yanlış fallback'i engellemek için)

@dataclass(frozen=True)
class FaqMatch:
    """SSS eşleşme sonucu."""
    answer: str
    intent: str
    confidence: float
    source: str | None = None
    matched_question: str | None = None

def _normalize_text(text: str) -> str:
    return " ".join(TurkishTextPreprocessor.process(text or ""))

def _faq_entries(faq_repository: FaqRepository) -> list[dict]:
    if hasattr(faq_repository, "get_all"):
        return faq_repository.get_all()
    if hasattr(faq_repository, "list_entries"):
        return faq_repository.list_entries()
    raise AttributeError("FaqRepository must implement get_all()")

class FaqService:
    """SSS arama ve eşleştirme servisi."""

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
        normalized_docs: list[str] = []

        for entry in _faq_entries(self._faq_repository):
            question = str(entry.get("question", "")).strip()
            answer = str(entry.get("answer", "")).strip()
            if not question or not answer:
                continue

            # Soru ve cevabı birleştirerek daha zengin TF-IDF metni elde et
            combined_text = f"{question} {answer}"
            normalized_doc = _normalize_text(combined_text)
            if not normalized_doc:
                continue

            valid_entries.append(entry)
            normalized_docs.append(normalized_doc)

        if not valid_entries:
            return None

        # Sonekli kelimeleri yakalayabilmek için karakter n-gram analizi
        # kullan (Örn: "ulaşırım" vs "ulaşabilirim")
        vectorizer = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(3, 5),
            lowercase=True,
        )

        doc_matrix = vectorizer.fit_transform(normalized_docs)
        query_vector = vectorizer.transform([normalized_query])

        cosine_scores = cosine_similarity(query_vector, doc_matrix).ravel()

        best_index = -1
        best_score = -1.0
        best_category_boosted = False

        for index, (entry, cosine_score) in enumerate(zip(valid_entries, cosine_scores)):
            adjusted_score = float(cosine_score)

            entry_intent = CATEGORY_TO_INTENT.get(str(entry.get("category", "")).strip(), "unknown")

            category_boosted = False
            if intent != "unknown":
                if entry_intent == intent:
                    adjusted_score += INTENT_MATCH_BONUS
                    category_boosted = True
                else:
                    adjusted_score -= INTENT_MISMATCH_PENALTY

            if adjusted_score > best_score or (
                adjusted_score == best_score and category_boosted and not best_category_boosted
            ):
                best_index = index
                best_score = adjusted_score
                best_category_boosted = category_boosted

        if best_index == -1 or best_score < self._match_threshold:
            return None

        best_entry = valid_entries[best_index]
        source = str(best_entry.get("source", "")).strip() or None
        matched_question = str(best_entry.get("question", "")).strip() or None
        matched_intent = CATEGORY_TO_INTENT.get(
            str(best_entry.get("category", "")).strip(),
            intent,
        )

        # Güven skorunu 0-1 aralığında normalize et
        final_confidence = max(0.0, min(best_score, 1.0))

        return FaqMatch(
            answer=str(best_entry.get("answer", "")).strip(),
            intent=matched_intent,
            confidence=round(final_confidence, 3),
            source=source,
            matched_question=matched_question,
        )