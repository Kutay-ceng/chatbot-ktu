# -*- coding: utf-8 -*-
import re


class TurkishTextPreprocessor:
    """Türkçe metinler için kural tabanlı ön işleme (preprocessing) adımları."""
    
    @staticmethod
    def lowercase_tr(text: str) -> str:
        if not text:
            return ""
        text = text.replace("I", "ı").replace("İ", "i")
        return text.lower()

    @staticmethod
    def remove_punctuation(text: str) -> str:
        if not text:
            return ""
        # Unicode destekli noktalama temizliği (Harf, rakam ve boşluk olmayanları siler)
        temiz_metin = re.sub(r'[^\w\s]', ' ', text)
        return temiz_metin.replace('_', ' ')

    @staticmethod
    def tokenize(text: str) -> list[str]:
        return text.split()

    @classmethod
    def process(cls, text: str) -> list[str]:
        text = cls.lowercase_tr(text)
        text = cls.remove_punctuation(text)
        return cls.tokenize(text)


class IntentClassifier:
    """Durumsuz (stateless), sınıf seviyesinde çalışan modüler niyet sınıflandırıcı."""
    
    INTENTS = {
        "course_info": [
            "ders", "müfredat", "kredi", "akts", "sınav", "vize",
            "final", "ödev", "geçme", "not", "proje", "quiz",
            "staj", "takvim", "dönem",
        ],
        "academic_staff": [
            "hoca", "profesör", "akademisyen", "öğretim", "asistan",
            "danışman", "görevli", "başkan", "anabilim",
        ],
        "contact_info": [
            "iletişim", "telefon", "mail", "posta", "adres",
            "ulaşım", "konum", "fax", "ofis", "oda",
            "laboratuvar", "teknik", "sorumlu", "sekreter",
        ],
        "general_info": [
            "üniversite", "kampüs", "rektör", "tarihçe", "yurt",
            "burs", "yemekhane", "kütüphane",
            "program", "eğitim", "lisans", "hazırlık", "ingilizce", "unvan",
        ]
    }

    @classmethod
    def predict(cls, text: str) -> str:
        if not text or not text.strip():
            return "unknown"

        tokens = TurkishTextPreprocessor.process(text)
        if not tokens:
            return "unknown"

        intent_scores = {intent: 0 for intent in cls.INTENTS.keys()}

        for token in tokens:
            for intent, keywords in cls.INTENTS.items():
                for kw in keywords:
                    if token.startswith(kw):
                        intent_scores[intent] += 1
                        break 
                        
        max_score = max(intent_scores.values())
        if max_score == 0:
            return "unknown"
            
        # Eşitlik (Tie-break) Kontrolü
        en_yuksek_niyetler = [
            intent for intent, score in intent_scores.items() 
            if score == max_score
        ]
        
        # Eğer birden fazla niyet aynı (en yüksek) puanı aldıysa kararsız kal ve unknown dön
        if len(en_yuksek_niyetler) > 1:
            return "unknown"
            
        # Sadece net bir kazanan varsa onu döndür
        return en_yuksek_niyetler[0]


# --- İNTERAKTİF TEST BÖLÜMÜ ---
if __name__ == "__main__":
    print("-" * 50)
    print("Niyet Sınıflandırıcı Başlatıldı!")
    print("Programı kapatmak için 'q', 'çıkış' veya 'exit' yazabilirsiniz.")
    print("-" * 50)

    while True:
        kullanici_sorusu = input("\nSoru sorun: ")

        if kullanici_sorusu.lower().strip() in ['q', 'çıkış', 'exit', 'quit']:
            print("Sistemden çıkılıyor. İyi çalışmalar!")
            break

        if not kullanici_sorusu.strip():
            print("Lütfen bir soru girin.")
            continue

        sonuc = IntentClassifier.predict(kullanici_sorusu)
        print(f"Tespit Edilen Niyet: {sonuc}")
