import re


class TurkishTextPreprocessor:
    """Kural tabanlı Türkçe ön işleme adımları."""

    @staticmethod
    def lowercase_tr(text: str) -> str:
        """Türkçe karakterleri gözeterek küçük harfe çevirir."""
        if not text:
            return ""
        text = text.replace("I", "ı").replace("İ", "i")
        return text.lower()

    @staticmethod
    def remove_punctuation(text: str) -> str:
        """Noktalama işaretlerini temizler."""
        if not text:
            return ""
        cleaned_text = re.sub(r"[^\w\s]", " ", text)
        return cleaned_text.replace("_", " ")

    @staticmethod
    def tokenize(text: str) -> list[str]:
        """Metni kelimelere böler."""
        return text.split()

    @classmethod
    def process(cls, text: str) -> list[str]:
        """Tüm ön işleme adımlarını uygular."""
        text = cls.lowercase_tr(text)
        text = cls.remove_punctuation(text)
        return cls.tokenize(text)


class IntentClassifier:
    """Niyet sınıflandırıcısı."""

    INTENTS = {
        "course_info": [
            "ders", "müfredat", "kredi", "akts", "sınav", "vize", "final",
            "ödev", "geçme", "not", "proje", "quiz", "staj", "takvim", "dönem",
        ],
        "academic_staff": [
            "hoca", "profesör", "akademisyen", "öğretim", "asistan",
            "danışman", "görevli", "başkan", "anabilim",
        ],
        "contact_info": [
            "iletişim", "telefon", "mail", "posta", "adres", "ulaşım",
            "konum", "fax", "ofis", "oda", "laboratuvar", "teknik", "sorumlu", "sekreter",
        ],
        "general_info": [
            "üniversite", "kampüs", "rektör", "tarihçe", "yurt", "burs",
            "yemekhane", "kütüphane", "program", "eğitim", "lisans", "hazırlık",
            "ingilizce", "unvan",
        ],
    }

    @classmethod
    def predict(cls, text: str) -> tuple[str, float]:
        """Niyeti ve güven skorunu tahmin eder."""
        if not text or not text.strip():
            return "unknown", 0.0

        tokens = TurkishTextPreprocessor.process(text)
        if not tokens:
            return "unknown", 0.0

        intent_scores = {intent: 0 for intent in cls.INTENTS}
        for token in tokens:
            for intent, keywords in cls.INTENTS.items():
                for keyword in keywords:
                    if token.startswith(keyword):
                        intent_scores[intent] += 1
                        break

        scores = list(intent_scores.values())
        max_score = max(scores)
        if max_score == 0:
            return "unknown", 0.0

        top_intents = [i for i, s in intent_scores.items() if s == max_score]
        if len(top_intents) > 1:
            return "unknown", float(max_score)

        return top_intents[0], float(max_score)