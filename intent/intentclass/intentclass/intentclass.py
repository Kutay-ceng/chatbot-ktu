from backend.app.nlp import IntentClassifier


def main() -> None:
    print("-" * 50)
    print("Niyet Siniflandirici Baslatildi!")
    print("Programi kapatmak icin 'q', 'cikis' veya 'exit' yazabilirsiniz.")
    print("-" * 50)

    while True:
        question = input("\nSoru sorun: ")
        if question.lower().strip() in ["q", "cikis", "exit", "quit"]:
            print("Sistemden cikiliyor. Iyi calismalar!")
            break

        if not question.strip():
            print("Lutfen bir soru girin.")
            continue

        result = IntentClassifier.predict(question)
        print(f"Tespit Edilen Niyet: {result}")


if __name__ == "__main__":
    main()
