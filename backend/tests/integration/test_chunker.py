import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from chunker import Dograyici


def test_ayni_metne_ayni_barkod_uretilmeli():
    dograyici = Dograyici()
    metin = "Test metni"
    belge = {"doc_id": "1"}
    
    hash1 = dograyici.barkod_uret(metin, belge["doc_id"])
    hash2 = dograyici.barkod_uret(metin, belge["doc_id"])
    
    assert hash1 == hash2