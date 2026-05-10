import re
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

# 0.50 altındaki FAQ eşleşmeleri güvenli kabul edilmez ve fallback'e düşer.
DEFAULT_MATCH_THRESHOLD = 0.50
INTENT_MATCH_BONUS = 0.30       # Intent eşleşirse güçlü bonus
INTENT_MISMATCH_PENALTY = 0.20  # Intent uyuşmazsa ceza (Yanlış fallback'i engellemek için)
QUESTION_SCORE_WEIGHT = 0.70
DOCUMENT_SCORE_WEIGHT = 0.30
CONTENT_STOP_WORDS = {
    "alabilirim",
    "atabilirim",
    "bilgiler",
    "bilgileri",
    "edebilirim",
    "görebilirim",
    "hakkında",
    "hangi",
    "için",
    "kimler",
    "nasıl",
    "neden",
    "nedir",
    "nerede",
    "nereden",
    "nereye",
    "oluyor",
    "yapılır",
}
GENERIC_CONTENT_WORDS = {
    "bilgisayar",
    "bölüm",
    "bölümü",
    "bölümün",
    "mühendisliği",
}

@dataclass(frozen=True)
class FaqMatch:
    """SSS eşleşme sonucu."""
    answer: str
    intent: str
    confidence: float
    source: str | None = None
    matched_question: str | None = None

def _normalize_text(text: str) -> str:
    text = re.sub(
        r"\be[\s-]?(?:posta|mail)\b|\bemail\b|\bmail\b",
        "eposta",
        text or "",
        flags=re.IGNORECASE,
    )
    return " ".join(TurkishTextPreprocessor.process(text))

def _has_all(text: str, terms: tuple[str, ...]) -> bool:
    return all(term in text for term in terms)

def _content_tokens(text: str) -> list[str]:
    return [
        token
        for token in _normalize_text(text).split()
        if len(token) >= 4
        and token not in CONTENT_STOP_WORDS
        and token not in GENERIC_CONTENT_WORDS
    ]

def _has_content_overlap(query_tokens: list[str], document_tokens: list[str]) -> bool:
    for query_token in query_tokens:
        for document_token in document_tokens:
            if query_token.startswith(document_token) or document_token.startswith(query_token):
                return True
    return False

def _domain_score_adjustment(
    normalized_query: str,
    normalized_question: str,
    normalized_doc: str,
) -> float:
    adjustment = 0.0

    if "ulaş" in normalized_query and "ulaş" in normalized_question:
        adjustment += 0.25

    if "eposta" in normalized_query and "eposta" in normalized_doc:
        adjustment += 0.35

    if _has_all(normalized_query, ("laboratuvar", "teknik")):
        asks_for_list = "kimler" in normalized_query or "sorumluları" in normalized_query
        is_list_entry = "personel" in normalized_question and "listesi" in normalized_question
        is_specific_lab = "pc lab" in normalized_question or "grafik lab" in normalized_question
        mentions_specific_lab = "pc" in normalized_query or "grafik" in normalized_query

        if asks_for_list and is_list_entry:
            adjustment += 0.20
        if asks_for_list and is_specific_lab and not mentions_specific_lab:
            adjustment -= 0.10

    return adjustment

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
        normalized_questions: list[str] = []
        normalized_docs: list[str] = []
        document_content_tokens: list[list[str]] = []

        for entry in _faq_entries(self._faq_repository):
            question = str(entry.get("question", "")).strip()
            answer = str(entry.get("answer", "")).strip()
            if not question or not answer:
                continue

            normalized_question = _normalize_text(question)
            if not normalized_question:
                continue

            # Soru ve cevabı birleştirerek daha zengin TF-IDF metni elde et
            combined_text = f"{question} {answer}"
            normalized_doc = _normalize_text(combined_text)
            if not normalized_doc:
                continue

            valid_entries.append(entry)
            normalized_questions.append(normalized_question)
            normalized_docs.append(normalized_doc)
            document_content_tokens.append(_content_tokens(combined_text))

        if not valid_entries:
            return None

        # Sonekli kelimeleri yakalayabilmek için karakter n-gram analizi
        # kullan (Örn: "ulaşırım" vs "ulaşabilirim")
        vectorizer = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(3, 5),
            lowercase=True,
        )

        question_matrix = vectorizer.fit_transform(normalized_questions)
        question_vector = vectorizer.transform([normalized_query])
        question_scores = cosine_similarity(question_vector, question_matrix).ravel()

        doc_matrix = vectorizer.fit_transform(normalized_docs)
        doc_vector = vectorizer.transform([normalized_query])
        doc_scores = cosine_similarity(doc_vector, doc_matrix).ravel()

        best_index = -1
        best_score = -1.0
        best_category_boosted = False
        query_content_tokens = _content_tokens(message)

        for index, entry in enumerate(valid_entries):
            if query_content_tokens and not _has_content_overlap(
                query_content_tokens,
                document_content_tokens[index],
            ):
                continue

            base_score = (
                QUESTION_SCORE_WEIGHT * float(question_scores[index])
                + DOCUMENT_SCORE_WEIGHT * float(doc_scores[index])
            )
            adjusted_score = base_score + _domain_score_adjustment(
                normalized_query,
                normalized_questions[index],
                normalized_docs[index],
            )

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
