import json
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def _faq_path() -> Path:
    """FAQ veri dosyasının yolunu bulur."""
    root = Path(__file__).resolve().parents[3]
    candidates = [root / "data" / "faq" / "faq.json", root / "data" / "faq.json"]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("FAQ veri dosyası bulunamadı.")


@lru_cache(maxsize=1)
def _load_faq_entries() -> list[dict]:
    """JSON dosyasını yükler."""
    with _faq_path().open("r", encoding="utf-8") as faq_file:
        raw_data = json.load(faq_file)
    if not isinstance(raw_data, list):
        raise ValueError("Geçersiz veri formatı.")
    return raw_data


class FaqRepository:
    """Veri erişim katmanı."""

    def get_all(self) -> list[dict]:
        """Tüm FAQ kayıtlarını döner."""
        return _load_faq_entries()