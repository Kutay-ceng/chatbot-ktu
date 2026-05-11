import pytest
import json
from unittest.mock import patch, MagicMock
from pymongo import UpdateOne

from backend.app.rag.document_loader import belgeleri_yukle, validate_document
from backend.app.rag.chunker import Dograyici

from ingest_rag import veritabanina_kaydet 


def test_validate_document_eksik_alan():
    eksik_belge = {"doc_id": "1", "title": "Test"} 
    with pytest.raises(ValueError, match="Geçersiz belge"):
        validate_document(eksik_belge)

def test_json_ve_jsonl_yukleme(tmp_path):
    gecerli_belge = {"doc_id": "1", "title": "T", "source": "S", "category": "C", "content": "Metin"}
    
    jsonl_dosya = tmp_path / "test.jsonl"
    jsonl_dosya.write_text(json.dumps(gecerli_belge) + "\n")
    belgeler = list(belgeleri_yukle(str(jsonl_dosya)))
    assert len(belgeler) == 1
    assert belgeler[0]["doc_id"] == "1"

    # JSON Testi
    json_dosya = tmp_path / "test.json"
    json_dosya.write_text(json.dumps([gecerli_belge]))
    belgeler_json = list(belgeleri_yukle(str(json_dosya)))
    assert len(belgeler_json) == 1
    assert belgeler_json[0]["content"] == "Metin"

def test_chunker_parametre_validasyonu():
    with pytest.raises(ValueError, match="Kesişme .* küçük olmalıdır"):
        Dograyici(parca_boyutu=50, kesisme=50) 
    with pytest.raises(ValueError):
        Dograyici(parca_boyutu=0)

def test_deterministik_chunk_id():
    dograyici = Dograyici(parca_boyutu=100, kesisme=20)
    id1 = dograyici.deterministik_chunk_id_uret("doc1", 0, "test metni")
    id2 = dograyici.deterministik_chunk_id_uret("doc1", 0, "test metni")
    id3 = dograyici.deterministik_chunk_id_uret("doc1", 1, "test metni")
    
    assert id1 == id2 
    assert id1 != id3 

def test_metadata_ve_parcalama():
    dograyici = Dograyici(parca_boyutu=10, kesisme=2)
    ornek_belge = {
        "doc_id": "belge1", "title": "Test", "source": "local", 
        "category": "test", "content": "0123456789abcdef"
    }
    
    parcalar = dograyici.parcalara_bol(ornek_belge)
    
    assert len(parcalar) == 2
    # İlk parça (0'dan 10'a)
    assert parcalar[0]["chunk_text"] == "0123456789"
    assert parcalar[0]["start_char"] == 0
    assert parcalar[0]["end_char"] == 10
    
    assert parcalar[1]["chunk_text"] == "89abcdef"
    assert parcalar[1]["start_char"] == 8
    
    assert parcalar[0]["doc_id"] == "belge1"
    assert parcalar[0]["title"] == "Test"

@patch("ingest_rag.MongoClient") 
def test_veritabanina_kaydet_upsert(mock_mongo_client):
    mock_db = MagicMock()
    mock_collection = MagicMock()
    mock_mongo_client.return_value.__getitem__.return_value = mock_db
    mock_db.__getitem__.return_value = mock_collection
    
    ornek_parcalar = [{"chunk_id": "hash123", "chunk_text": "test"}]
    
    veritabanina_kaydet(ornek_parcalar)
    
    assert mock_collection.bulk_write.call_count == 1
    
    args, kwargs = mock_collection.bulk_write.call_args
    operasyonlar = args[0]
    
    assert len(operasyonlar) == 1
    assert isinstance(operasyonlar[0], UpdateOne)
    
    assert operasyonlar[0]._upsert is True
