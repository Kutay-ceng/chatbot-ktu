import hashlib


class Dograyici:
    def __init__(self, parca_boyutu=50, kesisme=10):
        self.parca_boyutu = parca_boyutu
        self.kesisme = kesisme

    def barkod_uret(self, metin, belge_id):
        benzersiz_kelime = f"{belge_id}-{metin}"
        return hashlib.sha256(benzersiz_kelime.encode("utf-8")).hexdigest()

    def parcalara_bol(self, belge):
        icerik = belge.get("content", "")
        parcalar = []
        baslangic = 0
        while baslangic < len(icerik):
            bitis = baslangic + self.parca_boyutu
            kesilen_metin = icerik[baslangic:bitis]
            yeni_parca = {
                "doc_id": belge["doc_id"],
                "title": belge["title"],
                "source": belge["source"],
                "category": belge["category"],
                "chunk_text": kesilen_metin,
                "content_hash": self.barkod_uret(kesilen_metin, belge["doc_id"]),
                "embedding": None,  # Şimdilik boş bırakıyoruz
            }
            parcalar.append(yeni_parca)
            baslangic += self.parca_boyutu - self.kesisme

        return parcalar
