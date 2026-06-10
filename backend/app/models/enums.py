import enum


class OnboardingStage(str, enum.Enum):
    preparation = "preparation"
    introduction = "introduction"
    engagement = "engagement"
    adaptation = "adaptation"
    retention = "retention"


class TaskStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    overdue = "overdue"


class ChatRole(str, enum.Enum):
    user = "user"
    assistant = "assistant"


class SentimentType(str, enum.Enum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"


class RiskLevel(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class RiskStatus(str, enum.Enum):
    active = "active"
    resolved = "resolved"


class MeetingStatus(str, enum.Enum):
    planned = "planned"
    completed = "completed"
    cancelled = "cancelled"


class SmartGoalStatus(str, enum.Enum):
    planned = "planned"
    in_progress = "in_progress"
    completed = "completed"
    needs_update = "needs_update"


class LearningModuleStatus(str, enum.Enum):
    not_started = "not_started"
    in_progress = "in_progress"
    completed = "completed"
    overdue = "overdue"


class RecommendationPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class SurveyType(str, enum.Enum):
    pulse_day_14 = "pulse_day_14"
    nps_day_30 = "nps_day_30"
    final_nps = "final_nps"
