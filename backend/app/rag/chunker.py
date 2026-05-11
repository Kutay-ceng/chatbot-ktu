import hashlib


class Dograyici:
    def __init__(self, parca_boyutu=100, kesisme=20):
        if parca_boyutu <= 0:
            raise ValueError("Parça boyutu (chunk_size) 0'dan büyük olmalıdır.")
        if kesisme >= parca_boyutu:
            raise ValueError(
                "Kesişme (overlap) değeri, parça boyutundan küçük olmalıdır. "
                "Aksi takdirde sonsuz döngü oluşur."
            )
        
        self.parca_boyutu = parca_boyutu
        self.kesisme = kesisme

    def deterministik_chunk_id_uret(self, belge_id, chunk_index, metin):
        benzersiz_kelime = f"{belge_id}-chunk{chunk_index}-{metin}"
        return hashlib.sha256(benzersiz_kelime.encode('utf-8')).hexdigest()

    def parcalara_bol(self, belge):
        icerik = belge.get("content", "")
        parcalar = []
        baslangic = 0
        chunk_index = 0

        while baslangic < len(icerik):
            bitis = min(baslangic + self.parca_boyutu, len(icerik))
            kesilen_metin = icerik[baslangic:bitis]
            
            if not kesilen_metin.strip():
                baslangic += self.parca_boyutu - self.kesisme
                continue

            chunk_id = self.deterministik_chunk_id_uret(belge["doc_id"], chunk_index, kesilen_metin)

            yeni_parca = {
                "chunk_id": chunk_id,  
                "doc_id": belge["doc_id"],
                "title": belge["title"],
                "source": belge["source"],
                "category": belge["category"],
                "chunk_text": kesilen_metin,
                "chunk_index": chunk_index,
                "start_char": baslangic,
                "end_char": bitis,
                "chunk_size": self.parca_boyutu,
                "chunk_overlap": self.kesisme,
                "embedding": None  
            }
            
            parcalar.append(yeni_parca)
            
            chunk_index += 1
            baslangic += self.parca_boyutu - self.kesisme

        return parcalar
Chunker = Dograyici
SimpleChunker = Dograyici

 