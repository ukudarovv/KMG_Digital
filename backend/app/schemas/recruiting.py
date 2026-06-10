from datetime import date, datetime

from pydantic import BaseModel


class DepartmentMatchRead(BaseModel):
    id: int
    department_id: int
    department_code: str
    department_name: str
    score: int
    reasoning: str | None = None
    rank: int
    decision: str | None = None


class ResumeAnalysisRead(BaseModel):
    id: int
    parsed_json: dict | None = None
    llm_summary: str | None = None
    created_at: datetime
    matches: list[DepartmentMatchRead] = []


class CandidateRead(BaseModel):
    id: int
    full_name: str
    email: str | None = None
    phone: str | None = None
    source: str
    status: str
    consent_given: bool
    confirmed_department_id: int | None = None
    confirmed_department_name: str | None = None
    created_at: datetime
    top_match_department: str | None = None
    top_match_score: int | None = None


class CandidateDetailRead(CandidateRead):
    resume_file_name: str | None = None
    extracted_text_preview: str | None = None
    analysis: ResumeAnalysisRead | None = None
    hired_employee_id: int | None = None


class AnalyzeResumeResponse(BaseModel):
    candidate: CandidateDetailRead
    llm_used: bool


class ConfirmDepartmentRequest(BaseModel):
    department_id: int


class HireCandidateRequest(BaseModel):
    position: str | None = None
    manager_name: str | None = None
    start_date: date | None = None
    bitrix_user_id: int | None = None


class RecruitingSettingsRead(BaseModel):
    prompt_template: str | None = None
    min_score: int
    top_n: int
    llm_enabled: bool
    screening_service_url: str | None = None
    screening_service_available: bool = False

    model_config = {"from_attributes": True}


class RecruitingSettingsUpdate(BaseModel):
    prompt_template: str | None = None
    min_score: int | None = None
    top_n: int | None = None
    llm_enabled: bool | None = None
