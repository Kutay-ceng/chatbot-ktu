import json


def belgeleri_yukle(dosya_yolu):
    with open(dosya_yolu, "r", encoding="utf-8") as dosya:
        for satir in dosya:
            satir = satir.strip()
            if satir:
                yield json.loads(satir)
