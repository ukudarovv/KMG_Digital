import json
import shutil
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.culture_fit_nudge import CultureFitNudge
from app.models.enums import OnboardingStage
from app.models.vnd_document import VndDocument

SOURCE_TO_VND_CODE = {
    "Кодекс этики": "KMG-VND-4071",
    "Комплаенс": "KMG-VND-6677",
}

DEFAULT_VND_DOCUMENTS = [
    {
        "code": "KMG-PR-1186",
        "title": "Правила организации пропускного режима",
        "file_name": "pass_rules.pdf",
        "stage": OnboardingStage.introduction,
        "task_type": "pass_mode",
        "section_hint": "Раздел 1. Общие положения",
        "description": "Правила доступа, проксим-карта и режим объекта KMG.",
    },
    {
        "code": "KMG-VND-4071",
        "title": "Кодекс деловой этики АО НК «КазМунайГаз»",
        "file_name": "ethics_code.pdf",
        "stage": OnboardingStage.introduction,
        "task_type": "ethics_code",
        "section_hint": "Раздел 2. Стандарты делового поведения",
        "description": "Нормы профессионального поведения, переписки и совещаний.",
    },
    {
        "code": "KMG-VND-6677",
        "title": "Инструкция по противодействию коррупции",
        "file_name": "compliance.pdf",
        "stage": OnboardingStage.introduction,
        "task_type": "compliance",
        "section_hint": "Раздел 5.3. Конфликты интересов",
        "description": "Антикоррупционная политика, линия доверия и алгоритмы действий.",
    },
    {
        "code": "KMG-DI-6241",
        "title": "Должностная инструкция (образец для адаптации)",
        "file_name": "job_description.pdf",
        "stage": OnboardingStage.engagement,
        "task_type": "job_description",
        "section_hint": "Раздел 5. Функциональные обязанности",
        "description": "Обязанности, KPI и контекст для SMART-целей испытательного срока.",
    },
]

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "vnd"
RAG_CHUNKS_PATH = Path(__file__).resolve().parents[1] / "data" / "vnd_rag_chunks.json"
SEED_RAG_CHUNKS_PATH = Path(__file__).resolve().parents[1] / "data" / "seed_rag_chunks.json"
KNOWLEDGE_INDEX_META_PATH = (
    Path(__file__).resolve().parents[1] / "data" / "knowledge_index_meta.json"
)

DOC_FILE_MAPPING = {
    "pass_rules.pdf": (["пропуск", "PR_1186", "1186"], "KMG-PR-1186"),
    "ethics_code.pdf": (["Кодекс", "4071", "этики"], "KMG-VND-4071"),
    "compliance.pdf": (["противодейств", "6677", "коррупц"], "KMG-VND-6677"),
    "job_description.pdf": (["Должностная", "6241", "инструкц"], "KMG-DI-6241"),
    "tz_spec.docx": (["ТЗ", "техническ", "задани", "onboarding", "цифров"], "KMG-TZ-2024"),
}


class VndService:
    @staticmethod
    def get_data_dir() -> Path:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        return DATA_DIR

    @staticmethod
    def get_all(db: Session) -> list[VndDocument]:
        return db.query(VndDocument).order_by(VndDocument.code.asc()).all()

    @staticmethod
    def get_by_code(db: Session, code: str) -> VndDocument | None:
        return db.query(VndDocument).filter(VndDocument.code == code).first()

    @staticmethod
    def get_document_url(code: str | None) -> str | None:
        if not code:
            return None
        return f"/api/vnd/documents/{code}/file"

    @staticmethod
    def resolve_file_path(document: VndDocument) -> Path | None:
        if not document.file_name:
            return None
        file_path = VndService.get_data_dir() / document.file_name
        return file_path if file_path.exists() else None

    @staticmethod
    def seed_default_documents(db: Session) -> None:
        if db.query(VndDocument).count() == 0:
            for item in DEFAULT_VND_DOCUMENTS:
                db.add(VndDocument(**item))
            db.commit()
            VndService._copy_docs_from_workspace()

        VndService._sync_nudge_codes(db)

    @staticmethod
    def _safe_path_at_parent(level: int, *parts: str) -> Path | None:
        try:
            return Path(__file__).resolve().parents[level].joinpath(*parts)
        except IndexError:
            return None

    @staticmethod
    def get_docs_source_dirs() -> list[Path]:
        candidates: list[Path] = []
        if settings.docs_path:
            candidates.append(Path(settings.docs_path))

        for optional_path in (
            VndService._safe_path_at_parent(3, "Docs"),
            VndService._safe_path_at_parent(4, "KMG Digital", "Docs"),
            VndService._safe_path_at_parent(5, "KMG Digital", "Docs"),
        ):
            if optional_path is not None:
                candidates.append(optional_path)

        return [path for path in candidates if path.exists()]

    @staticmethod
    def _copy_docs_from_workspace() -> None:
        target_dir = VndService.get_data_dir()
        copied_targets: set[str] = set()

        for source_dir in VndService.get_docs_source_dirs():
            for file_path in source_dir.iterdir():
                if not file_path.is_file():
                    continue
                lowered = file_path.name.lower()
                for target_name, (markers, _) in DOC_FILE_MAPPING.items():
                    if target_name in copied_targets:
                        continue
                    if any(marker.lower() in lowered for marker in markers):
                        shutil.copy2(file_path, target_dir / target_name)
                        copied_targets.add(target_name)

    @staticmethod
    def load_seed_rag_chunks() -> list[dict]:
        if not SEED_RAG_CHUNKS_PATH.exists():
            return []
        with SEED_RAG_CHUNKS_PATH.open(encoding="utf-8") as file:
            return json.load(file)

    @staticmethod
    def load_index_meta() -> dict:
        if not KNOWLEDGE_INDEX_META_PATH.exists():
            return {}
        with KNOWLEDGE_INDEX_META_PATH.open(encoding="utf-8") as file:
            return json.load(file)

    @staticmethod
    def save_index_meta(meta: dict) -> None:
        KNOWLEDGE_INDEX_META_PATH.parent.mkdir(parents=True, exist_ok=True)
        with KNOWLEDGE_INDEX_META_PATH.open("w", encoding="utf-8") as file:
            json.dump(meta, file, ensure_ascii=False, indent=2)

    @staticmethod
    def _sync_nudge_codes(db: Session) -> None:
        for nudge in db.query(CultureFitNudge).all():
            code = SOURCE_TO_VND_CODE.get(nudge.source)
            if code and nudge.vnd_document_code != code:
                nudge.vnd_document_code = code
        db.commit()

    @staticmethod
    def load_rag_chunks() -> list[dict]:
        if not RAG_CHUNKS_PATH.exists():
            return []
        with RAG_CHUNKS_PATH.open(encoding="utf-8") as file:
            return json.load(file)
