import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from backend.app.services.chat_service import ChatService
except ImportError:
    print("[HATA] backend.app.services.chat_service.ChatService bulunamadi!")
    sys.exit(1)


def _shorten(text: str | None, max_length: int) -> str:
    if not text:
        return "-"
    if len(text) <= max_length:
        return text
    return f"{text[: max_length - 2]}.."


def _check_case(case: dict, response) -> list[str]:
    errors: list[str] = []

    expected_intent = case.get("intent") or case.get("category")
    if expected_intent and response.intent != expected_intent:
        errors.append(f"intent {expected_intent!r} yerine {response.intent!r}")

    expected_mode = case.get("expected_mode")
    if expected_mode and response.mode != expected_mode:
        errors.append(f"mode {expected_mode!r} yerine {response.mode!r}")

    if "expected_matched_question" in case:
        expected_match = case.get("expected_matched_question")
        if response.matched_question != expected_match:
            errors.append(
                f"match {expected_match!r} yerine {response.matched_question!r}"
            )

    return errors


def run_evaluation(data_path: Path | None = None) -> dict[str, int]:
    if data_path is None:
        data_path = Path(__file__).resolve().parents[1] / "datasets" / "test_data.json"

    try:
        with data_path.open("r", encoding="utf-8-sig") as f:
            test_cases = json.load(f)
    except FileNotFoundError:
        print(f"[HATA] {data_path} bulunamadi!")
        return {"total": 0, "passed": 0, "failed": 0}

    chat_service = ChatService()
    total = len(test_cases)
    passed = 0
    intent_success = 0
    mode_success = 0
    match_success = 0
    mode_checked = 0
    match_checked = 0

    print(f" KTU Chatbot E2E Testi Baslatildi ({total} Senaryo)")
    print("-" * 125)
    print(
        f"{'SORU':<38} | {'INTENT':<27} | {'MODE':<17} | {'FAQ MATCH':<10} | {'DURUM'}"
    )
    print("-" * 125)

    for index, case in enumerate(test_cases, start=1):
        question = case.get("text") or case.get("question")
        if not question:
            print(f"{'-':<38} | {'-':<27} | {'-':<17} | {'-':<10} | HATALI")
            continue

        response = chat_service.handle_message(question, session_id=f"eval-{index}")
        errors = _check_case(case, response)

        expected_intent = case.get("intent") or case.get("category") or "-"
        intent_pair = f"{expected_intent}->{response.intent}"
        if response.intent == expected_intent:
            intent_success += 1

        expected_mode = case.get("expected_mode")
        mode_pair = f"{expected_mode or '-'}->{response.mode}"
        if expected_mode:
            mode_checked += 1
            if response.mode == expected_mode:
                mode_success += 1

        match_status = "-"
        if "expected_matched_question" in case:
            match_checked += 1
            if response.matched_question == case.get("expected_matched_question"):
                match_success += 1
                match_status = "OK"
            else:
                match_status = "HATALI"

        if errors:
            status = "HATALI: " + "; ".join(errors)
        else:
            passed += 1
            status = "BASARILI"

        print(
            f"{_shorten(question, 38):<38} | "
            f"{_shorten(intent_pair, 27):<27} | "
            f"{_shorten(mode_pair, 17):<17} | "
            f"{match_status:<10} | "
            f"{_shorten(status, 45)}"
        )

    accuracy = (passed / total) * 100 if total > 0 else 0
    print("-" * 125)
    print(f" E2E PERFORMANS RAPORU: %{accuracy:.2f}")
    print(f" Basarili Senaryo: {passed} / {total}")
    print(f" Intent Dogrulugu: {intent_success} / {total}")
    print(f" Mode Dogrulugu: {mode_success} / {mode_checked}")
    print(f" FAQ Match Dogrulugu: {match_success} / {match_checked}")
    print("-" * 125)

    return {
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "intent_success": intent_success,
        "mode_success": mode_success,
        "match_success": match_success,
    }


if __name__ == "__main__":
    summary = run_evaluation()
    sys.exit(1 if summary["failed"] else 0)
