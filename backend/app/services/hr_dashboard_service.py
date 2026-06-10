from datetime import date

from sqlalchemy.orm import Session

from app.models.chat_message import ChatMessage
from app.models.development_recommendation import DevelopmentRecommendation
from app.models.employee import Employee
from app.models.enums import (
    ChatRole,
    RiskLevel,
    RiskStatus,
    SentimentType,
    TaskStatus,
)
from app.models.learning_module import LearningModule
from app.models.one_to_one_meeting import OneToOneMeeting
from app.models.onboarding_route import OnboardingRoute
from app.models.onboarding_task import OnboardingTask
from app.models.risk_flag import RiskFlag
from app.models.smart_goal import SmartGoal
from app.models.survey import Survey


class HRDashboardService:
    @staticmethod
    def get_employee_stage(db: Session, employee: Employee) -> str:
        route = (
            db.query(OnboardingRoute)
            .filter(OnboardingRoute.employee_id == employee.id)
            .order_by(OnboardingRoute.id.desc())
            .first()
        )

        if route:
            stage_map = {
                "introduction": "Знакомство",
                "engagement": "Вовлечение",
                "adaptation": "Адаптация",
                "retention": "Закрепление",
            }

            return stage_map.get(route.current_stage.value, "Знакомство")

        adaptation_day = max((date.today() - employee.start_date).days + 1, 1)

        if adaptation_day <= 1:
            return "Знакомство"

        if adaptation_day <= 30:
            return "Вовлечение"

        if adaptation_day <= 90:
            return "Адаптация"

        return "Закрепление"

    @staticmethod
    def calculate_progress(db: Session, employee: Employee) -> tuple[int, int, int]:
        total_tasks = (
            db.query(OnboardingTask)
            .filter(OnboardingTask.employee_id == employee.id)
            .count()
        )

        completed_tasks = (
            db.query(OnboardingTask)
            .filter(
                OnboardingTask.employee_id == employee.id,
                OnboardingTask.status == TaskStatus.completed,
            )
            .count()
        )

        if total_tasks == 0:
            return 0, 0, 0

        progress = round((completed_tasks / total_tasks) * 100)

        return progress, completed_tasks, total_tasks

    @staticmethod
    def get_latest_nps(db: Session, employee: Employee) -> int | None:
        survey = (
            db.query(Survey)
            .filter(
                Survey.employee_id == employee.id,
                Survey.nps_score.isnot(None),
            )
            .order_by(Survey.created_at.desc())
            .first()
        )

        if not survey:
            return None

        return survey.nps_score

    @staticmethod
    def get_sentiment(db: Session, employee: Employee) -> str:
        last_messages = (
            db.query(ChatMessage)
            .filter(
                ChatMessage.employee_id == employee.id,
                ChatMessage.role == ChatRole.user,
                ChatMessage.sentiment.isnot(None),
            )
            .order_by(ChatMessage.created_at.desc())
            .limit(10)
            .all()
        )

        if not last_messages:
            return "neutral"

        negative_count = sum(
            1
            for message in last_messages
            if message.sentiment == SentimentType.negative
        )
        positive_count = sum(
            1
            for message in last_messages
            if message.sentiment == SentimentType.positive
        )

        if negative_count >= 2:
            return "negative"

        if positive_count > negative_count:
            return "positive"

        return "neutral"

    @staticmethod
    def get_risk_level(db: Session, employee: Employee) -> str:
        active_risks = (
            db.query(RiskFlag)
            .filter(
                RiskFlag.employee_id == employee.id,
                RiskFlag.status == RiskStatus.active,
            )
            .all()
        )

        if any(risk.level == RiskLevel.high for risk in active_risks):
            return "high"

        if any(risk.level == RiskLevel.medium for risk in active_risks):
            return "medium"

        return "low"

    @staticmethod
    def get_last_activity(db: Session, employee: Employee) -> str:
        last_message = (
            db.query(ChatMessage)
            .filter(ChatMessage.employee_id == employee.id)
            .order_by(ChatMessage.created_at.desc())
            .first()
        )

        if not last_message:
            return "Нет активности"

        today = date.today()

        if last_message.created_at.date() == today:
            return "Сегодня"

        days_ago = (today - last_message.created_at.date()).days

        if days_ago == 1:
            return "Вчера"

        return f"{days_ago} дн. назад"

    @staticmethod
    def get_dashboard_employees(db: Session):
        employees = db.query(Employee).order_by(Employee.id.desc()).all()

        result = []

        for employee in employees:
            progress, completed_tasks, total_tasks = (
                HRDashboardService.calculate_progress(db, employee)
            )

            result.append(
                {
                    "id": employee.id,
                    "full_name": employee.full_name,
                    "position": employee.position,
                    "department": employee.department,
                    "manager": employee.manager_name,
                    "start_date": employee.start_date,
                    "current_stage": HRDashboardService.get_employee_stage(
                        db, employee
                    ),
                    "progress": progress,
                    "completed_tasks": completed_tasks,
                    "total_tasks": total_tasks,
                    "nps": HRDashboardService.get_latest_nps(db, employee),
                    "sentiment": HRDashboardService.get_sentiment(db, employee),
                    "risk_level": HRDashboardService.get_risk_level(db, employee),
                    "last_activity": HRDashboardService.get_last_activity(
                        db, employee
                    ),
                }
            )

        return result

    @staticmethod
    def get_dashboard(db: Session):
        employees = HRDashboardService.get_dashboard_employees(db)

        total_employees = len(employees)

        if total_employees == 0:
            average_progress = 0
        else:
            average_progress = round(
                sum(employee["progress"] for employee in employees) / total_employees
            )

        high_risk_count = sum(
            1 for employee in employees if employee["risk_level"] == "high"
        )

        active_today_count = sum(
            1 for employee in employees if employee["last_activity"] == "Сегодня"
        )

        return {
            "summary": {
                "total_employees": total_employees,
                "average_progress": average_progress,
                "high_risk_count": high_risk_count,
                "active_today_count": active_today_count,
            },
            "employees": employees,
        }

    @staticmethod
    def get_employee_detail(db: Session, employee_id: int):
        employees = HRDashboardService.get_dashboard_employees(db)

        for employee in employees:
            if employee["id"] == employee_id:
                return employee

        return None

    @staticmethod
    def get_route_steps(employee_stage: str) -> list[dict]:
        stage_order = {
            "Знакомство": 1,
            "Вовлечение": 2,
            "Адаптация": 3,
            "Закрепление": 4,
        }

        current_order = stage_order.get(employee_stage, 1)

        steps = [
            {
                "key": "introduction",
                "title": "Знакомство",
                "description": "День 1, приветствие, видео, обязательные инструктажи.",
                "order": 1,
            },
            {
                "key": "engagement",
                "title": "Вовлечение",
                "description": "Culture Fit Nudges, первые опросы, вовлечение в процессы.",
                "order": 2,
            },
            {
                "key": "adaptation",
                "title": "Адаптация",
                "description": "1:1 встречи, SMART-цели, промежуточная оценка.",
                "order": 3,
            },
            {
                "key": "retention",
                "title": "Закрепление",
                "description": "Итоговая оценка, NPS, рекомендации по развитию.",
                "order": 4,
            },
        ]

        result = []

        for step in steps:
            if step["order"] < current_order:
                status = "done"
            elif step["order"] == current_order:
                status = "active"
            else:
                status = "pending"

            result.append(
                {
                    "key": step["key"],
                    "title": step["title"],
                    "description": step["description"],
                    "status": status,
                }
            )

        return result

    @staticmethod
    def get_sentiment_weeks(db: Session, employee: Employee) -> list[dict]:
        messages = (
            db.query(ChatMessage)
            .filter(
                ChatMessage.employee_id == employee.id,
                ChatMessage.role == ChatRole.user,
                ChatMessage.sentiment.isnot(None),
            )
            .order_by(ChatMessage.created_at.asc())
            .all()
        )

        if not messages:
            return [
                {"week": "1 неделя", "positive": 20, "neutral": 70, "negative": 10},
                {"week": "2 неделя", "positive": 28, "neutral": 62, "negative": 10},
                {"week": "3 неделя", "positive": 35, "neutral": 55, "negative": 10},
                {"week": "4 неделя", "positive": 42, "neutral": 50, "negative": 8},
            ]

        positive = sum(
            1 for message in messages if message.sentiment == SentimentType.positive
        )
        neutral = sum(
            1 for message in messages if message.sentiment == SentimentType.neutral
        )
        negative = sum(
            1 for message in messages if message.sentiment == SentimentType.negative
        )

        total = positive + neutral + negative

        if total == 0:
            return [
                {"week": "Текущая", "positive": 0, "neutral": 100, "negative": 0}
            ]

        return [
            {
                "week": "Текущая",
                "positive": round((positive / total) * 100),
                "neutral": round((neutral / total) * 100),
                "negative": round((negative / total) * 100),
            }
        ]

    @staticmethod
    def get_employee_risk_flags(db: Session, employee: Employee) -> list[dict]:
        risks = (
            db.query(RiskFlag)
            .filter(RiskFlag.employee_id == employee.id)
            .order_by(RiskFlag.created_at.desc())
            .all()
        )

        if not risks:
            return [
                {
                    "id": 1,
                    "title": "Низкая активность в онбординге",
                    "description": "Сотрудник редко открывает материалы адаптации.",
                    "level": "medium",
                    "status": "active",
                },
                {
                    "id": 2,
                    "title": "Нет критических рисков",
                    "description": "Критические признаки риска не обнаружены.",
                    "level": "low",
                    "status": "resolved",
                },
            ]

        return [
            {
                "id": risk.id,
                "title": risk.title,
                "description": risk.description or "",
                "level": risk.level.value,
                "status": risk.status.value,
            }
            for risk in risks
        ]

    @staticmethod
    def get_recommendations(db: Session, employee: Employee) -> list[dict]:
        recommendations = (
            db.query(DevelopmentRecommendation)
            .filter(DevelopmentRecommendation.employee_id == employee.id)
            .order_by(DevelopmentRecommendation.id.asc())
            .all()
        )

        return [
            {
                "id": item.id,
                "title": item.title,
                "description": item.description or "",
                "priority": item.priority.value,
            }
            for item in recommendations
        ]

    @staticmethod
    def get_meetings(db: Session, employee: Employee) -> list[dict]:
        meetings = (
            db.query(OneToOneMeeting)
            .filter(OneToOneMeeting.employee_id == employee.id)
            .order_by(OneToOneMeeting.meeting_date.asc())
            .all()
        )

        return [
            {
                "id": item.id,
                "title": item.title,
                "date": item.meeting_date.strftime("%d.%m.%Y"),
                "time": item.meeting_time.strftime("%H:%M")
                if item.meeting_time
                else "—",
                "status": item.status.value,
                "description": item.description or "",
            }
            for item in meetings
        ]

    @staticmethod
    def get_smart_goals(db: Session, employee: Employee) -> list[dict]:
        goals = (
            db.query(SmartGoal)
            .filter(SmartGoal.employee_id == employee.id)
            .order_by(SmartGoal.deadline.asc())
            .all()
        )

        return [
            {
                "id": item.id,
                "title": item.title,
                "description": item.description or "",
                "deadline": item.deadline.strftime("%d.%m.%Y"),
                "status": item.status.value,
            }
            for item in goals
        ]

    @staticmethod
    def get_learning_modules(db: Session, employee: Employee) -> list[dict]:
        modules = (
            db.query(LearningModule)
            .filter(LearningModule.employee_id == employee.id)
            .order_by(LearningModule.deadline.asc())
            .all()
        )

        return [
            {
                "id": item.id,
                "title": item.title,
                "deadline": item.deadline.strftime("%d.%m.%Y"),
                "progress": item.progress,
                "status": item.status.value,
            }
            for item in modules
        ]

    @staticmethod
    def get_employee_full_detail(db: Session, employee_id: int):
        employee = HRDashboardService.get_employee_detail(db, employee_id)

        if not employee:
            return None

        db_employee = (
            db.query(Employee)
            .filter(Employee.id == employee_id)
            .first()
        )

        if not db_employee:
            return None

        current_stage = employee["current_stage"]

        return {
            "employee": employee,
            "route_steps": HRDashboardService.get_route_steps(current_stage),
            "sentiment_weeks": HRDashboardService.get_sentiment_weeks(
                db,
                db_employee,
            ),
            "risk_flags": HRDashboardService.get_employee_risk_flags(
                db,
                db_employee,
            ),
            "recommendations": HRDashboardService.get_recommendations(
                db,
                db_employee,
            ),
            "meetings": HRDashboardService.get_meetings(db, db_employee),
            "smart_goals": HRDashboardService.get_smart_goals(db, db_employee),
            "learning_modules": HRDashboardService.get_learning_modules(
                db,
                db_employee,
            ),
            "hr_summary": (
                "Сотрудник проходит маршрут адаптации. HR рекомендуется следить "
                "за прогрессом задач, тональностью обращений и своевременностью "
                "1:1 встреч."
            ),
            "privacy_note": (
                "HR видит только аналитику, статусы, риски и показатели. "
                "Текст личной переписки с Digital Buddy не отображается."
            ),
        }
