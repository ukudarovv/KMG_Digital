from datetime import date

from pydantic import BaseModel


class HREmployeeDashboardItem(BaseModel):
    id: int
    full_name: str
    position: str | None = None
    department: str | None = None
    manager: str | None = None
    start_date: date

    current_stage: str
    progress: int

    completed_tasks: int
    total_tasks: int

    nps: int | None = None
    sentiment: str
    risk_level: str
    last_activity: str


class HRDashboardSummary(BaseModel):
    total_employees: int
    average_progress: int
    high_risk_count: int
    active_today_count: int


class HRDashboardResponse(BaseModel):
    summary: HRDashboardSummary
    employees: list[HREmployeeDashboardItem]


class HRRouteStep(BaseModel):
    key: str
    title: str
    description: str
    status: str


class HRSentimentWeek(BaseModel):
    week: str
    positive: int
    neutral: int
    negative: int


class HRRiskFlagItem(BaseModel):
    id: int
    title: str
    description: str
    level: str
    status: str


class HRRecommendationItem(BaseModel):
    id: int
    title: str
    description: str
    priority: str


class HRMeetingItem(BaseModel):
    id: int
    title: str
    date: str
    time: str
    status: str
    description: str


class HRSmartGoalItem(BaseModel):
    id: int
    title: str
    description: str
    deadline: str
    status: str


class HRLearningModuleItem(BaseModel):
    id: int
    title: str
    deadline: str
    progress: int
    status: str


class HREmployeeDetailResponse(BaseModel):
    employee: HREmployeeDashboardItem
    route_steps: list[HRRouteStep]
    sentiment_weeks: list[HRSentimentWeek]
    risk_flags: list[HRRiskFlagItem]
    recommendations: list[HRRecommendationItem]
    meetings: list[HRMeetingItem]
    smart_goals: list[HRSmartGoalItem]
    learning_modules: list[HRLearningModuleItem]
    hr_summary: str
    privacy_note: str
