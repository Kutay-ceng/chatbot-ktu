# -*- coding: utf-8 -*-
import re


class TurkishTextPreprocessor:
    """Türkçe metinler için kural tabanlı ön işleme adımları."""
    
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
        # Unicode destekli noktalama temizliği
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
    """Durumsuz (stateless) niyet sınıflandırıcı (Genişletilmiş Scope & Confidence)."""
    
    INTENTS = {
        "courses": [
            "ders", "müfredat", "kredi", "akts", "sınav", "vize", "final", "ödev", "proje", 
            "quiz", "staj", "program", "büt", "bütünleme", "telafi", "mazeret",
            "geçme", "not", "çan", "harf", "ortalama", "gno", "ano", "transkript", 
            "devamsızlık", "yoklama", "kayıt", "seçmeli", "zorunlu", "çap", "yandal", 
            "yaz", "muaf", "mezuniyet", "diploma", "yatay", "dikey", "erasmus", 
            "farabi", "mevlana", "network", "olasılık", "istatistik", "fizik", "işaret", 
            "matematik", "database", "automata", "paralel", "algoritma", "microprocessor", 
            "numerical", "analysis", "grafik", "madencili", "programlama", "programming", 
            "web", "sinyal", "sistem", "devre", "software", "optimizasyon", "görüntü", 
            "tasarım", "bitirme"
        ],
        "academic_staff": [
            "hoca", "profesör", "akademisyen", "öğretim", "asistan", "danışman", "görevli", 
            "başkan", "doçent", "doktor", "dekan", "rektör", "kim", "görüşme", "müsait", 
            "hangi", "veriyor", "bekir", "murat", "cemal", "vasif", "güzin", "mustafa", 
            "tuğrul", "selen", "sedat", "hüseyin", "beste", "şeyma", "selçuk", "bahar", 
            "gül", "zafer", "ömer", "burak", "metehan", "samet", "seda", "muhammed", 
            "orhan", "batuhan", "büşra", "dizdaroğlu", "ekinci", "köse", "nabiyev", 
            "ulutaş", "çavdar", "ayas", "görmüş", "pehlivan", "üstübioğlu", "aykut", 
            "aymaz", "cevher", "hatipoğlu", "yılmaz", "tahaoğlu", "yavuz", "çakır", 
            "aydın", "bulut", "dinçer", "efendioğlu", "kılıç", "sivaz", "çimşit", 
            "özkellekci"
        ],
        "contact_info": [
            "iletişim", "telefon", "mail", "posta", "e-posta", "fax", "kep", "numara", 
            "santral", "dahili", "adres", "nerede", "ulaşım", "konum", "ofis", "oda", 
            "yol", "harita", "otobüs", "dolmuş", "durak"
        ],
        "general_info": [
            "üniversite", "kampüs", "yurt", "burs", "yemekhane", "kütüphane", "sağlık", 
            "mediko", "spor", "havuz", "ring", "etkinlik", "kulüp", "topluluk", "şenlik",
            "öğrenci", "işleri", "tarihçe", "obs", "bilgi", "sistemi", "takvim", 
            "akademik", "duyuru", "şifre", "belge"
        ]
    }

    @classmethod
    def predict(cls, text: str) -> tuple[str, float]:
        """(intent, confidence) tuple'ı döndürür."""
        if not text or not text.strip():
            return ("unknown", 0.0)

        tokens = TurkishTextPreprocessor.process(text)
        if not tokens:
            return ("unknown", 0.0)

        intent_scores = {intent: 0 for intent in cls.INTENTS.keys()}

        for token in tokens:
            for intent, keywords in cls.INTENTS.items():
                for kw in keywords:
                    if token.startswith(kw):
                        intent_scores[intent] += 1
                        break 
                        
        max_score = max(intent_scores.values())
        total_score = sum(intent_scores.values())
        
        # Hiçbir eşleşme yoksa
        if max_score == 0:
            return ("unknown", 0.0)
            
        # Eşitlik (Tie-break) Kontrolü
        en_yuksek_niyetler = [
            intent for intent, score in intent_scores.items() 
            if score == max_score
        ]
        
        # Kararsızlık durumu (Eşitlik)
        if len(en_yuksek_niyetler) > 1:
            return ("unknown", 0.0)
            
        # Güven Skoru (Confidence): En yüksek skorun, toplam skora oranı
        confidence = round(max_score / total_score, 2)
        
        return (en_yuksek_niyetler[0], confidence)


# --- İNTERAKTİF VE OTOMATİK TEST BÖLÜMÜ ---
if __name__ == "__main__":
    
    # Otomatik testler için önceden hazırlanmış soru havuzu
    TEST_SORULARI = [
        "Bilgisayar ağları dersi kaç AKTS?",
        "Automata theory geçme notu nedir?",
        "Vize ve final tarihleri açıklandı mı?",
        "Bekir hocanın ofisi nerede?",
        "Bölüm başkanı kimdir?",
        "Danışman hocamı nasıl öğrenebilirim?",
        "Öğrenci işlerinin telefon numarası nedir?",
        "Bana Ekinci'nin e-posta adresini yazar mısın?",
        "Okula ulaşım nasıl sağlanır?",
        "Üniversite kampüsü çok büyük mü?",
        "Yemekhanede bugün hangi menü var?",
        "Erasmus başvuruları ne zaman başlıyor?",
        "Bugün hava çok güzel.",           # unknown bekliyoruz
        "Ders hocasının telefonu ne?"      # eşitlikten unknown bekliyoruz
    ]

    print("-" * 60)
    print("Niyet Sınıflandırıcı Test Ortamı")
    print("-" * 60)

    while True:
        print("\n" + "="*30)
        print("ANA MENÜ")
        print("1. Otomatik Testleri Çalıştır (Batch Test)")
        print("2. Manuel Soru Gir (İnteraktif Mode)")
        print("3. Çıkış")
        print("="*30)
        
        secim = input("Seçiminiz (1/2/3): ").strip()

        if secim in ['3', 'q', 'çıkış', 'exit', 'quit']:
            print("Sistemden çıkılıyor. İyi çalışmalar!")
            break
            
        elif secim == '1':
            print("\n" + "-" * 40)
            print("OTOMATİK TESTLER BAŞLATILIYOR...")
            print("-" * 40)
            for i, soru in enumerate(TEST_SORULARI, 1):
                intent, confidence = IntentClassifier.predict(soru)
                
                print(f"Soru {i}: {soru}")
                if intent == "unknown":
                    print("  └─ Sonuç: unknown (Emin Değil)")
                else:
                    print(f"  └─ Sonuç: {intent} (Güven: %{int(confidence*100)})")
                print("-" * 40)
            print("Testler tamamlandı! Menüye dönülüyor...\n")

        elif secim == '2':
            print("\n(Manuel moda geçildi. Ana menüye dönmek için 'm' yazın)")
            while True:
                kullanici_sorusu = input("\nSoru sorun: ")
                
                if kullanici_sorusu.lower().strip() == 'm':
                    break
                    
                if not kullanici_sorusu.strip():
                    continue

                intent, confidence = IntentClassifier.predict(kullanici_sorusu)
                
                if intent == "unknown":
                    print("Tespit Edilen Niyet: unknown (Anlaşılamadı)")
                else:
                    print(f"Tespit Edilen Niyet: {intent}")
                    print(f"Güven Skoru: %{int(confidence * 100)} ({confidence})")
        else:
            print("Lütfen menüden geçerli bir numara (1, 2 veya 3) girin.")