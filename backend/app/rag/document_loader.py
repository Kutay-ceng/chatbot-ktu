import json
import os

def validate_document(doc):
    """Belgenin gerekli tüm alanlara sahip olup olmadığını kontrol eder."""
    required_fields = ["doc_id", "title", "source", "category", "content"]
    for field in required_fields:
        if field not in doc or not str(doc[field]).strip():
            raise ValueError(f"Geçersiz belge: '{field}' alanı eksik veya boş. Belge ID: {doc.get('doc_id', 'Bilinmiyor')}")
    return True

def belgeleri_yukle(dosya_yolu):
    """JSON veya JSONL dosyasından belgeleri okur ve doğrular."""
    if not os.path.exists(dosya_yolu):
        raise FileNotFoundError(f"Dosya bulunamadı: {dosya_yolu}")

    _, uzanti = os.path.splitext(dosya_yolu)
    uzanti = uzanti.lower()

    if uzanti == '.jsonl':
        with open(dosya_yolu, 'r', encoding='utf-8') as dosya:
            for satir_no, satir in enumerate(dosya, 1):
                satir = satir.strip()
                if satir:
                    try:
                        doc = json.loads(satir)
                        validate_document(doc)
                        yield doc
                    except json.JSONDecodeError:
                        raise ValueError(f"JSON çözme hatası. Dosya: {dosya_yolu}, Satır: {satir_no}")
    
    elif uzanti == '.json':
        with open(dosya_yolu, 'r', encoding='utf-8') as dosya:
            try:
                veriler = json.load(dosya)
                if not isinstance(veriler, list):
                    raise ValueError("JSON dosyası bir belge listesi (array) içermelidir.")
                
                for doc in veriler:
                    validate_document(doc)
                    yield doc
            except json.JSONDecodeError:
                raise ValueError(f"Geçersiz JSON formatı: {dosya_yolu}")
    else:
        raise ValueError(f"Desteklenmeyen dosya formatı: {uzanti}. Sadece .json ve .jsonl desteklenir.")