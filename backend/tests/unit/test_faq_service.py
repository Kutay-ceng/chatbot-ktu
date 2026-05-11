import pytest

from backend.app.services.faq_service import FaqService

FAQ_ENTRIES = [
    {
        "question": "Bölüm başkanı kim?",
        "answer": "Bölüm Başkanı: Prof. Dr. Mustafa Ulutaş.",
        "category": "Academic staff",
        "source": "https://example.edu/yonetim",
    },
    {
        "question": "Bölümün telefon numarası nedir?",
        "answer": "Telefon: +90 (462) 377 31 57",
        "category": "Contact information",
        "source": "https://example.edu/iletisim",
    },
    {
        "question": "Staj zorunluluğu kaç gün?",
        "answer": "Toplam 60 gün staj zorunludur.",
        "category": "Courses",
        "source": "https://example.edu/staj",
    },
    {
        "question": "İngilizce hazırlık eğitimi var mı?",
        "answer": "Yeterlilik durumuna göre İngilizce hazırlık uygulanır.",
        "category": "General department information",
        "source": "https://example.edu/hazirlik",
    },
    {
        "question": "Akademik takvimi nereden takip edebilirim?",
        "answer": "Akademik takvim OIDB sayfasında yayınlanır.",
        "category": "Courses",
        "source": "https://example.edu/takvim",
    },
]

QUESTION_TO_ENTRY = {entry["question"]: entry for entry in FAQ_ENTRIES}


class InMemoryFaqRepository:
    def __init__(self, entries: list[dict]) -> None:
        self._entries = entries

    def list_entries(self) -> list[dict]:
        return self._entries


@pytest.fixture
def faq_service() -> FaqService:
    return FaqService(faq_repository=InMemoryFaqRepository(FAQ_ENTRIES))


@pytest.mark.parametrize(
    ("message", "intent", "expected_question"),
    [
        ("BÖLÜM BAŞKANI KİM?!!", "academic_staff", "Bölüm başkanı kim?"),
        ("Telefon numarası nedir?", "contact_info", "Bölümün telefon numarası nedir?"),
        ("Staj kaç gün?", "course_info", "Staj zorunluluğu kaç gün?"),
        ("İngilizce hazırlık var mı", "general_info", "İngilizce hazırlık eğitimi var mı?"),
        (
            "Akademik takvim nereden takip edilir?",
            "course_info",
            "Akademik takvimi nereden takip edebilirim?",
        ),
    ],
)
def test_find_best_match_returns_expected_faq_entry(
    faq_service: FaqService, message: str, intent: str, expected_question: str
) -> None:
    match = faq_service.find_best_match(message=message, intent=intent)

    assert match is not None
    assert match.matched_question == expected_question

    expected_entry = QUESTION_TO_ENTRY[expected_question]
    assert match.answer == expected_entry["answer"]
    assert match.source == expected_entry["source"]
    assert match.confidence >= 0.50


def test_find_best_match_returns_none_for_empty_message(faq_service: FaqService) -> None:
    assert faq_service.find_best_match(message="   ", intent="unknown") is None


def test_find_best_match_returns_none_for_low_confidence_query(faq_service: FaqService) -> None:
    match = faq_service.find_best_match(
        message="Mars ussune nasil giderim",
        intent="unknown",
    )
    assert match is None


def test_find_best_match_honors_custom_threshold() -> None:
    service = FaqService(
        faq_repository=InMemoryFaqRepository(FAQ_ENTRIES),
        match_threshold=0.90,
    )

    # Intent'i "unknown" yaparak +0.30 bonus almasını engelliyoruz,
    # böylece salt TF-IDF skoru 0.90 eşiğinin altında kalıp None dönecek.
    match = service.find_best_match(message="Telefon bilgisi", intent="unknown")

    assert match is None
