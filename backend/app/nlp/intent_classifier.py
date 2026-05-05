import difflib  # <-- Benzerlik ölçümü için yerleşik kütüphaneyi ekliyoruz
import re


class TurkishTextPreprocessor:
    """Kural tabanlı ön işleme adımları."""
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
    """Niyet sınıflandırıcı."""
    
    INTENTS = {
        "course_info": [
            "ders", "müfredat", "kredi", "akts", "sınav", "vize", "final",
            "ödev", "geçme", "not", "proje", "quiz", "staj", "takvim", "dönem",
            "içerik", "haftalık", "zorunlu", "gün"
        ],
        "academic_staff": [
            "hoca", "profesör", "akademisyen", "öğretim", "asistan",
            "danışman", "görevli", "başkan", "anabilim", "randevu", "dal"
        ],
        "contact_info": [
            "iletişim", "telefon", "mail", "posta", "adres", "ulaşım",
            "konum", "fax", "ofis", "oda", "laboratuvar", "teknik", "sorumlu", "sekreter",
            "numara"
        ],
        "general_info": [
            "üniversite", "kampüs", "rektör", "tarihçe", "yurt", "burs",
            "yemekhane", "kütüphane", "program", "eğitim", "lisans", "hazırlık",
            "ingilizce", "unvan", "ktü", "bilgisayar", "mühendis", "öğrenci", "yemek"
        ],
    }

    @classmethod
    def predict(cls, text: str) -> tuple[str, float]:
        """Niyeti ve güven skorunu (0.0 - 1.0 aralığında) tahmin eder."""
        if not text or not text.strip():
            return "unknown", 0.0

        tokens = TurkishTextPreprocessor.process(text)
        if not tokens:
            return "unknown", 0.0

        intent_scores = {intent: 0 for intent in cls.INTENTS}

        for token in tokens:
            for intent, keywords in cls.INTENTS.items():
                for keyword in keywords:
                    # 1. Birebir veya kökten eşleşme (Mevcut mantık)
                    if token.startswith(keyword):
                        intent_scores[intent] += 1
                        break
                    
                    # 2. Yazım hatası toleransı (Fuzzy Matching)
                    # ÇOK ÖNEMLİ: Kısa kelimelerde (ör: "da" vs "dal") saçma 
                    # eşleşmeleri önlemek için uzunluk şartı
                    if len(token) >= 4 and len(keyword) >= 4:
                        similarity = difflib.SequenceMatcher(None, token, keyword).ratio()
                        if similarity > 0.75:
                            intent_scores[intent] += 1
                            break

        scores = list(intent_scores.values())
        total_matches = sum(scores)
        
        if total_matches == 0:
            return "unknown", 0.0

        max_score = max(scores)
        top_intents = [i for i, s in intent_scores.items() if s == max_score]

        # Güven skorunu 0-1 aralığında anlamlı hale getir
        confidence = float(max_score) / total_matches

        return top_intents[0], round(confidence, 2)