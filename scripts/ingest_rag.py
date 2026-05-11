import sys
import os
from pymongo import MongoClient, UpdateOne

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.rag.document_loader import belgeleri_yukle
from backend.app.rag.chunker import Dograyici

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "rag_db"
COLLECTION_NAME = "chunks"

def veritabanina_kaydet(parcalar):
    if not parcalar:
        print("Kaydedilecek parça bulunamadı.")
        return

    print(f"\n--- Toplam {len(parcalar)} parça MongoDB'ye gönderiliyor ---")
    
    # MongoDB'ye bağlanıyoruz
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    operasyonlar = []
    for parca in parcalar:
        filtre = {"chunk_id": parca["chunk_id"]}
        
        guncelleme = {"$set": parca}
        
        operasyonlar.append(UpdateOne(filtre, guncelleme, upsert=True))

    if operasyonlar:
        sonuc = collection.bulk_write(operasyonlar)
        print(f"İşlem Tamamlandı! Yeni Eklenen: {sonuc.upserted_count}, Güncellenen: {sonuc.modified_count}")
        
    client.close()

def main():
    dosya_yolu = "data/ornek_veriler.jsonl" 
    
    try:
        dograyici = Dograyici(parca_boyutu=100, kesisme=20)
        tum_parcalar = []
        
        print(f"Belgeler okunuyor: {dosya_yolu}")
        belgeler = belgeleri_yukle(dosya_yolu)
        
        for belge in belgeler:
            kucuk_parcalar = dograyici.parcalara_bol(belge)
            tum_parcalar.extend(kucuk_parcalar)

        veritabanina_kaydet(tum_parcalar)
        
    except Exception as hata:
        print(f"İşlem sırasında bir hata oluştu: {hata}")

if __name__ == "__main__":
    main()
    