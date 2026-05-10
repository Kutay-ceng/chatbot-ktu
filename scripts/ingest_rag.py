import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from document_loader import belgeleri_yukle
from chunker import Dograyici

def veritabanina_kaydet(parcalar):
    print(f"\n--- Toplam {len(parcalar)} parça veritabanına gönderiliyor ---")
    for parca in parcalar:
        print(
            f"Barkod: {parca['content_hash'][:10]}... | "
            f"Belge: {parca['doc_id']} | "
            f"Metin: {parca['chunk_text'][:20]}..."
        )

def main():
    dosya_yolu = "data/ornek_veriler.jsonl"
    dograyici = Dograyici(parca_boyutu=100, kesisme=20)
    tum_parcalar = []
    print("Belgeler okunuyor...")
    belgeler = belgeleri_yukle(dosya_yolu)
    for belge in belgeler:
        kucuk_parcalar = dograyici.parcalara_bol(belge)
        tum_parcalar.extend(kucuk_parcalar)
    veritabanina_kaydet(tum_parcalar)

if __name__ == "__main__":
    main()