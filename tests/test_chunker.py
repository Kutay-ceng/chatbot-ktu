import os
import sys

from chunker import Dograyici

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_ayni_metne_ayni_barkod_uretilmeli():
    dograyici = Dograyici()
    ornek_belge = {
        "doc_id": "test-belgesi", 
        "title": "Test",
        "source": "local", 
        "category": "test", 
        "content": "Bu çok kısa bir test metnidir."
    }
    
    parcalar_birinci_deneme = dograyici.parcalara_bol(ornek_belge)
    parcalar_ikinci_deneme = dograyici.parcalara_bol(ornek_belge)
    
    assert parcalar_birinci_deneme[0]["content_hash"] == parcalar_ikinci_deneme[0]["content_hash"]
    
def test_etiketler_korunmali():
    dograyici = Dograyici(parca_boyutu=10)
    ornek_belge = {
        "doc_id": "test-belgesi-2", 
        "title": "Önemli Başlık", 
        "source": "url", 
        "category": "Kategori A", 
        "content": "Kısa metin"
    }
    parcalar = dograyici.parcalara_bol(ornek_belge)
    assert parcalar[0]["title"] == "Önemli Başlık"
    assert parcalar[0]["category"] == "Kategori A"