# -*- coding: utf-8 -*-
"""Unit tests for conversational chat flow."""
import sys

from app.services.buddy_i18n import (
    align_source_with_answer,
    conversational_answer,
    finalize_answer,
    is_conversational_message,
    is_vnd_question,
)
from app.schemas.digital_buddy import DigitalBuddyAnswer


def test_greeting_is_conversational() -> None:
    assert is_conversational_message("Здравствуй")
    assert is_conversational_message("Сәлеметсіз бе")
    assert not is_vnd_question("Здравствуй")


def test_vnd_question_detection() -> None:
    assert is_vnd_question("Что такое конфликт интересов?")
    assert is_vnd_question("Можно ли передавать проксим-карту другим лицам?")
    assert not is_vnd_question("Спасибо")


def test_conversational_answer_no_source() -> None:
    answer = finalize_answer(
        conversational_answer("Здравствуй", "ru"),
        "ru",
        add_footer=False,
    )
    assert answer.mode == "chat"
    assert "здравствуйте" in answer.answer.lower()
    assert answer.source == "Digital Buddy"
    assert not answer.document_code


def test_align_source_conflict_of_interest() -> None:
    misaligned = DigitalBuddyAnswer(
        answer="Конфликт интересов — это противоречие между личными и рабочими интересами.",
        source="Правила организации пропускного режима",
        section="п.5.1",
        document_code="KMG-PR-1186",
        mode="llm",
    )
    aligned = align_source_with_answer(misaligned)
    assert aligned.document_code == "KMG-VND-6677"
    assert "коррупц" in aligned.source.lower() or "противодейств" in aligned.source.lower()


def main() -> int:
    tests = [
        test_greeting_is_conversational,
        test_vnd_question_detection,
        test_conversational_answer_no_source,
        test_align_source_conflict_of_interest,
    ]
    failed = 0
    for test in tests:
        try:
            test()
            print(f"PASS: {test.__name__}")
        except AssertionError as error:
            print(f"FAIL: {test.__name__} — {error}")
            failed += 1
    print(f"\n=== {len(tests) - failed}/{len(tests)} passed ===")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
