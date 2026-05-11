import json

import pytest

from backend.app.services.faq_loader import FaqLoadError, load_faq


def write_json(path, content) -> None:
    path.write_text(json.dumps(content, ensure_ascii=False), encoding="utf-8")


def test_load_faq_returns_valid_records(tmp_path):
    faq_file = tmp_path / "faq.json"
    write_json(
        faq_file,
        [
            {
                "question": "Bölüm başkanı kim?",
                "answer": "Bölüm Başkanı Prof. Dr. Mustafa Ulutaş.",
                "category": "Academic staff",
                "source": "https://www.ktu.edu.tr/bilgisayar/yonetim",
            }
        ],
    )

    result = load_faq(faq_file)
    assert len(result) == 1
    assert result[0]["question"] == "Bölüm başkanı kim?"
    assert result[0]["answer"] == "Bölüm Başkanı Prof. Dr. Mustafa Ulutaş."
    assert result[0]["category"] == "Academic staff"
    assert result[0]["source"] == "https://www.ktu.edu.tr/bilgisayar/yonetim"


def test_load_faq_raises_error_when_file_missing(tmp_path):
    missing_file = tmp_path / "missing.json"
    with pytest.raises(FaqLoadError, match="FAQ file not found"):
        load_faq(missing_file)


def test_load_faq_raises_error_for_invalid_json(tmp_path):
    faq_file = tmp_path / "faq.json"
    faq_file.write_text("{ invalid json", encoding="utf-8")
    with pytest.raises(FaqLoadError, match="Invalid FAQ JSON"):
        load_faq(faq_file)


def test_load_faq_raises_error_when_data_is_not_list(tmp_path):
    faq_file = tmp_path / "faq.json"
    write_json(
        faq_file,
        {
            "question": "Bölüm başkanı kim?",
            "answer": "Bölüm Başkanı Prof. Dr. Mustafa Ulutaş.",
            "category": "Academic staff",
            "source": "https://www.ktu.edu.tr/bilgisayar/yonetim",
        },
    )
    with pytest.raises(FaqLoadError, match="FAQ data must be a list"):
        load_faq(faq_file)


def test_load_faq_raises_error_for_missing_required_field(tmp_path):
    faq_file = tmp_path / "faq.json"
    write_json(
        faq_file,
        [
            {
                "question": "Bölüm başkanı kim?",
                "answer": "Bölüm Başkanı Prof. Dr. Mustafa Ulutaş.",
                "category": "Academic staff",
            }
        ],
    )
    with pytest.raises(FaqLoadError, match="missing required field"):
        load_faq(faq_file)


def test_load_faq_raises_error_for_wrong_field_type(tmp_path):
    faq_file = tmp_path / "faq.json"
    write_json(
        faq_file,
        [
            {
                "question": ["Bölüm başkanı kim?"],
                "answer": "Bölüm Başkanı Prof. Dr. Mustafa Ulutaş.",
                "category": "Academic staff",
                "source": "https://www.ktu.edu.tr/bilgisayar/yonetim",
            }
        ],
    )
    with pytest.raises(FaqLoadError, match="must be a string"):
        load_faq(faq_file)


def test_load_faq_raises_error_for_empty_question(tmp_path):
    faq_file = tmp_path / "faq.json"

    write_json(
        faq_file,
        [
            {
                "question": "   ",
                "answer": "Bölüm Başkanı Prof. Dr. Mustafa Ulutaş.",
                "category": "Academic staff",
                "source": "https://www.ktu.edu.tr/bilgisayar/yonetim",
            }
        ],
    )
    with pytest.raises(FaqLoadError, match="must not be empty"):
        load_faq(faq_file)


def test_load_faq_raises_error_for_empty_answer(tmp_path):
    faq_file = tmp_path / "faq.json"
    write_json(
        faq_file,
        [
            {
                "question": "Bölüm başkanı kim?",
                "answer": "",
                "category": "Academic staff",
                "source": "https://www.ktu.edu.tr/bilgisayar/yonetim",
            }
        ],
    )
    with pytest.raises(FaqLoadError, match="must not be empty"):
        load_faq(faq_file)
