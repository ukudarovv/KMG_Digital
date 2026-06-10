from datetime import datetime

from pydantic import BaseModel

from app.models.enums import OnboardingStage, TaskStatus


class OnboardingTaskBase(BaseModel):
    employee_id: int
    bitrix_task_id: int | None = None
    stage: OnboardingStage
    title: str
    description: str | None = None
    deadline_at: datetime | None = None
    status: TaskStatus = TaskStatus.pending
    is_required: bool = True
    vnd_document_code: str | None = None
    external_link: str | None = None
    confirmation_required: bool = False
    document_url: str | None = None
    requirement_code: str | None = None


class OnboardingTaskCreate(OnboardingTaskBase):
    pass


class OnboardingTaskUpdate(BaseModel):
    bitrix_task_id: int | None = None
    title: str | None = None
    description: str | None = None
    deadline_at: datetime | None = None
    status: TaskStatus | None = None
    is_required: bool | None = None
    completed_at: datetime | None = None


class OnboardingTaskRead(OnboardingTaskBase):
    id: int
    created_at: datetime
    completed_at: datetime | None = None

    model_config = {
        "from_attributes": True
    }
