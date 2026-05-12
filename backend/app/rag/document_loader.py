import json
import os

from backend.app.rag.models import RagDocument, RagSource


def validate_document(doc):
    """Belgenin gerekli tüm alanlara sahip olup olmadığını kontrol eder."""
    required_fields = ["doc_id", "title", "source", "category", "content"]
    for field in required_fields:
        if field not in doc or not str(doc[field]).strip():
            raise ValueError(
                f"Geçersiz belge: '{field}' alanı eksik veya boş. "
                f"Belge ID: {doc.get('doc_id', 'Bilinmiyor')}"
            )
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
                        raise ValueError(
                            f"JSON çözme hatası. Dosya: {dosya_yolu}, "
                            f"Satır: {satir_no}"
                        )
    
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
        raise ValueError(
            f"Desteklenmeyen dosya formatı: {uzanti}. Sadece .json ve .jsonl desteklenir."
        )

class SimpleDocumentLoader:
    """Eski testlerle ve yeni dosya okuma sistemiyle uyumlu Document Loader"""
    
    def __init__(self, entries=None, file_path=None):
        self.entries = entries
        self.file_path = file_path

    def load(self):
        raw_docs = []
        
        if self.entries is not None:
            raw_docs = self.entries
        elif self.file_path is not None:
            raw_docs = list(belgeleri_yukle(self.file_path))

        documents = []
        for item in raw_docs:
            doc_id = item.get("id") or item.get("doc_id") or "unknown"
            title = item.get("title", "")
            text = item.get("text") or item.get("content") or ""
            
            source_obj = None
            source_data = item.get("source")
            
            if isinstance(source_data, dict):
                source_obj = RagSource(
                    title=source_data.get("title", ""),
                    url=source_data.get("url", ""),
                    source_type=source_data.get("type", source_data.get("source_type", ""))
                )
            doc = RagDocument(
                id=doc_id,
                title=title,
                text=text,
                source=source_obj
            )
            documents.append(doc)

        return documents

DocumentLoader = SimpleDocumentLoader
