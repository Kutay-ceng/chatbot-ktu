import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from backend.app.nlp import IntentClassifier
except ImportError:
    print("[HATA] backend.app.nlp.IntentClassifier bulunamadi!")
    sys.exit(1)


def run_evaluation():
    data_path = Path(__file__).resolve().parents[1] / "datasets" / "test_data.json"
    try:
        with data_path.open("r", encoding="utf-8") as f:
            test_cases = json.load(f)
    except FileNotFoundError:
        print(f"[HATA] {data_path} bulunamadi!")
        return

    total = len(test_cases)
    success_count = 0

    print(f" KTU Chatbot Testi Baslatildi ({total} Senaryo)")
    print("-" * 85)
    print(f"{'SORU':<40} | {'BEKLENEN':<15} | {'BOT NE DEDI':<15} | {'DURUM'}")
    print("-" * 85)

    for case in test_cases:
        question = case.get("text") or case.get("question")
        expected = case.get("intent") or case.get("category")

        # Sadece niyeti aliyoruz, skoru (_) atliyoruz
        result, _ = IntentClassifier.predict(question)

        if result == expected:
            success_count += 1
            status = "BASARILI"
        else:
            status = "HATALI"

        short_q = (question[:37] + "..") if len(question) > 37 else question
        print(f"{short_q:<40} | {expected:<15} | {result:<15} | {status}")

    accuracy = (success_count / total) * 100 if total > 0 else 0
    print("-" * 85)
    print(f" PERFORMANS RAPORU: %{accuracy:.2f}")
    print(f" Dogru Tahmin: {success_count} / {total}")
    print("-" * 85)

if __name__ == "__main__":
    run_evaluation()