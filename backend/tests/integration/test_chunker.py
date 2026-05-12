import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.app.rag.chunker import SimpleChunker


def test_ayni_metne_ayni_barkod_uretilmeli():
    chunker = SimpleChunker()
    metin = "Test metni"
    doc_id = "1"
    chunk_index = 0
    
    hash1 = chunker._generate_chunk_id(doc_id, chunk_index, metin)
    hash2 = chunker._generate_chunk_id(doc_id, chunk_index, metin)
    
    assert hash1 == hash2