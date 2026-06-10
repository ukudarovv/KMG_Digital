# -*- coding: utf-8 -*-
"""E2E tests for improved conversational flow."""
import json
import sys
import urllib.request

BASE_URL = "http://localhost:8010/api/digital-buddy/ask"


def ask(question: str, language: str = "ru") -> dict:
    payload = json.dumps(
        {"employee_id": 1, "question": question, "language": language},
        ensure_ascii=False,
    ).encode("utf-8")
    request = urllib.request.Request(
        BASE_URL,
        data=payload,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    tests = [
        {
            "question": "Здравствуй",
            "language": "ru",
            "expect_mode": "chat",
            "expect_no_code": True,
            "expect_contains": "здравствуйте",
        },
        {
            "question": "Спасибо",
            "language": "ru",
            "expect_mode": "chat",
            "expect_no_code": True,
        },
        {
            "question": "Что такое конфликт интересов?",
            "language": "ru",
            "expect_mode": None,
            "expect_code": "KMG-VND-6677",
            "expect_contains": "конфликт",
        },
        {
            "question": "Сәлеметсіз бе",
            "language": "kk",
            "expect_mode": "chat",
            "expect_no_code": True,
        },
    ]

    failed = 0
    for test in tests:
        result = ask(test["question"], test.get("language", "ru"))
        ok = True
        reasons: list[str] = []

        if test.get("expect_mode"):
            if result.get("mode") != test["expect_mode"]:
                ok = False
                reasons.append(f"mode={result.get('mode')}")
        if test.get("expect_no_code") and result.get("document_code"):
            ok = False
            reasons.append(f"unexpected code={result.get('document_code')}")
        if test.get("expect_code") and result.get("document_code") != test["expect_code"]:
            ok = False
            reasons.append(f"code={result.get('document_code')}")
        if test.get("expect_contains"):
            needle = test["expect_contains"].lower()
            if needle not in (result.get("answer") or "").lower():
                ok = False
                reasons.append("answer mismatch")

        status = "PASS" if ok else "FAIL"
        print(f"{status}: [{test.get('language', 'ru')}] {test['question']}")
        print(f"  mode={result.get('mode')} code={result.get('document_code')}")
        print(f"  source={result.get('source')}")
        print(f"  answer={(result.get('answer') or '')[:180]}")
        if reasons:
            print(f"  reasons: {', '.join(reasons)}")
        print()
        if not ok:
            failed += 1

    print(f"=== {len(tests) - failed}/{len(tests)} passed ===")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
