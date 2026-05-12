from unittest.mock import MagicMock

from scripts.ingest_rag import veritabanina_kaydet


def test_veritabanina_kaydet_upsert_mantigi():
    mock_collection = MagicMock()
    
    ornek_parcalar = [
        {
            "chunk_id": "chunk_abc123",
            "content_hash": "abc123",
            "content": "Bu bir test içeriğidir."
        }
    ]
    
    veritabanina_kaydet(ornek_parcalar, mock_collection)
    
    assert mock_collection.bulk_write.called
    
    cagri_listesi = mock_collection.bulk_write.call_args[0][0]
    ilk_islem = cagri_listesi[0]
    
    assert ilk_islem._upsert is True

    assert ilk_islem._filter == {"chunk_id": "chunk_abc123"}
    