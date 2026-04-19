import json
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def _faq_path() -> Path:
    root = Path(__file__).resolve().parents[3]
    candidates = [root / "data" / "faq" / "faq.json", root / "data" / "faq.json"]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("FAQ data file was not found in expected locations.")


@lru_cache(maxsize=1)
def _load_faq_entries() -> list[dict]:
    with _faq_path().open("r", encoding="utf-8") as faq_file:
        raw_data = json.load(faq_file)

    if not isinstance(raw_data, list):
        raise ValueError("FAQ data is invalid; expected a list.")
    return raw_data


class FaqRepository:
    def list_entries(self) -> list[dict]:
        return _load_faq_entries()
