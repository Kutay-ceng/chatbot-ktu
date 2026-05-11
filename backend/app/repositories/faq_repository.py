from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def _faq_path() -> Path:
    """FAQ veri dosyasının yolunu bulur."""
    root = Path(__file__).resolve().parents[3]

    candidates = [
        root / "data" / "faq" / "faq.json",
        root / "data" / "faq.json",
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    raise FileNotFoundError("FAQ veri dosyası bulunamadı.")

@lru_cache(maxsize=1)
def _load_faq_entries() -> list[dict[str, str]]:
    """FAQ kayıtlarını doğrulayarak yükler."""
    from backend.app.services.faq_loader import load_faq

    return load_faq(_faq_path())

class FaqRepository:
    """FAQ veri erişim katmanı."""

    def get_all(self) -> list[dict[str, str]]:
        """Tüm FAQ kayıtlarını döndürür."""
        return _load_faq_entries()
