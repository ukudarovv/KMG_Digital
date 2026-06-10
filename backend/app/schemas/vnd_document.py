from pydantic import BaseModel

from app.models.enums import OnboardingStage


class VndDocumentRead(BaseModel):
    id: int
    code: str
    title: str
    file_name: str | None = None
    bitrix_file_id: int | None = None
    stage: OnboardingStage | None = None
    task_type: str | None = None
    section_hint: str | None = None
    description: str | None = None

    model_config = {"from_attributes": True}
