import json
import logging
import re

import httpx

from app.core.config import settings
from app.schemas.digital_buddy import DigitalBuddyAnswer
from app.services.buddy_i18n import (
    validate_answer_language,
    validate_answer_relevance,
)
from app.services.rag_service import RagService

logger = logging.getLogger(__name__)

ANSWER_JSON_SCHEMA = (
    '{"answer":"прямой ответ на вопрос, 2-4 предложения",'
    '"source":"название документа из фрагмента",'
    '"section":"раздел или пункт из фрагмента",'
    '"document_code":"код вида KMG-..."}'
)


class LlmService:
    @staticmethod
    def is_enabled() -> bool:
        return settings.llm_enabled

    @staticmethod
    def is_available() -> bool:
        if not settings.llm_enabled:
            return False

        try:
            with httpx.Client(timeout=3.0) as client:
                response = client.get(f"{settings.ollama_base_url}/api/tags")
                return response.status_code == 200
        except httpx.HTTPError:
            return False

    @staticmethod
    def list_models() -> list[str]:
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{settings.ollama_base_url}/api/tags")
                response.raise_for_status()
                payload = response.json()
                return [
                    item.get("name", "")
                    for item in payload.get("models", [])
                    if item.get("name")
                ]
        except httpx.HTTPError:
            return []

    @staticmethod
    def _build_system_prompt(language: str) -> str:
        if language == "kk":
            return (
                "Сіз Digital Buddy — KMG онбординг цифрлық көмекшісісіз.\n"
                "МІНДЕТТІ ЕРЕЖЕЛЕР:\n"
                "1. Жауап ТЕК қазақ тілінде болуы керек (русский тіліне ауысуға болмайды).\n"
                "2. Тек берілген НҚА (ВНД) фрагменттерін пайдаланыңыз — басқа білім жоқ.\n"
                "3. Алдымен сұраққа тікелей жауап беріңіз, содан кейін нақты талапты атаңыз.\n"
                "4. 2-4 қысқа сөйлем, қызметтік «сіз», әдеби қазақ тілі.\n"
                "5. Контекст орысша болса да — жауапты қазақша түсіндіріңіз.\n"
                "6. Тек [Фрагмент 1] мәтінін пайдаланыңыз, басқа тақырыпқа ауысуға болмайды.\n"
                "7. Тыйым салынған болса — жауап «жоқ/болмайды» болуы керек.\n"
                "8. Контекстте жауап жоқ болса — мұны қазақша айтыңыз.\n"
                "9. document_code, source, section — ең сәйкес фрагменттен.\n"
                f"JSON жауап: {ANSWER_JSON_SCHEMA}"
            )

        return (
            "Вы Digital Buddy — цифровой помощник по онбордингу KMG.\n"
            "ОБЯЗАТЕЛЬНЫЕ ПРАВИЛА:\n"
            "1. Ответ ТОЛЬКО на русском языке (без казахских слов и букв әғқңөұүһі).\n"
            "2. Используйте ТОЛЬКО переданные фрагменты ВНД — внешние знания запрещены.\n"
            "3. Сначала дайте прямой ответ на вопрос, затем укажите конкретное требование.\n"
            "4. 2-4 коротких предложения, обращение на «вы».\n"
            "5. Используйте ТОЛЬКО текст [Фрагмент 1], не меняйте тему вопроса.\n"
            "6. Если фрагмент запрещает действие — ответ должен быть отрицательным.\n"
            "7. Если в контексте нет ответа — честно сообщите об этом по-русски.\n"
            "8. document_code, source, section — из наиболее релевантного фрагмента.\n"
            f"JSON ответ: {ANSWER_JSON_SCHEMA}"
        )

    @staticmethod
    def _build_retry_system_prompt(language: str) -> str:
        if language == "kk":
            return (
                "Сіз Digital Buddy. Алдыңғы жауап тіл ережесін бұзды.\n"
                "Қайта жазыңыз: ТЕК қазақ тілінде, 2-4 сөйлем, тек НҚА контексті.\n"
                f"JSON: {ANSWER_JSON_SCHEMA}"
            )

        return (
            "Вы Digital Buddy. Предыдущий ответ нарушил языковое правило.\n"
            "Перепишите: ТОЛЬКО на русском, 2-4 предложения, только контекст ВНД.\n"
            f"JSON: {ANSWER_JSON_SCHEMA}"
        )

    @staticmethod
    def _format_rag_context(
        chunks: list[dict],
    ) -> tuple[str, str | None, str | None, str | None]:
        if not chunks:
            return "", None, None, None

        blocks: list[str] = []
        primary = chunks[0]
        primary_source = primary.get("source")
        primary_section = primary.get("section")
        primary_code = primary.get("document_code")

        for index, chunk in enumerate(chunks[:3], start=1):
            blocks.append(
                f"[Фрагмент {index}]\n"
                f"document_code: {chunk.get('document_code', '—')}\n"
                f"Документ: {chunk.get('source', 'ВНД')}\n"
                f"Раздел: {chunk.get('section', '—')}\n"
                f"Текст: {chunk.get('text', '')}"
            )

        return "\n\n".join(blocks), primary_source, primary_section, primary_code

    @staticmethod
    def _format_history(history: list[dict[str, str]], language: str) -> str:
        if not history:
            return "Диалог пуст." if language == "ru" else "Диалог бос."

        lines: list[str] = []
        for item in history[-4:]:
            if language == "kk":
                role = "Қызметкер" if item["role"] == "user" else "Digital Buddy"
            else:
                role = "Сотрудник" if item["role"] == "user" else "Digital Buddy"
            lines.append(f"{role}: {item['text']}")
        return "\n".join(lines)

    @staticmethod
    def _parse_json_response(raw_text: str) -> dict[str, str] | None:
        text = raw_text.strip()
        if not text:
            return None

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if not match:
                return None
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                return None

    @staticmethod
    def _call_ollama(
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> dict[str, str] | None:
        if not settings.llm_enabled:
            return None

        payload = {
            "model": settings.ollama_model,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": temperature if temperature is not None else settings.llm_temperature,
                "num_predict": max_tokens or settings.llm_max_tokens,
                "top_p": 0.9,
                "repeat_penalty": 1.15,
            },
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

        try:
            with httpx.Client(timeout=settings.llm_timeout_seconds) as client:
                response = client.post(
                    f"{settings.ollama_base_url}/api/chat",
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as error:
            logger.warning("Ollama request failed: %s", error)
            return None

        raw_content = data.get("message", {}).get("content", "")
        return LlmService._parse_json_response(raw_content)

    @staticmethod
    def generate_json(
        system_prompt: str,
        user_prompt: str,
        max_tokens: int | None = None,
    ) -> dict | None:
        return LlmService._call_ollama(
            system_prompt,
            user_prompt,
            max_tokens=max_tokens,
        )

    @staticmethod
    def _build_user_prompt(
        question: str,
        language: str,
        rag_context: str,
        history_text: str,
    ) -> str:
        if language == "kk":
            return (
                "ЖАУАП ТІЛІ: қазақша (міндетті)\n"
                f"Сұрақ: {question}\n\n"
                f"НҚА контексті (басымдық — [Фрагмент 1]):\n{rag_context}\n\n"
                f"Диалог тарихы:\n{history_text}\n\n"
                "Тапсырма: сұраққа тікелей, нақты жауап беріңіз. Тек JSON."
            )

        return (
            "ЯЗЫК ОТВЕТА: русский (обязательно)\n"
            f"Вопрос: {question}\n\n"
            f"Контекст ВНД (приоритет — [Фрагмент 1]):\n{rag_context}\n\n"
            f"История диалога:\n{history_text}\n\n"
            "Задача: дайте прямой точный ответ на вопрос. Только JSON."
        )

    @staticmethod
    def _build_retry_user_prompt(
        question: str,
        language: str,
        rag_context: str,
        previous_answer: str,
    ) -> str:
        if language == "kk":
            return (
                f"Сұрақ: {question}\n\n"
                f"НҚА контексті:\n{rag_context}\n\n"
                f"Қате жауап (қайта жазыңыз): {previous_answer}\n\n"
                "Жаңа жауап тек қазақ тілінде болуы керек."
            )

        return (
            f"Вопрос: {question}\n\n"
            f"Контекст ВНД:\n{rag_context}\n\n"
            f"Неверный ответ (перепишите): {previous_answer}\n\n"
            "Новый ответ должен быть только на русском языке."
        )

    @staticmethod
    def _parsed_to_answer(
        parsed: dict[str, str],
        default_source: str | None,
        default_section: str | None,
        default_code: str | None,
    ) -> DigitalBuddyAnswer:
        return DigitalBuddyAnswer(
            answer=str(parsed.get("answer", "")).strip(),
            source=(parsed.get("source") or default_source) or None,
            section=(parsed.get("section") or default_section) or None,
            document_code=(parsed.get("document_code") or default_code) or None,
        )

    @staticmethod
    def generate_curated_answer(
        question: str,
        language: str,
        chunk: dict,
    ) -> DigitalBuddyAnswer | None:
        source_text = str(chunk.get("text", "")).strip()
        if not source_text:
            return None

        if language == "kk":
            system_prompt = (
                "Сіз Digital Buddy. Тек берілген НҚА мәтінін қазақ тілінде "
                "2-3 сөйлеммен түсіндіріңіз. Тақырыпты өзгертпеңіз.\n"
                "Русский сөздерді қолдануға тыйым. Тек қазақша жазыңыз.\n"
                f"JSON: {ANSWER_JSON_SCHEMA}"
            )
            user_prompt = (
                f"Сұрақ: {question}\n\n"
                f"НҚА мәтіні:\n{source_text[:900]}\n\n"
                f"document_code: {chunk.get('document_code', '')}\n"
                f"source: {chunk.get('source', '')}\n"
                f"section: {chunk.get('section', '')}\n\n"
                "Жауап тек қазақ тілінде."
            )
        else:
            system_prompt = (
                "Вы Digital Buddy. Переформулируйте ТОЛЬКО данный текст ВНД "
                "в 2-3 предложения, отвечая на вопрос. Не меняйте тему.\n"
                f"JSON: {ANSWER_JSON_SCHEMA}"
            )
            user_prompt = (
                f"Вопрос: {question}\n\n"
                f"Текст ВНД:\n{source_text[:900]}\n\n"
                f"document_code: {chunk.get('document_code', '')}\n"
                f"source: {chunk.get('source', '')}\n"
                f"section: {chunk.get('section', '')}\n\n"
                "Ответ только на русском языке."
            )

        parsed = LlmService._call_ollama(system_prompt, user_prompt, temperature=0.08)
        if not parsed or not parsed.get("answer"):
            return None

        answer = LlmService._parsed_to_answer(
            parsed,
            chunk.get("source"),
            chunk.get("section"),
            chunk.get("document_code"),
        )

        if not validate_answer_language(answer.answer, language):
            return None
        if not validate_answer_relevance(question, answer.answer):
            return None

        return answer

    @staticmethod
    def generate_answer(
        question: str,
        language: str,
        history: list[dict[str, str]] | None = None,
        chunks: list[dict] | None = None,
    ) -> DigitalBuddyAnswer | None:
        if not settings.llm_enabled:
            return None

        context_chunks = chunks or RagService.search(question)
        if not context_chunks:
            return None

        rag_context, default_source, default_section, default_code = (
            LlmService._format_rag_context(context_chunks)
        )
        history_text = LlmService._format_history(history or [], language)
        user_prompt = LlmService._build_user_prompt(
            question,
            language,
            rag_context,
            history_text,
        )

        parsed = LlmService._call_ollama(
            LlmService._build_system_prompt(language),
            user_prompt,
        )
        if not parsed or not parsed.get("answer"):
            return None

        answer = LlmService._parsed_to_answer(
            parsed,
            default_source,
            default_section,
            default_code,
        )

        needs_retry = (
            not validate_answer_language(answer.answer, language)
            or not validate_answer_relevance(question, answer.answer)
        )
        if needs_retry:
            retry_parsed = LlmService._call_ollama(
                LlmService._build_retry_system_prompt(language),
                LlmService._build_retry_user_prompt(
                    question,
                    language,
                    rag_context,
                    answer.answer,
                ),
                temperature=0.05,
            )
            if retry_parsed and retry_parsed.get("answer"):
                answer = LlmService._parsed_to_answer(
                    retry_parsed,
                    default_source,
                    default_section,
                    default_code,
                )

        if not validate_answer_language(answer.answer, language):
            return None
        if not validate_answer_relevance(question, answer.answer):
            return None

        return answer
