import json
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    from src.intentclass import IntentClassifier
except ImportError:
    print("❌ HATA: 'src/intentclass.py' dosyası bulunamadı!")
    sys.exit(1)

def run_evaluation():
    data_path = os.path.join(current_dir, 'test_data.json')
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            test_cases = json.load(f)
    except FileNotFoundError:
        print(f"❌ HATA: {data_path} bulunamadı!")
        return

    total = len(test_cases)
    success_count = 0

    print(f" KTÜ Chatbot Testi Başlatıldı ({total} Senaryo)")
    print("-" * 85)
    print(f"{'SORU':<40} | {'BEKLENEN':<15} | {'BOT NE DEDİ':<15} | {'DURUM'}")
    print("-" * 85)

    for case in test_cases:
        question = case.get('text') or case.get('question')
        expected = case.get('intent') or case.get('category')
        
        result = IntentClassifier.predict(question)

        if result == expected:
            success_count += 1
            status = "✅"
        else:
            status = "❌"

        short_q = (question[:37] + '..') if len(question) > 37 else question
        print(f"{short_q:<40} | {expected:<15} | {result:<15} | {status}")

    accuracy = (success_count / total) * 100 if total > 0 else 0
    print("-" * 85)
    print(f" PERFORMANS RAPORU: %{accuracy:.2f}")
    print(f" Doğru Tahmin: {success_count} / {total}")
    print("-" * 85)

if __name__ == "__main__":
    run_evaluation()