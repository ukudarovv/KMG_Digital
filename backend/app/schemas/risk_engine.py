from pydantic import BaseModel


class RiskEngineItem(BaseModel):
    id: int
    title: str
    description: str | None = None
    level: str
    status: str


class RiskEngineAnalyzeResponse(BaseModel):
    employee_id: int
    created_or_updated_count: int
    active_risks_count: int
    active_risks: list[RiskEngineItem]
