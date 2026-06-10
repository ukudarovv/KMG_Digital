from pydantic import BaseModel

from app.schemas.adaptation import LearningModuleRead


class CorporateChannelItem(BaseModel):
    name: str
    purpose: str
    contact: str


class CorporateChannelsBlock(BaseModel):
    requirement_code: str = "F-12"
    title: str
    description: str
    channels: list[CorporateChannelItem]
    unlocked: bool


class DuchrMeetingBlock(BaseModel):
    requirement_code: str = "F-15"
    title: str
    description: str
    meeting_day: int
    suggested_questions: list[str]
    unlocked: bool


class EngagementFeatureStatus(BaseModel):
    f10_completed: bool
    f11_completed: bool
    f12_unlocked: bool
    f13_has_courses: bool
    f14_completed: bool
    f15_unlocked: bool
    f16_completed: bool


class EngagementContextResponse(BaseModel):
    adaptation_day: int
    corporate_channels: CorporateChannelsBlock | None
    learning_modules: list[LearningModuleRead]
    duchr_meeting: DuchrMeetingBlock | None
    feature_status: EngagementFeatureStatus
