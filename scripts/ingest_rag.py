from pymongo import UpdateOne


def veritabanina_kaydet(parcalar, collection):
    if not parcalar:
        print("Kaydedilecek parça bulunamadı.")
        return None

    operasyonlar = []
    for parca in parcalar:
        operasyonlar.append(
            UpdateOne(
                {"chunk_id": parca["chunk_id"]},  
                {"$set": parca},     
                upsert=True                      
            )
        )
    
    try:
        sonuc = collection.bulk_write(operasyonlar)
        print(
            f"İşlem Tamamlandı! Yeni: {sonuc.upserted_count}, "
            f"Güncellenen: {sonuc.modified_count}"
        )
        return sonuc
    except Exception as e:
        print(f"Veritabanı kayıt hatası: {e}")
        return None
    