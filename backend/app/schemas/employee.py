from datetime import date, datetime

from pydantic import BaseModel, EmailStr


class EmployeeBase(BaseModel):
    bitrix_user_id: int | None = None
    full_name: str
    email: EmailStr | None = None
    position: str | None = None
    department: str | None = None
    department_id: int | None = None
    manager_name: str | None = None
    start_date: date
    language: str = "ru"
    status: str = "active"


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    bitrix_user_id: int | None = None
    full_name: str | None = None
    email: EmailStr | None = None
    position: str | None = None
    department: str | None = None
    department_id: int | None = None
    manager_name: str | None = None
    start_date: date | None = None
    language: str | None = None
    status: str | None = None


class EmployeeRead(EmployeeBase):
    id: int
    candidate_id: int | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
