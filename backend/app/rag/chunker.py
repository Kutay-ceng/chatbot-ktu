import hashlib

from backend.app.rag.models import RagChunk


class SimpleChunker:

    def __init__(self, chunk_size=100, overlap=20):
        if chunk_size <= 0:
            raise ValueError("chunk_size 0'dan büyük olmalıdır.")
        if overlap >= chunk_size:
            raise ValueError(
                "overlap değeri, chunk_size'dan küçük olmalıdır. "
                "Aksi takdirde sonsuz döngü oluşur."
            )
        
        self.chunk_size = chunk_size
        self.overlap = overlap

    def _generate_chunk_id(self, doc_id, chunk_index, text):
        benzersiz_kelime = f"{doc_id}-chunk{chunk_index}-{text}"
        return hashlib.sha256(benzersiz_kelime.encode('utf-8')).hexdigest()

    def chunk(self, document):
        icerik = (
            getattr(document, "text", "") 
            if hasattr(document, "text") 
            else document.get("text", document.get("content", ""))
        )
        
        doc_id = (
            getattr(document, "id", "") 
            if hasattr(document, "id") 
            else document.get("id", document.get("doc_id", ""))
        )
        
        parcalar = []
        baslangic = 0
        
        parcalar = []
        baslangic = 0
        chunk_index = 0

        while baslangic < len(icerik):
            bitis = min(baslangic + self.chunk_size, len(icerik))
            kesilen_metin = icerik[baslangic:bitis]
            
            if not kesilen_metin.strip():
                baslangic += self.chunk_size - self.overlap
                continue

            chunk_id = self._generate_chunk_id(doc_id, chunk_index, kesilen_metin)
            content_hash = hashlib.sha256(kesilen_metin.encode('utf-8')).hexdigest()

            yeni_parca = RagChunk(
                id=chunk_id,               
                document_id=doc_id,
                text=kesilen_metin,
                start=baslangic,
                end=bitis,
                chunk_id=chunk_id,         
                content_hash=content_hash  
            )
            
            parcalar.append(yeni_parca)
            
            chunk_index += 1
            baslangic += self.chunk_size - self.overlap

        return parcalar

Chunker = SimpleChunker
