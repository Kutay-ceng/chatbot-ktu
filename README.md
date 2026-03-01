# chatbot-ktu
Karadeniz Teknik Üniversitesi (KTÜ) Bilgisayar Mühendisliği bölümü için geliştirilen,
soru-cevap odaklı bir chatbot projesidir.

Bu proje, öğrencilerin bölümle ilgili sıkça sorulan sorulara hızlı ve doğru cevaplar
alabilmesini amaçlamaktadır.

## Proje Geliştiricileri
- Muhammet Doğukan Bingöl (https://github.com/ProfTR55)
- Kutay Keleş (https://github.com/Kutay-ceng)
- Ahmet Taha Dinç (https://github.com/moti-maze)
- Onur Karaahmet (https://github.com/honorzilla)
- Ataberk Güneş (https://github.com/ataberkgunes)

## Projenin Amacı
•	KTÜ Bilgisayar Mühendisliği öğrencileri için bilgilendirici bir chatbot geliştirmek,
•	Bölüm, dersler, akademik kadro ve genel bilgiler hakkında otomatik cevaplar sunmak,
•	NLP (Doğal Dil İşleme) tekniklerini uygulamalı olarak kullanmak.
•	 Doğal dil işleme (NLP) teknikleri ile metin sınıflandırma ve bilgi çıkarımı gerçekleştirmek,
•	 Makine öğrenmesi tabanlı bir niyet sınıflandırma modeli geliştirmek,
•	 Bölüme ait yapılandırılmış veri kaynaklarını chatbot sistemine entegre etmek,
•	 Sistem doğruluk oranını ölçmek için test veri setleri oluşturmak,
•	 Kullanıcı geri bildirimleri doğrultusunda modeli iyileştirmek.

## Öncül Gereksinim Analizi
1) Fonksiyonel Gereksinimler
FR1 – Soru Alma
•	Sistem kullanıcıdan metin tabanlı soru alabilmelidir.
•	Türkçe karakter desteği olmalıdır.
FR2 – Soru Analizi
•	Girilen soru NLP teknikleri ile analiz edilmelidir.
•	Anahtar kelime veya intent (niyet) tespiti yapılmalıdır.
•	RAG mimarisiyle beraber çalışmalıdır.
FR3 – Cevap Üretme
•	Sistem analiz edilen soruya uygun cevap verebilmelidir.
•	Sık sorulan sorular için hazır cevaplar bulunmalıdır.
•	Sohbet bağlamından kopulmamalıdır.
•	Halisünasyonlardan kaçınılmalıdır.
FR4 – Bölüm Bilgileri Sunma
•	Ders bilgileri
•	Akademik kadro
•	İletişim bilgileri
•	Kullanıcının sohbet bağlamında temel bilgileri
FR5 – Hatalı Girdi Yönetimi
•	Anlaşılamayan sorular için uygun uyarı mesajı gösterilmelidir.
•	Kullanıcıya alternatif öneriler sunulmalıdır.
FR6 – Güncellenebilir Veri Yapısı
•	Veri tabanı güncellenebilir olmalıdır.
•	Yeni soru-cevap eklenebilmelidir.

2) Fonksiyonel Olmayan Gereksinimler
NFR1 – Performans
•	Sistem en fazla 2–3 saniye içinde cevap vermelidir.
NFR2 – Kullanılabilirlik
•	Arayüz sade ve kullanıcı dostu olmalıdır.
•	Mobil ve masaüstü uyumlu olmalıdır.
NFR3 – Güvenlik
•	Kullanıcı girdileri kontrol edilmelidir.
•	SQL injection gibi saldırılara karşı önlem alınmalıdır.
•	Her kullanıcı bilgisi maskelendirilerek saklanmalıdır.
NFR4 – Ölçeklenebilirlik
•	Sistem ileride diğer bölümler için de genişletilebilir olmalıdır.
NFR5 – Bakım Kolaylığı
•	Kod modüler yapıda olmalıdır.
•	GitHub üzerinden versiyon kontrolü yapılmalıdır.

3) Teknik Gereksinimler
•	Python programlama dili kullanılacaktır.
•	İhtiyaçalara yönelik Pythton kütüphanesi (örnek: NLTK, Pandas veya benzeri)
•	Git & GitHub ile versiyon kontrolü
•	Web framework: Flask / FastAPI

4) Kısıtlar
•	Proje belirli bir süre içinde tamamlanmalıdır.
•	Akademik dönem takvimi zaman kısıtı oluşturmaktadır.
•	Sistem yalnızca KTÜ Bilgisayar Mühendisliği bölümüne yönelik olacaktır.

## Risk Yönetimi
Risk 1 — Chatbot’un yanlış / eksik cevap vermesi
Açıklama:
NLP tabanlı sistemler bazen soruları yanlış yorumlayabilir veya eksik bilgi verebilir.
Önlemler
•	Sık sorulan sorular için hazır soru-cevap veri seti oluşturulacak
•	Test aşamasında gerçek öğrenci soruları toplanacak
•	Sürekli güncellenebilir bilgi tabanı kurulacak
•	Veri setinin kontrol edilecek

Risk 2 — NLP performansının düşük olması
Açıklama:
Türkçe doğal dil işleme İngilizceye göre daha zordur.
Önlemler
•	Tokenizasyon işlemi için Türkçeleştirilme araştırılacak
•	Model küçük başlayıp iteratif geliştirilecek
•	Alternatif yaklaşım: Rule-based + NLP hibrit sistem

Risk 3 — Sistem entegrasyon sorunları
Açıklama:
Backend, chatbot motoru ve veri tabanı entegrasyonunda sorun yaşanabilir.
Önlemler
•	Modüler mimari kullanılacak
•	Git-GitHub üzerinden düzenli entegrasyon yapılacak
•	Haftalık entegrasyon testleri yapılacak

Risk 4 — Güncel bilgiye erişememe
Açıklama:
Bölüm bilgileri değişebilir (dersler, akademik kadro vb.)
Önlemler
•	Bilgiler resmi KTÜ-Ceng web sitesinden alınacak
•	Veri tabanı güncellenebilir şekilde tasarlanacak
•	Yönetici paneli eklenmesi planlanacak

Risk 5 — Yetersiz soru veri seti
Açıklama:
Chatbot eğitimi için yeterli soru bulunamayabilir.
Önlemler
•	Öğrencilerden örnek sorular toplanacak
•	Manuel soru üretimi yapılacak
•	KTÜ-Ceng web sitesindeki SSS’a bakılacak

## Proje Grubu İş Paylaşımı
Görev Dağılımı
Mimari Tasarım Raporu
Lider: Kutay Keleş
Sorumluluklar:
•	Sistem mimarisinin tasarlanması
•	Modül yapısının belirlenmesi
•	Veri akış diyagramlarının hazırlanması
•	Teknik altyapı kararlarının dokümantasyonu

Proje Sonuç Raporu
Lider: Ahmet Taha Dinç
Sorumluluklar:
•	Proje çıktılarının değerlendirilmesi
•	Performans analizleri
•	Elde edilen sonuçların raporlanması
•	Genel proje değerlendirme bölümü

Gereksinim Analizi Raporu
Lider: Onur Karaahmet
Sorumluluklar:
•	Fonksiyonel ve fonksiyonel olmayan gereksinimlerin belirlenmesi
•	Sistem kısıtlarının tanımlanması
•	Riskleri azaltmaya yönelik gereksinim çerçevesinin oluşturulması

Git Repo Değerlendirmesi
Lider: Muhammet Doğukan Bingöl
Sorumluluklar:
•	GitHub repo düzeni
•	Versiyon kontrol yönetimi
•	Commit düzeninin takibi
•	Branch yönetimi ve entegrasyon kontrolü

Sunum
Lider: Ataberk Güneş
Sorumluluklar:
•	Proje sunumunun hazırlanması
•	Sunum slaytlarının tasarlanması
•	Demo senaryosunun hazırlanması
•	Sunum koordinasyonu

Genel İlke
Her lider kendi bölümünden sorumlu olmakla birlikte, proje ekip çalışması ile yürütülecektir. Haftalık toplantılarla ilerleme kontrolü sağlanacaktır.

## Proje Planı Kaynakları
Teknik Kaynaklar
•	Python Resmi Dokümantasyonu (https://docs.python.org/3/)
•	NLTK (Natural Language Toolkit) Dokümantasyonu (https://www.nltk.org/)
•	spaCy NLP Dokümantasyonu (https://spacy.io/)
•	Flask / FastAPI Dokümantasyonu 
•	Pandas (https://pandas.pydata.org/docs/)
•	Numpy (https://numpy.org/doc/)
•	Zamanla Kaynaklarda Güncelleme Yapılacaktır

Versiyon Kontrol ve Yazılım Geliştirme
•	Git Resmi Dokümantasyonu (https://git-scm.com/docs)
•	GitHub Dokümantasyonu (https://docs.github.com/)

Proje Yönetimi ve Yazılım Mühendisliği Kaynakları
•	IEEE Software Engineering Standards
•	Pressman, R. (Software Engineering: A Practitioner’s Approach)
•	Agile Yazılım Geliştirme Yaklaşımı Dokümanları

Veri Kaynakları
•	Karadeniz Teknik Üniversitesi (KTÜ) Resmi Web Sitesi
•	KTÜ Bilgisayar Mühendisliği Bölüm Sayfası
•	Öğrencilerden toplanan sık sorulan sorular (SSS)

Akademik ve Teknik Referanslar
•	Doğal Dil İşleme (NLP) üzerine akademik makaleler
•	Türkçe NLP çalışmaları ve açık kaynak projeler
•	https://scholar.google.com/ Üzerinden İhtiyaçlar Üzerine Alınabilecek Referanslar

---
