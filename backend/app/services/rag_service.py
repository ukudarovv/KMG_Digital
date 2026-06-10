import re

from app.core.config import settings
from app.schemas.digital_buddy import DigitalBuddyAnswer
from app.services.embedding_service import EmbeddingService
from app.services.vnd_service import VndService


class RagService:
    TOPIC_MARKERS: list[tuple[tuple[str, ...], tuple[str, ...]]] = [
        (("мүдде", "конфликт", "интерес"), ("конфликт", "интерес", "5.3")),
        (("пара", "взятк", "коррупц"), ("взятк", "коррупц", "5.1")),
        (("сенім", "доверия"), ("доверия", "линия")),
        (("проксим", "карт", "пропуск", "жоғал", "турникет"), ("проксим", "пропуск", "карт")),
        (("переписк", "хат", "делов"), ("переписк", "делов")),
        (("совещан", "кездесу"), ("совещан",)),
        (("smart", "мақсат", "испытатель"), ("smart", "испытатель")),
    ]

    @staticmethod
    def _tokenize(text: str) -> set[str]:
        words = re.findall(r"[a-zа-яёәғқңөұүһі0-9]+", text.lower())
        return {word for word in words if len(word) > 2}

    @staticmethod
    def _keyword_search(
        question: str,
        limit: int,
        chunks: list[dict] | None = None,
        min_overlap: int = 2,
    ) -> list[dict]:
        source_chunks = chunks if chunks is not None else VndService.load_rag_chunks()
        if not source_chunks:
            return []

        query_tokens = RagService._tokenize(question)
        normalized_question = question.lower()
        document_hints = {
            "KMG-PR-1186": (
                "пропуск",
                "проксим",
                "турникет",
                "карт",
                "құжат",
                "жоғал",
            ),
            "KMG-VND-4071": (
                "этик",
                "переписк",
                "совещан",
                "общени",
                "хат",
                "кездесу",
            ),
            "KMG-VND-6677": (
                "коррупц",
                "взятк",
                "доверия",
                "комплаенс",
                "конфликт",
                "мүдде",
                "пара",
                "сенім",
            ),
            "KMG-DI-6241": (
                "smart",
                "испытатель",
                "должностн",
                "адаптац",
                "мақсат",
                "бейімделу",
            ),
        }
        scored: list[tuple[float, dict]] = []

        for chunk in source_chunks:
            chunk_text = (
                chunk["text"]
                + " "
                + chunk.get("source", "")
                + " "
                + chunk.get("section", "")
            )
            chunk_tokens = RagService._tokenize(chunk_text)
            overlap = len(query_tokens & chunk_tokens)
            if overlap < min_overlap:
                continue

            score = float(overlap)
            for token in query_tokens:
                if token in chunk["text"].lower():
                    score += 0.5

            section = chunk.get("section", "")
            if chunk.get("is_curated") or section.startswith("Раздел") or "п." in section:
                score += 3.0

            document_code = chunk.get("document_code", "")
            for code, hints in document_hints.items():
                if document_code == code and any(hint in normalized_question for hint in hints):
                    score += 2.0

            section_lower = section.lower()
            text_lower = chunk["text"].lower()
            topic_hints = (
                "переписк",
                "совещан",
                "конфликт",
                "взятк",
                "доверия",
                "пропуск",
                "проксим",
                "smart",
                "хат",
                "кездесу",
                "мүдде",
                "пара",
                "сенім",
                "карт",
                "жоғал",
                "мақсат",
            )
            for hint in topic_hints:
                if hint in normalized_question and hint in section_lower:
                    score += 5.0
                elif hint in normalized_question and hint in text_lower:
                    score += 3.0

            normalized_score = min(1.0, score / max(len(query_tokens), 1))
            if normalized_score > 0:
                item = {**chunk, "score": normalized_score}
                scored.append((normalized_score, item))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [chunk for _, chunk in scored[:limit]]

    @staticmethod
    def _topic_focused_search(question: str, limit: int) -> list[dict]:
        normalized_question = question.lower()
        all_chunks = VndService.load_rag_chunks()
        curated_chunks = [chunk for chunk in all_chunks if chunk.get("is_curated")]
        if not curated_chunks:
            return []

        for question_markers, chunk_markers in RagService.TOPIC_MARKERS:
            if not any(marker in normalized_question for marker in question_markers):
                continue

            focused_chunks = [
                chunk
                for chunk in curated_chunks
                if any(
                    marker in chunk.get("section", "").lower()
                    or marker in chunk.get("text", "").lower()
                    for marker in chunk_markers
                )
            ]
            if not focused_chunks:
                continue

            focused_matches = RagService._keyword_search(
                question,
                limit,
                focused_chunks,
                min_overlap=1,
            )
            if focused_matches:
                return focused_matches

        return []

    @staticmethod
    def search(question: str, limit: int | None = None) -> list[dict]:
        top_k = limit or settings.rag_search_limit
        all_chunks = VndService.load_rag_chunks()
        curated_chunks = [chunk for chunk in all_chunks if chunk.get("is_curated")]

        topic_matches = RagService._topic_focused_search(question, top_k)
        if topic_matches:
            return topic_matches

        if curated_chunks:
            normalized_question = question.lower()
            topic_hints = (
                "переписк",
                "совещан",
                "конфликт",
                "взятк",
                "доверия",
                "пропуск",
                "проксим",
                "smart",
                "хат",
                "кездесу",
                "мүдде",
                "пара",
                "сенім",
                "карт",
                "жоғал",
                "мақсат",
            )
            for hint in topic_hints:
                if hint not in normalized_question:
                    continue
                focused_chunks = [
                    chunk
                    for chunk in curated_chunks
                    if hint in chunk.get("section", "").lower()
                    or hint in chunk.get("text", "").lower()
                ]
                if not focused_chunks:
                    continue
                focused_matches = RagService._keyword_search(
                    question, top_k, focused_chunks, min_overlap=1
                )
                if focused_matches:
                    return focused_matches

            curated_matches = RagService._keyword_search(
                question, top_k, curated_chunks, min_overlap=1
            )
            if curated_matches:
                return curated_matches

        semantic_matches = EmbeddingService.search(question, limit=top_k)
        if semantic_matches:
            return semantic_matches

        keyword_matches = RagService._keyword_search(question, top_k, all_chunks)
        min_keyword_score = max(settings.rag_min_score, 0.35)
        return [
            chunk
            for chunk in keyword_matches
            if chunk.get("score", 0) >= min_keyword_score
        ]

    @staticmethod
    def has_relevant_context(question: str) -> bool:
        return bool(RagService.search(question))

    @staticmethod
    def build_answer(
        question: str,
        chunks: list[dict] | None = None,
    ) -> DigitalBuddyAnswer | None:
        matches = chunks or RagService.search(question)
        if not matches:
            return None

        best = matches[0]
        return DigitalBuddyAnswer(
            answer=best["text"],
            source=best.get("source"),
            section=best.get("section"),
            document_code=best.get("document_code"),
        )
