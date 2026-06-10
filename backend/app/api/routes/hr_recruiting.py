from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.integrations.resume_screening.client import ResumeScreeningClient
from app.models.employee import Employee
from app.models.recruiting import Candidate
from app.schemas.employee import EmployeeRead
from app.schemas.recruiting import (
    AnalyzeResumeResponse,
    CandidateDetailRead,
    CandidateRead,
    ConfirmDepartmentRequest,
    DepartmentMatchRead,
    HireCandidateRequest,
    RecruitingSettingsRead,
    RecruitingSettingsUpdate,
    ResumeAnalysisRead,
)
from app.services.department_service import DepartmentService
from app.services.recruiting_ai_service import (
    ALLOWED_EXTENSIONS,
    MAX_FILE_SIZE,
    RecruitingAiService,
)

router = APIRouter(prefix="/hr/recruiting", tags=["HR Recruiting"])


def _matches_to_read(analysis) -> list[DepartmentMatchRead]:
    return [
        DepartmentMatchRead(
            id=match.id,
            department_id=match.department_id,
            department_code=match.department.code,
            department_name=match.department.name,
            score=match.score,
            reasoning=match.reasoning,
            rank=match.rank,
            decision=match.decision,
        )
        for match in sorted(analysis.department_matches, key=lambda item: item.rank)
    ]


def _to_candidate_read(db: Session, candidate: Candidate) -> CandidateRead:
    analysis = RecruitingAiService.get_latest_analysis(db, candidate)
    top_match_department = None
    top_match_score = None
    if analysis and analysis.department_matches:
        top = min(analysis.department_matches, key=lambda item: item.rank)
        top_match_department = top.department.name
        top_match_score = top.score
    return CandidateRead(
        id=candidate.id,
        full_name=candidate.full_name,
        email=candidate.email,
        phone=candidate.phone,
        source=candidate.source,
        status=candidate.status,
        consent_given=candidate.consent_given,
        confirmed_department_id=candidate.confirmed_department_id,
        confirmed_department_name=(
            candidate.confirmed_department.name
            if candidate.confirmed_department
            else None
        ),
        created_at=candidate.created_at,
        top_match_department=top_match_department,
        top_match_score=top_match_score,
    )


def _to_candidate_detail(db: Session, candidate: Candidate) -> CandidateDetailRead:
    base = _to_candidate_read(db, candidate)
    analysis = RecruitingAiService.get_latest_analysis(db, candidate)
    latest_resume = candidate.resumes[-1] if candidate.resumes else None
    hired_employee = (
        db.query(Employee).filter(Employee.candidate_id == candidate.id).first()
    )

    extracted_preview = None
    if latest_resume and latest_resume.extracted_text:
        extracted_preview = latest_resume.extracted_text[:1200]

    return CandidateDetailRead(
        **base.model_dump(),
        resume_file_name=latest_resume.file_name if latest_resume else None,
        extracted_text_preview=extracted_preview,
        analysis=(
            ResumeAnalysisRead(
                id=analysis.id,
                parsed_json=analysis.parsed_json,
                llm_summary=analysis.llm_summary,
                created_at=analysis.created_at,
                matches=_matches_to_read(analysis),
            )
            if analysis
            else None
        ),
        hired_employee_id=hired_employee.id if hired_employee else None,
    )


def _settings_to_read(settings_row) -> RecruitingSettingsRead:
    client = ResumeScreeningClient()
    return RecruitingSettingsRead(
        prompt_template=settings_row.prompt_template,
        min_score=settings_row.min_score,
        top_n=settings_row.top_n,
        llm_enabled=settings_row.llm_enabled,
        screening_service_url=client.base_url or None,
        screening_service_available=client.is_available(),
    )


@router.get("/settings", response_model=RecruitingSettingsRead)
def get_recruiting_settings(db: Session = Depends(get_db)):
    return _settings_to_read(RecruitingAiService.get_settings(db))


@router.patch("/settings", response_model=RecruitingSettingsRead)
def update_recruiting_settings(
    payload: RecruitingSettingsUpdate,
    db: Session = Depends(get_db),
):
    settings_row = RecruitingAiService.get_settings(db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(settings_row, field, value)
    db.commit()
    db.refresh(settings_row)
    return _settings_to_read(settings_row)


@router.post("/analyze-resume", response_model=AnalyzeResumeResponse, status_code=201)
async def analyze_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Недопустимый формат. Разрешены: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Пустой файл.")
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Файл превышает лимит 10 МБ.")

    candidate, llm_used = RecruitingAiService.analyze_resume(
        db,
        file.filename or f"resume{suffix}",
        content,
    )
    return AnalyzeResumeResponse(
        candidate=_to_candidate_detail(db, candidate),
        llm_used=llm_used,
    )


@router.get("/candidates", response_model=list[CandidateRead])
def get_candidates(db: Session = Depends(get_db)):
    return [
        _to_candidate_read(db, candidate)
        for candidate in RecruitingAiService.get_candidates(db)
    ]


@router.get("/candidates/{candidate_id}", response_model=CandidateDetailRead)
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = RecruitingAiService.get_candidate(db, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return _to_candidate_detail(db, candidate)


@router.post(
    "/candidates/{candidate_id}/confirm-department",
    response_model=CandidateDetailRead,
)
def confirm_department(
    candidate_id: int,
    payload: ConfirmDepartmentRequest,
    db: Session = Depends(get_db),
):
    candidate = RecruitingAiService.get_candidate(db, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    department = DepartmentService.get_by_id(db, payload.department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    candidate = RecruitingAiService.confirm_department(db, candidate, department)
    return _to_candidate_detail(db, candidate)


@router.post("/candidates/{candidate_id}/hire", response_model=EmployeeRead, status_code=201)
def hire_candidate(
    candidate_id: int,
    payload: HireCandidateRequest,
    db: Session = Depends(get_db),
):
    candidate = RecruitingAiService.get_candidate(db, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    if candidate.status == "hired":
        raise HTTPException(status_code=400, detail="Кандидат уже принят на работу.")
    return RecruitingAiService.hire(
        db,
        candidate,
        position=payload.position,
        manager_name=payload.manager_name,
        start_date=payload.start_date,
        bitrix_user_id=payload.bitrix_user_id,
    )
