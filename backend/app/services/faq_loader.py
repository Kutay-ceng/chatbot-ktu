import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

REQUIRED_FIELDS = {"question", "answer", "category", "source"}
NON_EMPTY_FIELDS = {"question", "answer"}

DEFAULT_FAQ_PATH = Path(__file__).resolve().parents[3] / "data" / "faq" / "faq.json"

class FaqLoadError(Exception):
    """ faq dosyasını yüklerken oluşan hatalar için """
def load_faq(file_path: str | Path | None = None) -> list[dict[str, str]]:
    path = Path(file_path) if file_path is not None else DEFAULT_FAQ_PATH

    if not path.exists():
        message = f"FAQ file not found: {path}"
        logger.error(message)
        raise FaqLoadError(message)

    try:
        with path.open("r", encoding="utf-8-sig") as faq_file:
            data = json.load(faq_file)
    except json.JSONDecodeError as exc:
        message = (
            f"Invalid FAQ JSON in '{path}': "
            f"line {exc.lineno}, column {exc.colno}."
        )
        logger.error(message)
        raise FaqLoadError(message) from exc
    except OSError as exc:
        message = f"Could not read FAQ file '{path}': {exc}"
        logger.error(message)
        raise FaqLoadError(message) from exc

    if not isinstance(data, list):
        message = "FAQ data must be a list of records."
        logger.error(message)
        raise FaqLoadError(message)

    return [_validate_record(record, index) for index, record in enumerate(data, start=1)]


def _validate_record(record: Any, index: int) -> dict[str, str]:
    if not isinstance(record, dict):
        raise FaqLoadError(f"FAQ record #{index} must be an object.")

    missing_fields = REQUIRED_FIELDS - set(record.keys())

    if missing_fields:
        fields = ", ".join(sorted(missing_fields))
        raise FaqLoadError(
            f"FAQ record #{index} is missing required field(s): {fields}."
        )

    validated_record: dict[str, str] = {}

    for field in REQUIRED_FIELDS:
        value = record[field]

        if not isinstance(value, str):
            raise FaqLoadError(
                f"FAQ record #{index} field '{field}' must be a string."
            )

        cleaned_value = value.strip()

        if field in NON_EMPTY_FIELDS and not cleaned_value:
            raise FaqLoadError(
                f"FAQ record #{index} field '{field}' must not be empty."
            )

        validated_record[field] = cleaned_value

    return validated_record