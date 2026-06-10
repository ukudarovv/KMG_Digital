import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.schemas import HealthResponse, ScreenResumeResponse
from app.services.file_reader import (
    FileValidationError,
    TextExtractionError,
    extract_text,
    validate_extension,
    validate_file_size,
)
from app.services.llm_client import (
    OllamaClient,
    OllamaResponseError,
    OllamaTimeoutError,
    OllamaUnavailableError,
)
from app.services.screening_service import ScreeningService

settings = get_settings()
llm_client = OllamaClient(settings)
screening_service = ScreeningService(settings, llm_client)

app = FastAPI(
    title="Resume Screening Service",
    description="Локальный микросервис AI-проверки резюме через Ollama",
    version="1.0.0",
)

Path(settings.uploads_dir).mkdir(parents=True, exist_ok=True)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", service="resume-screening-service")


@app.post("/screen-resume", response_model=ScreenResumeResponse)
async def screen_resume(
    file: UploadFile = File(...),
    vacancy_title: str = Form(...),
    required_skills: str = Form(...),
    optional_skills: str = Form(""),
    min_experience_years: int = Form(...),
    full_name: str | None = Form(None),
    email: str | None = Form(None),
    phone: str | None = Form(None),
) -> ScreenResumeResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Имя файла не указано")

    try:
        extension = validate_extension(file.filename)
    except FileValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    content = await file.read()
    try:
        validate_file_size(len(content), settings.max_file_size_bytes)
    except FileValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    file_type = "pdf" if extension == ".pdf" else "docx"
    temp_path = Path(settings.uploads_dir) / f"{uuid.uuid4()}{extension}"

    try:
        temp_path.write_bytes(content)
        resume_text = extract_text(temp_path, extension)
    except TextExtractionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    finally:
        if temp_path.exists():
            temp_path.unlink()

    if not await llm_client.ollama_reachable():
        raise HTTPException(
            status_code=503,
            detail="Ollama недоступна. Запустите контейнер: docker compose up -d",
        )
    if not await llm_client.model_installed():
        raise HTTPException(
            status_code=503,
            detail=(
                f"Модель '{settings.ollama_model}' не загружена. "
                f"Выполните: docker exec -it ollama ollama pull {settings.ollama_model}"
            ),
        )

    try:
        result = await screening_service.screen_resume(
            resume_text=resume_text,
            filename=file.filename,
            file_type=file_type,
            vacancy_title=vacancy_title.strip(),
            required_skills_raw=required_skills,
            optional_skills_raw=optional_skills,
            min_experience_years=min_experience_years,
            candidate_full_name=full_name,
            candidate_email=email,
            candidate_phone=phone,
        )
    except OllamaTimeoutError as exc:
        raise HTTPException(status_code=504, detail=str(exc)) from exc
    except (OllamaUnavailableError, OllamaResponseError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return result


@app.exception_handler(Exception)
async def unhandled_exception_handler(_request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"detail": f"Внутренняя ошибка сервера: {exc}"},
    )
