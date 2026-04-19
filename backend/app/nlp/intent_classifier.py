import re


class TurkishTextPreprocessor:
    """Kural tabanli Turkce on-isleme adimlari."""

    @staticmethod
    def lowercase_tr(text: str) -> str:
        """Convert text to lowercase with Turkish character handling."""
        if not text:
            return ""
        text = text.replace("I", "ı").replace("İ", "i")
        return text.lower()

    @staticmethod
    def remove_punctuation(text: str) -> str:
        """Remove punctuation from text."""
        if not text:
            return ""
        cleaned_text = re.sub(r"[^\w\s]", " ", text)
        return cleaned_text.replace("_", " ")

    @staticmethod
    def tokenize(text: str) -> list[str]:
        """Split text into tokens."""
        return text.split()

    @classmethod
    def process(cls, text: str) -> list[str]:
        """Process text through all preprocessing steps."""
        text = cls.lowercase_tr(text)
        text = cls.remove_punctuation(text)
        return cls.tokenize(text)


class IntentClassifier:
    """Durumsuz, sinif seviyesinde calisan niyet siniflandirici."""

    INTENTS = {
        "course_info": [
            "ders",
            "müfredat",
            "kredi",
            "akts",
            "sınav",
            "vize",
            "final",
            "ödev",
            "geçme",
            "not",
            "proje",
            "quiz",
            "staj",
            "takvim",
            "dönem",
        ],
        "academic_staff": [
            "hoca",
            "profesör",
            "akademisyen",
            "öğretim",
            "asistan",
            "danışman",
            "görevli",
            "başkan",
            "anabilim",
        ],
        "contact_info": [
            "iletişim",
            "telefon",
            "mail",
            "posta",
            "adres",
            "ulaşım",
            "konum",
            "fax",
            "ofis",
            "oda",
            "laboratuvar",
            "teknik",
            "sorumlu",
            "sekreter",
        ],
        "general_info": [
            "üniversite",
            "kampüs",
            "rektör",
            "tarihçe",
            "yurt",
            "burs",
            "yemekhane",
            "kütüphane",
            "program",
            "eğitim",
            "lisans",
            "hazırlık",
            "ingilizce",
            "unvan",
        ],
    }

    @classmethod
    def predict(cls, text: str) -> str:
        """Predict intent from text input."""
        if not text or not text.strip():
            return "unknown"

        tokens = TurkishTextPreprocessor.process(text)
        if not tokens:
            return "unknown"

        intent_scores = {intent: 0 for intent in cls.INTENTS}
        
        for token in tokens:
            for intent, keywords in cls.INTENTS.items():
                for keyword in keywords:
                    if token.startswith(keyword):
                        intent_scores[intent] += 1
                        break

        # Get max score with fallback for empty values
        scores = intent_scores.values()
        if not scores:
            return "unknown"
        
        max_score = max(scores)
        if max_score == 0:
            return "unknown"

        top_intents = [
            intent
            for intent, score in intent_scores.items()
            if score == max_score
        ]
        if len(top_intents) > 1:
            return "unknown"

        return top_intents[0]