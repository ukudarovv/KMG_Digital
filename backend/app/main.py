from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.adaptation import router as adaptation_router
from app.api.routes.digital_buddy import router as digital_buddy_router
from app.api.routes.employees import router as employees_router
from app.api.routes.health import router as health_router
from app.api.routes.hr_admin import router as hr_admin_router
from app.api.routes.hr_dashboard import router as hr_dashboard_router
from app.api.routes.hr_documents import router as hr_documents_router
from app.api.routes.hr_recruiting import router as hr_recruiting_router
from app.api.routes.onboarding import router as onboarding_router
from app.api.routes.risk_engine import router as risk_engine_router
from app.api.routes.surveys import router as surveys_router
from app.api.routes.vnd import router as vnd_router
from app.api.routes.webhooks import router as webhooks_router
from app.core.config import settings
from app.core.database import SessionLocal
from app.services.department_service import DepartmentService
from app.services.hr_document_service import HrDocumentService
from app.services.knowledge_index_service import KnowledgeIndexService
from app.services.scheduler_service import start_scheduler, stop_scheduler
from app.services.vnd_service import VndService
import app.models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[KMG Backend] Запуск API-сервера...")
    if not VndService.load_index_meta().get("last_indexed_at"):
        print("[KMG Backend] Индексация базы знаний из Docs...")
        result = KnowledgeIndexService.index_all_documents()
        print(
            "[KMG Backend] База знаний:",
            f"{result.get('chunks_count', 0)} chunks,",
            f"Chroma: {result.get('chroma_count', 0)} vectors.",
        )
    db = SessionLocal()
    try:
        DepartmentService.ensure_default_departments(db)
        HrDocumentService.ensure_default_workflows(db)
    except Exception as error:
        print(f"[KMG Backend] Не удалось создать HR-справочники: {error}")
    finally:
        db.close()
    start_scheduler()
    print("[KMG Backend] API готов: http://127.0.0.1:8010/docs (Docker) или :8000 (локально)")
    yield
    stop_scheduler()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

if settings.environment == "development":
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            settings.frontend_url,
            "https://kmg.aqlant.com",
            "http://kmg.aqlant.com",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(health_router, prefix="/api")
app.include_router(employees_router, prefix="/api")
app.include_router(onboarding_router, prefix="/api")
app.include_router(digital_buddy_router, prefix="/api")
app.include_router(hr_dashboard_router, prefix="/api")
app.include_router(hr_admin_router, prefix="/api")
app.include_router(hr_documents_router, prefix="/api")
app.include_router(hr_recruiting_router, prefix="/api")
app.include_router(adaptation_router, prefix="/api")
app.include_router(surveys_router, prefix="/api")
app.include_router(risk_engine_router, prefix="/api")
app.include_router(vnd_router, prefix="/api")
app.include_router(webhooks_router, prefix="/api")


@app.get("/")
def root():
    return {
        "message": "KMG Onboarding AI Module API",
        "docs": "/docs",
    }
