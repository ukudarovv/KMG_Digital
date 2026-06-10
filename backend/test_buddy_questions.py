# -*- coding: utf-8 -*-
"""E2E tests: questions phrased from VND/Docs instructions."""
import json
import sys
import urllib.request

BASE_URL = "http://localhost:8010/api/digital-buddy"

TESTS = [
    {
        "question": "Можно ли передавать проксим-карту другим лицам?",
        "expected_code": "KMG-PR-1186",
    },
    {
        "question": "Что должен сделать сотрудник при потере карты и пропуска?",
        "expected_code": "KMG-PR-1186",
    },
    {
        "question": "Что такое конфликт интересов по инструкции противодействия коррупции?",
        "expected_code": "KMG-VND-6677",
        "expected_section_contains": "5.3.1",
    },
    {
        "question": "Как работник должен действовать при предложении взятки?",
        "expected_code": "KMG-VND-6677",
        "expected_section_contains": "5.1.5",
    },
    {
        "question": "Как сообщить о коррупционных правонарушениях через линию доверия?",
        "expected_code": "KMG-VND-6677",
        "expected_section_contains": "доверия",
    },
    {
        "question": "Какие требования к деловой переписке в кодексе этики?",
        "expected_code": "KMG-VND-4071",
        "expected_section_contains": "переписк",
    },
    {
        "question": "Что относится к эффективным совещаниям по кодексу деловой этики?",
        "expected_code": "KMG-VND-4071",
        "expected_section_contains": "Совещания",
    },
    {
        "question": "Как формулировать SMART-цели на испытательный срок?",
        "expected_code": "KMG-DI-6241",
        "expected_section_contains": "SMART",
    },
    {
        "question": "Какой курс доллара сегодня?",
        "expected_mode": "no_context",
    },
]


def ask(question: str) -> dict:
    payload = json.dumps({"employee_id": 1, "question": question}).encode("utf-8")
    request = urllib.request.Request(
        f"{BASE_URL}/ask",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    print("=== Digital Buddy E2E tests (questions from VND instructions) ===\n")
    passed = 0
    failed = 0

    for test in TESTS:
        question = test["question"]
        try:
            result = ask(question)
        except Exception as error:
            print(f"FAIL: {question}")
            print(f"  Error: {error}\n")
            failed += 1
            continue

        code_ok = True
        section_ok = True
        mode_ok = True

        if test.get("expected_code"):
            code_ok = result.get("document_code") == test["expected_code"]
        if test.get("expected_section_contains"):
            section = (result.get("section") or "").lower()
            answer = (result.get("answer") or "").lower()
            needle = test["expected_section_contains"].lower()
            section_ok = needle in section or needle in answer
        if test.get("expected_mode"):
            mode_ok = result.get("mode") == test["expected_mode"]
            code_ok = not result.get("document_code")

        ok = code_ok and section_ok and mode_ok
        status = "PASS" if ok else "FAIL"
        print(f"{status}: {question}")
        print(f"  mode={result.get('mode')} code={result.get('document_code')}")
        print(f"  source={result.get('source')}")
        print(f"  section={result.get('section')}")
        answer = result.get("answer", "")
        print(f"  answer={answer[:200]}...")
        print()

        if ok:
            passed += 1
        else:
            failed += 1

    print(f"=== Results: {passed} passed, {failed} failed ===")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
