from datetime import datetime

from pydantic import BaseModel


class DepartmentBase(BaseModel):
    code: str
    name: str
    description: str | None = None
    competencies: str | None = None
    is_active: bool = True


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    description: str | None = None
    competencies: str | None = None
    is_active: bool | None = None


class DepartmentRead(DepartmentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
