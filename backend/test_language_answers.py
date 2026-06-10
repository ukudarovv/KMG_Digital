# -*- coding: utf-8 -*-
import json
import urllib.request

KK_CHARS = set("әғқңөұүһі")


def ask(question: str, language: str) -> dict:
    payload = json.dumps(
        {"employee_id": 1, "question": question, "language": language},
        ensure_ascii=False,
    ).encode("utf-8")
    request = urllib.request.Request(
        "http://localhost:8010/api/digital-buddy/ask",
        data=payload,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))


def has_kazakh(text: str) -> bool:
    lower = text.lower()
    return any(char in lower for char in KK_CHARS)


def main() -> None:
    tests = [
        ("ru", "Можно ли передавать проксим-карту другим лицам?"),
        ("ru", "Что такое конфликт интересов?"),
        ("kk", "Проксим-картаны басқа адамдарға беруге бола ма?"),
        ("kk", "Мүдде конфликті деген не?"),
    ]

    for lang, question in tests:
        result = ask(question, lang)
        answer = result.get("answer", "")
        lang_ok = has_kazakh(answer) if lang == "kk" else not has_kazakh(answer)
        print(f"[{lang}] response_lang={result.get('language')} mode={result.get('mode')}")
        print(f"     code={result.get('document_code')} language_ok={lang_ok}")
        print(f"Q: {question}")
        print(f"A: {answer[:350]}")
        print("---")


if __name__ == "__main__":
    main()
