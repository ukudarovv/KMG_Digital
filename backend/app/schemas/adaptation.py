from datetime import date, datetime, time

from pydantic import BaseModel, Field

from app.models.enums import (
    LearningModuleStatus,
    MeetingStatus,
    SmartGoalStatus,
)


class OneToOneMeetingBase(BaseModel):
    title: str
    description: str | None = None
    meeting_date: date
    meeting_time: time | None = None
    status: MeetingStatus = MeetingStatus.planned


class OneToOneMeetingCreate(OneToOneMeetingBase):
    pass


class OneToOneMeetingUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    meeting_date: date | None = None
    meeting_time: time | None = None
    status: MeetingStatus | None = None


class OneToOneMeetingRead(OneToOneMeetingBase):
    id: int
    employee_id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class SmartGoalBase(BaseModel):
    title: str
    description: str | None = None
    deadline: date
    status: SmartGoalStatus = SmartGoalStatus.planned


class SmartGoalCreate(SmartGoalBase):
    pass


class SmartGoalUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    deadline: date | None = None
    status: SmartGoalStatus | None = None


class SmartGoalRead(SmartGoalBase):
    id: int
    employee_id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class LearningModuleBase(BaseModel):
    title: str
    deadline: date
    progress: int = Field(default=0, ge=0, le=100)
    status: LearningModuleStatus = LearningModuleStatus.not_started


class LearningModuleCreate(LearningModuleBase):
    pass


class LearningModuleUpdate(BaseModel):
    title: str | None = None
    deadline: date | None = None
    progress: int | None = Field(default=None, ge=0, le=100)
    status: LearningModuleStatus | None = None


class LearningModuleRead(LearningModuleBase):
    id: int
    employee_id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class OneToOnePrepBlock(BaseModel):
    requirement_code: str = "F-18"
    topics: list[str]
    suggested_questions: list[str]


class SmartGoalHelpBlock(BaseModel):
    requirement_code: str = "F-19"
    clarifying_questions: list[str]
    document_code: str


class ReflectionStep(BaseModel):
    step: int
    question: str
    hint: str


class ReflectionDialogBlock(BaseModel):
    requirement_code: str = "F-21"
    steps: list[ReflectionStep]


class InterimAssessmentBlock(BaseModel):
    requirement_code: str = "F-20"
    meeting_date: date | None = None
    employee_prep: list[str]
    manager_prep: list[str]
    days_until: int | None = None


class AdaptationFeatureStatus(BaseModel):
    f17_has_upcoming_meeting: bool
    f17_days_until_meeting: int | None = None
    f18_prep_available: bool
    f19_has_goals: bool
    f20_interim_scheduled: bool
    f20_days_until_interim: int | None = None
    f21_reflection_available: bool
    f22_needs_kpi_update: bool
    f23_incomplete_modules: int
    f24_vnd_available: bool


class AdaptationContextResponse(BaseModel):
    adaptation_day: int
    meetings: list[OneToOneMeetingRead]
    goals: list[SmartGoalRead]
    learning_modules: list[LearningModuleRead]
    one_to_one_prep: OneToOnePrepBlock
    smart_goal_help: SmartGoalHelpBlock
    reflection_dialog: ReflectionDialogBlock
    interim_assessment: InterimAssessmentBlock
    feature_status: AdaptationFeatureStatus
