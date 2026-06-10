import re

from sqlalchemy.orm import Session

from app.models.chat_message import ChatMessage
from app.models.employee import Employee
from app.models.enums import ChatRole, SentimentType
from app.schemas.digital_buddy import DigitalBuddyAnswer
from app.services.buddy_i18n import (
    adaptation_answer,
    conversational_answer,
    curated_kk_answer,
    detect_adaptation_topic,
    detect_language,
    ensure_formal_tone,
    expand_search_query,
    fallback_answer,
    finalize_answer,
    is_conversational_message,
    is_off_topic_question,
    is_vnd_question,
    localize_answer,
    no_context_answer,
    validate_answer_relevance,
)
from app.services.embedding_service import EmbeddingService
from app.services.knowledge_index_service import KnowledgeIndexService
from app.services.llm_service import LlmService
from app.services.rag_service import RagService
from app.services.vnd_service import VndService


class DigitalBuddyService:
    @staticmethod
    def get_status() -> dict:
        models = LlmService.list_models() if LlmService.is_available() else []
        model_ready = settings_model_ready(models)
        index_meta = VndService.load_index_meta()
        chunks = VndService.load_rag_chunks()

        return {
            "llm_enabled": LlmService.is_enabled(),
            "llm_available": LlmService.is_available(),
            "llm_provider": "ollama",
            "llm_model": settings_model_name(),
            "model_ready": model_ready,
            "installed_models": models,
            "embedding_model": settings_embedding_model(),
            "embedding_model_ready": EmbeddingService.is_available(),
            "chunks_count": len(chunks),
            "indexed_documents": index_meta.get("indexed_documents", []),
            "chroma_ready": EmbeddingService.chroma_ready(),
            "chroma_count": EmbeddingService.chroma_count(),
            "last_indexed_at": index_meta.get("last_indexed_at"),
        }

    @staticmethod
    def reindex_knowledge() -> dict:
        return KnowledgeIndexService.index_all_documents()

    @staticmethod
    def is_app_navigation_question(question: str) -> bool:
        normalized = question.lower()
        navigation_markers = [
            "видео",
            "председател",
            "информационной безопасности",
            "технике безопасности",
            "инструктаж",
            "задач",
            "день 1",
            "блок «знакомство»",
            "блок знакомство",
            "модуль комплаенс",
            "где найти",
            "где пройти",
            "как открыть",
            "ақпараттық қауіпсіздік",
            "еңбек қауіпсіздігі",
            "нұсқаулық",
            "тапсырма",
            "бірінші күн",
            "таныстыру",
            "комплаенс",
            "қайда",
            "қалай ашу",
            "төраға",
        ]
        short_markers = ["иб", "тб"]
        return any(marker in normalized for marker in navigation_markers) or any(
            re.search(rf"\b{marker}\b", normalized) for marker in short_markers
        )

    @staticmethod
    def detect_sentiment(text: str) -> SentimentType:
        normalized = text.lower()

        negative_words = [
            "не понимаю",
            "сложно",
            "проблема",
            "плохо",
            "не получается",
            "не знаю",
            "стресс",
            "трудно",
            "қиын",
            "түсінбеймін",
        ]

        positive_words = [
            "понятно",
            "спасибо",
            "хорошо",
            "отлично",
            "удобно",
            "получилось",
            "рахмет",
            "жақсы",
        ]

        if any(word in normalized for word in negative_words):
            return SentimentType.negative

        if any(word in normalized for word in positive_words):
            return SentimentType.positive

        return SentimentType.neutral

    @staticmethod
    def resolve_language(
        db: Session,
        employee: Employee,
        question: str,
        preferred_language: str | None = None,
    ) -> str:
        if preferred_language in {"ru", "kk"}:
            language = preferred_language
        elif detect_language(question) == "kk":
            language = "kk"
        else:
            language = employee.language or "ru"

        if employee.language != language:
            employee.language = language
            db.commit()
            db.refresh(employee)

        return language

    @staticmethod
    def _load_history(db: Session, employee_id: int) -> list[dict[str, str]]:
        messages = (
            db.query(ChatMessage)
            .filter(ChatMessage.employee_id == employee_id)
            .order_by(ChatMessage.id.desc())
            .limit(8)
            .all()
        )
        messages.reverse()

        return [
            {
                "role": "user" if message.role == ChatRole.user else "assistant",
                "text": message.text,
            }
            for message in messages
        ]

    @staticmethod
    def generate_answer(question: str, language: str) -> DigitalBuddyAnswer:
        normalized = question.lower()

        if (
            "иб" in normalized
            or "информационной безопасности" in normalized
            or "ақпараттық қауіпсіздік" in normalized
        ):
            answer = DigitalBuddyAnswer(
                answer=(
                    "Ақпараттық қауіпсіздік бойынша нұсқаулық 1-күн тапсырмалары "
                    "тізімінде орналасқан. Тапсырманы ашып, материалдармен танысыңыз "
                    "және өту фактісін растаңыз."
                    if language == "kk"
                    else (
                        "Инструктаж по информационной безопасности находится "
                        "в списке задач Дня 1. Откройте задачу, ознакомьтесь "
                        "с материалами и подтвердите прохождение."
                    )
                ),
                source=(
                    "Ақпараттық қауіпсіздік регламенті"
                    if language == "kk"
                    else "Регламент информационной безопасности"
                ),
                section=(
                    "2-тарау. Міндетті нұсқаулықтар"
                    if language == "kk"
                    else "Раздел 2. Обязательные инструктажи"
                ),
            )
            return localize_answer(answer, language)

        if (
            "тб" in normalized
            or "технике безопасности" in normalized
            or "еңбек қауіпсіздігі" in normalized
        ):
            answer = DigitalBuddyAnswer(
                answer=(
                    "Еңбек қауіпсіздігі бойынша нұсқаулық 1-күн міндетті "
                    "тапсырмасы. Оны жұмыс күнінің соңына дейін аяқтаңыз."
                    if language == "kk"
                    else (
                        "Инструктаж по технике безопасности обязателен для "
                        "прохождения в День 1. Завершите его до конца рабочего дня."
                    )
                ),
                source=(
                    "Еңбек қауіпсіздігі ережелері"
                    if language == "kk"
                    else "Правила техники безопасности"
                ),
                section=(
                    "1-тарау. Бастапқы нұсқаулық"
                    if language == "kk"
                    else "Раздел 1. Первичный инструктаж"
                ),
            )
            return localize_answer(answer, language)

        if (
            "видео" in normalized
            or "председателя" in normalized
            or "төраға" in normalized
        ):
            answer = DigitalBuddyAnswer(
                answer=(
                    "Басқарма төрағасының бейнеүндеуі «Таныстыру» блогында "
                    "қолжетімді. Бейнені көру міндетті тапсырма болып табылады."
                    if language == "kk"
                    else (
                        "Видеообращение Председателя Правления доступно в блоке "
                        "«Знакомство». Просмотр видео является обязательной задачей."
                    )
                ),
                source=(
                    "Бейімделу бағдарламасы"
                    if language == "kk"
                    else "Программа адаптации"
                ),
                section=(
                    "1-күн. Қош келдіңіз"
                    if language == "kk"
                    else "День 1. Приветствие"
                ),
            )
            return localize_answer(answer, language)

        if "комплаенс" in normalized or "антикорруп" in normalized:
            answer = DigitalBuddyAnswer(
                answer=(
                    "Комплаенс модулі антикоррупциялық саясатты және сенім "
                    "желісі туралы ақпаратты қамтиды. Оны 1-күн ішінде өту керек."
                    if language == "kk"
                    else (
                        "Модуль Комплаенс включает антикоррупционную политику "
                        "и информацию о линии доверия. Его нужно пройти в День 1."
                    )
                ),
                source=(
                    "Комплаенс саясаты"
                    if language == "kk"
                    else "Комплаенс-политика"
                ),
                section=(
                    "Антикоррупциялық талаптар"
                    if language == "kk"
                    else "Антикоррупционные требования"
                ),
            )
            return localize_answer(answer, language)

        return localize_answer(fallback_answer(language), language)

    @staticmethod
    def ask(
        db: Session,
        employee_id: int,
        question: str,
        preferred_language: str | None = None,
    ) -> DigitalBuddyAnswer:
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            raise ValueError("Employee not found")

        language = DigitalBuddyService.resolve_language(
            db,
            employee,
            question,
            preferred_language=preferred_language,
        )
        sentiment = DigitalBuddyService.detect_sentiment(question)
        history = DigitalBuddyService._load_history(db, employee_id)
        search_query = expand_search_query(question, language)

        user_message = ChatMessage(
            employee_id=employee_id,
            role=ChatRole.user,
            text=question,
            sentiment=sentiment,
        )

        db.add(user_message)
        db.flush()

        answer: DigitalBuddyAnswer | None = None
        answer_mode = "no_context"

        adaptation_topic = detect_adaptation_topic(question)
        if adaptation_topic:
            answer = finalize_answer(
                adaptation_answer(adaptation_topic, language),
                language,
                add_footer=False,
            )
            answer_mode = "adaptation"
        elif is_conversational_message(question):
            answer = finalize_answer(
                conversational_answer(question, language),
                language,
                add_footer=False,
            )
            answer_mode = "chat"
        elif is_off_topic_question(question):
            answer = finalize_answer(
                no_context_answer(language),
                language,
                add_footer=False,
            )
            answer_mode = "no_context"
        elif not is_vnd_question(question):
            answer = finalize_answer(
                conversational_answer(question, language),
                language,
                add_footer=False,
            )
            answer_mode = "chat"
        elif DigitalBuddyService.is_app_navigation_question(question):
            answer = DigitalBuddyService.generate_answer(question, language)
            answer_mode = "fallback"
        else:
            rag_chunks = RagService.search(search_query)

            if rag_chunks:
                top_chunk = rag_chunks[0]
                llm_answer = None
                document_code = top_chunk.get("document_code")
                kk_template_text = (
                    curated_kk_answer(document_code)
                    if language == "kk"
                    else None
                )
                kk_template = (
                    kk_template_text
                    if kk_template_text
                    and validate_answer_relevance(question, kk_template_text)
                    else None
                )

                if kk_template:
                    llm_answer = DigitalBuddyAnswer(
                        answer=kk_template,
                        source=top_chunk.get("source"),
                        section=top_chunk.get("section"),
                        document_code=document_code,
                    )
                elif top_chunk.get("is_curated"):
                    llm_answer = LlmService.generate_curated_answer(
                        question=question,
                        language=language,
                        chunk=top_chunk,
                    )

                if not llm_answer:
                    llm_answer = LlmService.generate_answer(
                        question=question,
                        language=language,
                        history=history,
                        chunks=rag_chunks,
                    )
                if llm_answer and llm_answer.answer.strip():
                    if not validate_answer_relevance(question, llm_answer.answer):
                        llm_answer = None

                if llm_answer and llm_answer.answer.strip():
                    answer = llm_answer
                    answer.answer = ensure_formal_tone(answer.answer, language)
                    answer = finalize_answer(answer, language)
                    answer_mode = "llm"
                else:
                    focused_answer = LlmService.generate_answer(
                        question=question,
                        language=language,
                        history=[],
                        chunks=rag_chunks[:1],
                    )
                    if focused_answer and focused_answer.answer.strip():
                        answer = finalize_answer(focused_answer, language)
                        answer_mode = "llm"
                    else:
                        curated_retry = None
                        if rag_chunks[0].get("is_curated"):
                            curated_retry = LlmService.generate_curated_answer(
                                question=question,
                                language=language,
                                chunk=rag_chunks[0],
                            )
                        if curated_retry:
                            answer = finalize_answer(curated_retry, language)
                            answer_mode = "llm"
                        else:
                            rag_answer = RagService.build_answer(
                                question,
                                chunks=rag_chunks,
                            )
                            if rag_answer:
                                kk_template = (
                                    curated_kk_answer(rag_answer.document_code)
                                    if language == "kk"
                                    else None
                                )
                                if kk_template:
                                    rag_answer.answer = kk_template
                                answer = finalize_answer(rag_answer, language)
                                answer_mode = "rag"
            else:
                answer = localize_answer(no_context_answer(language), language)
                answer_mode = "no_context"

        answer.sentiment = sentiment.value
        answer.language = language
        answer.mode = answer_mode

        assistant_message = ChatMessage(
            employee_id=employee_id,
            role=ChatRole.assistant,
            text=answer.answer,
            source_document=answer.source,
            source_section=answer.section,
            sentiment=SentimentType.neutral,
        )

        db.add(assistant_message)
        db.commit()

        return answer


def settings_model_name() -> str:
    from app.core.config import settings

    return settings.ollama_model


def settings_model_ready(models: list[str]) -> bool:
    target = settings_model_name()
    return any(model == target or model.startswith(f"{target}:") for model in models)


def settings_embedding_model() -> str:
    from app.core.config import settings

    return settings.embedding_model
