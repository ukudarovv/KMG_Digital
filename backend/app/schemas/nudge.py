from datetime import date, datetime

from pydantic import BaseModel


class CultureFitNudgeBase(BaseModel):
    day_number: int
    title: str
    text: str
    source: str
    is_active: bool = True


class CultureFitNudgeCreate(CultureFitNudgeBase):
    pass


class CultureFitNudgeRead(CultureFitNudgeBase):
    id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class NudgeDeliveryRead(BaseModel):
    id: int
    employee_id: int
    nudge_id: int
    delivery_date: date
    sent_to_popup: bool
    sent_to_chat: bool
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class CurrentNudgeResponse(BaseModel):
    nudge: CultureFitNudgeRead | None
    already_sent_today: bool
    adaptation_day: int


class ShiftAdaptationDayRequest(BaseModel):
    target_day: int | None = None
    delta: int | None = None


class ShiftAdaptationDayResponse(BaseModel):
    success: bool
    adaptation_day: int
    nudge_day: int
    message: str
