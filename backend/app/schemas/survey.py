from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import SurveyType


class SurveyCreate(BaseModel):
    survey_type: SurveyType
    nps_score: int | None = Field(default=None, ge=0, le=10)
    comment: str | None = None
    answers: dict | None = None


class SurveyUpdate(BaseModel):
    nps_score: int | None = Field(default=None, ge=0, le=10)
    comment: str | None = None
    answers: dict | None = None


class SurveyRead(BaseModel):
    id: int
    employee_id: int
    survey_type: SurveyType
    nps_score: int | None = None
    comment: str | None = None
    answers: dict | None = None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class SurveySummary(BaseModel):
    pulse_day_14_completed: bool
    nps_day_30_completed: bool
    final_nps_completed: bool
    latest_nps: int | None = None
