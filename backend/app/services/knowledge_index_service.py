"""Index knowledge documents from Docs into RAG chunk store."""

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path

import fitz
import pytesseract
from docx import Document as DocxDocument
from pypdf import PdfReader

from app.services.embedding_service import EmbeddingService
from app.services.vnd_service import RAG_CHUNKS_PATH, VndService

logger = logging.getLogger(__name__)

SECTION_PATTERN = re.compile(
    r"(?:раздел\s+\d+[\.\s][^\n]{0,80}|п\.\s*\d+(?:\.\d+)*[^\n]{0,60})",
    re.IGNORECASE,
)

DOCUMENT_SOURCES = {
    "pass_rules.pdf": ("KMG-PR-1186", "Правила организации пропускного режима"),
    "ethics_code.pdf": ("KMG-VND-4071", "Кодекс деловой этики"),
    "compliance.pdf": ("KMG-VND-6677", "Инструкция по противодействию коррупции"),
    "job_description.pdf": ("KMG-DI-6241", "Должностная инструкция"),
    "tz_spec.docx": ("KMG-TZ-2024", "Техническое задание"),
}


class KnowledgeIndexService:
    @staticmethod
    def extract_pdf_text_pypdf(file_path: Path) -> str:
        reader = PdfReader(str(file_path))
        pages: list[str] = []
        for page in reader.pages:
            text = (page.extract_text() or "").strip()
            if text:
                pages.append(text)
        return "\n\n".join(pages)

    @staticmethod
    def extract_pdf_text_ocr(file_path: Path) -> str:
        pages: list[str] = []
        try:
            with fitz.open(str(file_path)) as document:
                for page_index in range(len(document)):
                    page = document.load_page(page_index)
                    pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                    image = pixmap.pil_image()
                    text = pytesseract.image_to_string(image, lang="rus+eng").strip()
                    if text:
                        pages.append(text)
        except Exception as error:
            logger.warning("OCR failed for %s: %s", file_path.name, error)
            return ""
        return "\n\n".join(pages)

    @staticmethod
    def extract_pdf_text(file_path: Path) -> tuple[str, bool]:
        text = KnowledgeIndexService.extract_pdf_text_pypdf(file_path)
        if text.strip():
            return text, False
        ocr_text = KnowledgeIndexService.extract_pdf_text_ocr(file_path)
        return ocr_text, bool(ocr_text.strip())

    @staticmethod
    def extract_docx_text(file_path: Path) -> str:
        document = DocxDocument(str(file_path))
        paragraphs = [paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()]
        return "\n\n".join(paragraphs)

    @staticmethod
    def detect_section(text: str) -> str | None:
        match = SECTION_PATTERN.search(text)
        if match:
            return match.group(0).strip()
        return None

    @staticmethod
    def chunk_text(
        text: str,
        document_code: str,
        source: str,
        chunk_size: int = 700,
    ) -> list[dict]:
        paragraphs = [part.strip() for part in re.split(r"\n{2,}", text) if part.strip()]
        chunks: list[dict] = []
        buffer = ""
        current_section: str | None = None

        for paragraph in paragraphs:
            section = KnowledgeIndexService.detect_section(paragraph)
            if section:
                current_section = section

            if len(buffer) + len(paragraph) > chunk_size and buffer:
                chunks.append(
                    {
                        "document_code": document_code,
                        "source": source,
                        "section": current_section or f"Фрагмент {len(chunks) + 1}",
                        "text": buffer.strip(),
                    }
                )
                buffer = paragraph
            else:
                buffer = f"{buffer}\n{paragraph}".strip()

        if buffer:
            chunks.append(
                {
                    "document_code": document_code,
                    "source": source,
                    "section": current_section or f"Фрагмент {len(chunks) + 1}",
                    "text": buffer.strip(),
                }
            )

        return chunks

    @staticmethod
    def _merge_seed_chunks(chunks: list[dict]) -> list[dict]:
        seed_chunks = VndService.load_seed_rag_chunks()
        existing = {(item["document_code"], item["text"]) for item in chunks}

        for seed in seed_chunks:
            key = (seed["document_code"], seed["text"])
            if key not in existing:
                curated = {**seed, "is_curated": True}
                chunks.append(curated)
                existing.add(key)

        return chunks

    @staticmethod
    def index_all_documents() -> dict:
        VndService._copy_docs_from_workspace()
        data_dir = VndService.get_data_dir()
        all_chunks: list[dict] = []
        indexed_documents: list[str] = []
        ocr_documents: list[str] = []
        missing_codes: set[str] = set()

        for file_name, (document_code, source) in DOCUMENT_SOURCES.items():
            file_path = data_dir / file_name
            if not file_path.exists():
                missing_codes.add(document_code)
                logger.warning("Knowledge file missing: %s", file_name)
                continue

            text = ""
            used_ocr = False

            if file_path.suffix.lower() == ".pdf":
                text, used_ocr = KnowledgeIndexService.extract_pdf_text(file_path)
            elif file_path.suffix.lower() == ".docx":
                text = KnowledgeIndexService.extract_docx_text(file_path)

            if not text.strip():
                missing_codes.add(document_code)
                logger.warning("No extractable text for %s", file_name)
                continue

            document_chunks = KnowledgeIndexService.chunk_text(text, document_code, source)
            if not document_chunks:
                missing_codes.add(document_code)
                continue

            all_chunks.extend(document_chunks)
            indexed_documents.append(document_code)
            if used_ocr:
                ocr_documents.append(document_code)

        all_chunks = KnowledgeIndexService._merge_seed_chunks(all_chunks)

        output_path = RAG_CHUNKS_PATH
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as file:
            json.dump(all_chunks, file, ensure_ascii=False, indent=2)

        indexed_at = datetime.now(timezone.utc).isoformat()
        meta = {
            "last_indexed_at": indexed_at,
            "chunks_count": len(all_chunks),
            "indexed_documents": indexed_documents,
            "ocr_documents": ocr_documents,
            "seed_fallback_codes": sorted(missing_codes),
        }
        VndService.save_index_meta(meta)

        chroma_count = EmbeddingService.rebuild_index(all_chunks)

        return {
            **meta,
            "chroma_count": chroma_count,
        }
