from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    service: str


class CandidateInfo(BaseModel):
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None


class VacancyInfo(BaseModel):
    title: str
    required_skills: list[str]
    optional_skills: list[str]
    min_experience_years: int


class ScreeningResult(BaseModel):
    decision: Literal["pass", "reject", "review"]
    score: int = Field(ge=0, le=100)
    matched_required_skills: list[str] = Field(default_factory=list)
    missing_required_skills: list[str] = Field(default_factory=list)
    matched_optional_skills: list[str] = Field(default_factory=list)
    experience_years_detected: int | None = None
    reason: str = ""
    hr_message: str = ""


class MetaInfo(BaseModel):
    filename: str
    file_type: Literal["pdf", "docx"]
    llm_model: str


class ScreenResumeResponse(BaseModel):
    candidate: CandidateInfo
    vacancy: VacancyInfo
    screening: ScreeningResult
    meta: MetaInfo


class LLMCandidateInfo(BaseModel):
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None


class LLMScreeningResult(BaseModel):
    decision: Literal["pass", "reject", "review"] = "review"
    score: int = Field(default=0, ge=0, le=100)
    matched_required_skills: list[str] = Field(default_factory=list)
    missing_required_skills: list[str] = Field(default_factory=list)
    matched_optional_skills: list[str] = Field(default_factory=list)
    experience_years_detected: int | None = None
    reason: str = ""
    hr_message: str = ""


class LLMResponse(BaseModel):
    candidate: LLMCandidateInfo = Field(default_factory=LLMCandidateInfo)
    screening: LLMScreeningResult = Field(default_factory=LLMScreeningResult)
