# chatbot-ktu

Karadeniz Teknik Üniversitesi (KTÜ) Bilgisayar Mühendisliği bölümü için geliştirilen soru-cevap odaklı bir chatbot projesidir.

Bu proje, öğrencilerin bölümle ilgili sıkça sorulan sorulara hızlı ve doğru cevaplar alabilmesini amaçlamaktadır.

---

# Proje Geliştiricileri

- Muhammet Doğukan Bingöl — https://github.com/ProfTR55  
- Kutay Keleş — https://github.com/Kutay-ceng  
- Ahmet Taha Dinç — https://github.com/moti-maze  
- Onur Karaahmet — https://github.com/honorzilla  
- Ataberk Güneş — https://github.com/ataberkgunes  

---

# Projenin Amacı

- KTÜ Bilgisayar Mühendisliği öğrencileri için bilgilendirici bir chatbot geliştirmek
- Bölüm, dersler, akademik kadro ve genel bilgiler hakkında otomatik cevaplar sunmak
- NLP (Doğal Dil İşleme) tekniklerini uygulamalı olarak kullanmak
- Doğal dil işleme teknikleri ile metin sınıflandırma ve bilgi çıkarımı gerçekleştirmek
- Makine öğrenmesi tabanlı bir niyet (intent) sınıflandırma modeli geliştirmek
- Bölüme ait yapılandırılmış veri kaynaklarını chatbot sistemine entegre etmek
- Sistem doğruluk oranını ölçmek için test veri setleri oluşturmak
- Kullanıcı geri bildirimleri doğrultusunda modeli iyileştirmek

---

# Öncül Gereksinim Analizi

## 1. Fonksiyonel Gereksinimler

### FR1 – Soru Alma
- Sistem kullanıcıdan metin tabanlı soru alabilmelidir
- Türkçe karakter desteği olmalıdır

### FR2 – Soru Analizi
- Girilen soru NLP teknikleri ile analiz edilmelidir
- Anahtar kelime veya intent (niyet) tespiti yapılmalıdır
- RAG mimarisi ile çalışmalıdır

### FR3 – Cevap Üretme
- Sistem analiz edilen soruya uygun cevap verebilmelidir
- Sık sorulan sorular için hazır cevaplar bulunmalıdır
- Sohbet bağlamından kopulmamalıdır
- Hallusinasyonlardan kaçınılmalıdır

### FR4 – Bölüm Bilgileri Sunma
Sistem aşağıdaki bilgileri sağlayabilmelidir:

- Ders bilgileri
- Akademik kadro
- İletişim bilgileri
- Kullanıcının sohbet bağlamında temel bilgiler

### FR5 – Hatalı Girdi Yönetimi
- Anlaşılamayan sorular için uygun uyarı mesajı gösterilmelidir
- Kullanıcıya alternatif öneriler sunulmalıdır

### FR6 – Güncellenebilir Veri Yapısı
- Veri tabanı güncellenebilir olmalıdır
- Yeni soru-cevap eklenebilmelidir

---

## 2. Fonksiyonel Olmayan Gereksinimler

### NFR1 – Performans
- Sistem en fazla **2–3 saniye** içinde cevap vermelidir

### NFR2 – Kullanılabilirlik
- Arayüz sade ve kullanıcı dostu olmalıdır
- Mobil ve masaüstü uyumlu olmalıdır

### NFR3 – Güvenlik
- Kullanıcı girdileri kontrol edilmelidir
- SQL Injection gibi saldırılara karşı önlem alınmalıdır
- Kullanıcı bilgileri maskelenerek saklanmalıdır

### NFR4 – Ölçeklenebilirlik
- Sistem ileride diğer bölümler için genişletilebilir olmalıdır

### NFR5 – Bakım Kolaylığı
- Kod modüler yapıda olmalıdır
- GitHub üzerinden versiyon kontrolü yapılmalıdır

---

## 3. Teknik Gereksinimler

- Python programlama dili
- NLP kütüphaneleri (NLTK, spaCy vb.)
- Pandas, NumPy
- Git & GitHub ile versiyon kontrolü
- Web framework: **Flask** veya **FastAPI**

---

## 4. Kısıtlar

- Proje belirli bir süre içinde tamamlanmalıdır
- Akademik dönem takvimi zaman kısıtı oluşturmaktadır
- Sistem yalnızca **KTÜ Bilgisayar Mühendisliği** bölümüne yönelik olacaktır
---

# API Kontratı ve Entegrasyon

Frontend, LLM ve RAG ekiplerinin aynı standartta çalışabilmesi için `/chat` uç noktasının (endpoint) girdi ve çıktı formatları aşağıda tanımlanmıştır. Frontend ekibi geliştirme aşamasında bu yapıya bakarak sahte (mock) yanıtlar hazırlayabilir.

## 1. İstek (Request) Formatı

İstemci (Frontend) tarafından `/chat` uç noktasına yapılacak `POST` isteğinin JSON gövdesi aşağıdaki gibidir:

```json
POST /chat
{
  "message": "Kütüphane hafta sonu açık mı?",
  "session_id": "req-12345" 
}
```

## 2. Yanıt (Response) Modelleri ve Parametreler

API'den dönen yanıtta, sistemin arka planda hangi mekanizmayı çalıştırdığını belirtmek için `mode` alanı, yanıtın dayanağını göstermek için ise `sources` alanı kullanılır.

### `mode` Değerleri

- **`faq`**: Kullanıcının amacı (intent) sınıflandırıcı tarafından net bir şekilde tespit edildiğinde ve SSS veri setinden statik bir metin döndüğünde kullanılır.
- **`fallback`**: Sistem soruyu anlayamadığında, niyet eşleşmediğinde veya beklenen bir veri bulunamadığında dönen standart yedek (kurtarma) yanıtıdır.
- **`llm`**: Herhangi bir dış belge aranmaksızın doğrudan model tarafından üretilmiş jenerik bir yanıt dönüldüğünde kullanılacaktır.
- **`rag`**: Veri tabanından veya belgelerden arama yapılıp (Retrieval), bu bağlamın LLM'e verilmesiyle üretilen dinamik yanıtlar için kullanılacaktır.

### `sources` Alanı

- Verilen yanıtın dayandığı referansları Frontend'e iletmek için kullanılır.
- SSS (`faq`) modunda web sayfası linkleri veya formlar, `rag` modunda ise alıntı yapılan doküman isimleri yer alır.
- Bilgi kaynağı yoksa (örneğin `fallback` modunda) boş bir dizi (`[]`) olarak dönmelidir.

## 3. Yanıt (Response) Örnekleri

### Örnek A: SSS (FAQ) Yanıtı
Bilinen bir niyet (intent) yakalandığında döner.

```json
{
  "answer": "Faık Ahmet Barutçu Kütüphanesi hafta sonları 09:00 - 17:00 saatleri arasında hizmet vermektedir. Vize ve final dönemlerinde bu saatler 7/24 olacak şekilde güncellenmektedir.",
  "mode": "faq",
  "sources": [
    {
      "title": "Kütüphane Çalışma Saatleri",
      "url": "https://www.ktu.edu.tr/kutuphane"
    }
  ]
}
```

### Örnek B: Geri Dönüş (Fallback) Yanıtı
Soru anlaşılamadığında veya sistem yanıt üretemediğinde döner.

```json
{
  "answer": "Üzgünüm, sorunuzu tam olarak anlayamadım veya şu anda bu bilgiye ulaşamıyorum. Lütfen sorunuzu farklı kelimelerle tekrar ifade etmeyi deneyin.",
  "mode": "fallback",
  "sources": []
}
```
---

# Risk Yönetimi

## Risk 1 — Chatbot’un yanlış / eksik cevap vermesi

**Açıklama**

NLP tabanlı sistemler bazen soruları yanlış yorumlayabilir veya eksik bilgi verebilir.

**Önlemler**

- Sık sorulan sorular için hazır soru-cevap veri seti oluşturulacak
- Test aşamasında gerçek öğrenci soruları toplanacak
- Sürekli güncellenebilir bilgi tabanı kurulacak
- Veri seti düzenli olarak kontrol edilecek

---

## Risk 2 — NLP performansının düşük olması

**Açıklama**

Türkçe doğal dil işleme İngilizceye göre daha zordur.

**Önlemler**

- Türkçe tokenizasyon yöntemleri araştırılacak
- Model küçük başlayıp iteratif olarak geliştirilecek
- Rule-based + NLP hibrit sistem değerlendirilecek

---

## Risk 3 — Sistem entegrasyon sorunları

**Açıklama**

Backend, chatbot motoru ve veri tabanı entegrasyonunda sorun yaşanabilir.

**Önlemler**

- Modüler mimari kullanılacak
- Git/GitHub üzerinden düzenli entegrasyon yapılacak
- Haftalık entegrasyon testleri gerçekleştirilecek

---

## Risk 4 — Güncel bilgiye erişememe

**Açıklama**

Bölüm bilgileri zamanla değişebilir.

**Önlemler**

- Bilgiler resmi KTÜ CENG web sitesinden alınacak
- Veri tabanı güncellenebilir şekilde tasarlanacak
- Yönetici paneli eklenmesi planlanacak

---

## Risk 5 — Yetersiz soru veri seti

**Açıklama**

Chatbot eğitimi için yeterli soru bulunamayabilir.

**Önlemler**

- Öğrencilerden örnek sorular toplanacak
- Manuel soru üretimi yapılacak
- KTÜ CENG web sitesindeki SSS incelenecek

---

# Proje Grubu İş Paylaşımı

## Gereksinim Analizi Raporu
**Lider:** Onur Karaahmet

Sorumluluklar:

- Fonksiyonel ve fonksiyonel olmayan gereksinimlerin belirlenmesi
- Sistem kısıtlarının tanımlanması
- Riskleri azaltmaya yönelik gereksinim çerçevesi oluşturmak

---

## Mimari Tasarım Raporu
**Lider:** Kutay Keleş

Sorumluluklar:

- Sistem mimarisinin tasarlanması
- Modül yapısının belirlenmesi
- Veri akış diyagramlarının hazırlanması
- Teknik altyapı kararlarının dokümantasyonu

---

## Proje Sonuç Raporu
**Lider:** Ahmet Taha Dinç

Sorumluluklar:

- Proje çıktılarının değerlendirilmesi
- Performans analizleri
- Elde edilen sonuçların raporlanması
- Genel proje değerlendirmesi

---

## Git Repo Değerlendirmesi
**Lider:** Muhammet Doğukan Bingöl

Sorumluluklar:

- GitHub repo düzeni
- Versiyon kontrol yönetimi
- Commit düzeninin takibi
- Branch yönetimi ve entegrasyon kontrolü

---

## Sunum
**Lider:** Ataberk Güneş

Sorumluluklar:

- Proje sunumunun hazırlanması
- Sunum slaytlarının tasarlanması
- Demo senaryosunun hazırlanması
- Sunum koordinasyonu

---

## Genel İlke

Her lider kendi bölümünden sorumlu olmakla birlikte proje ekip çalışması ile yürütülecektir. Haftalık toplantılar ile ilerleme kontrolü sağlanacaktır.

---

# Proje Planı Kaynakları

## Teknik Kaynaklar

- Python Resmi Dokümantasyonu — https://docs.python.org/3/
- NLTK — https://www.nltk.org/
- spaCy — https://spacy.io/
- Pandas — https://pandas.pydata.org/docs/
- NumPy — https://numpy.org/doc/
- Flask / FastAPI Dokümantasyonu

---

## Versiyon Kontrol

- Git Dokümantasyonu — https://git-scm.com/docs
- GitHub Dokümantasyonu — https://docs.github.com/

---

## Yazılım Mühendisliği Kaynakları

- IEEE Software Engineering Standards
- Pressman – *Software Engineering: A Practitioner’s Approach*
- Agile Yazılım Geliştirme Yaklaşımı

---

## Veri Kaynakları

- Karadeniz Teknik Üniversitesi Resmi Web Sitesi
- KTÜ Bilgisayar Mühendisliği Bölüm Sayfası
- Öğrencilerden toplanan sık sorulan sorular

---

## Akademik Kaynaklar

- NLP üzerine akademik makaleler
- Türkçe NLP çalışmaları
- https://scholar.google.com/
