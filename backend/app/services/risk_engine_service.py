from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models.chat_message import ChatMessage
from app.models.enums import (
    ChatRole,
    RiskLevel,
    RiskStatus,
    SentimentType,
    TaskStatus,
)
from app.models.learning_module import LearningModule
from app.models.onboarding_task import OnboardingTask
from app.models.risk_flag import RiskFlag
from app.models.survey import Survey


class RiskEngineService:
    @staticmethod
    def create_or_update_risk(
        db: Session,
        employee_id: int,
        title: str,
        description: str,
        level: RiskLevel,
    ) -> RiskFlag:
        existing_risk = (
            db.query(RiskFlag)
            .filter(
                RiskFlag.employee_id == employee_id,
                RiskFlag.title == title,
                RiskFlag.status == RiskStatus.active,
            )
            .first()
        )

        if existing_risk:
            existing_risk.description = description
            existing_risk.level = level
            db.commit()
            db.refresh(existing_risk)
            return existing_risk

        risk = RiskFlag(
            employee_id=employee_id,
            title=title,
            description=description,
            level=level,
            status=RiskStatus.active,
        )

        db.add(risk)
        db.commit()
        db.refresh(risk)

        return risk

    @staticmethod
    def resolve_risk(
        db: Session,
        employee_id: int,
        title: str,
    ) -> None:
        existing_risk = (
            db.query(RiskFlag)
            .filter(
                RiskFlag.employee_id == employee_id,
                RiskFlag.title == title,
                RiskFlag.status == RiskStatus.active,
            )
            .first()
        )

        if existing_risk:
            existing_risk.status = RiskStatus.resolved
            db.commit()

    @staticmethod
    def check_negative_sentiment(db: Session, employee_id: int) -> list[RiskFlag]:
        messages = (
            db.query(ChatMessage)
            .filter(
                ChatMessage.employee_id == employee_id,
                ChatMessage.role == ChatRole.user,
                ChatMessage.sentiment.isnot(None),
            )
            .order_by(ChatMessage.created_at.desc())
            .limit(10)
            .all()
        )

        negative_count = sum(
            1 for message in messages if message.sentiment == SentimentType.negative
        )

        title = "Негативная тональность обращений"

        if negative_count >= 3:
            return [
                RiskEngineService.create_or_update_risk(
                    db=db,
                    employee_id=employee_id,
                    title=title,
                    description=(
                        "В последних обращениях сотрудника обнаружено несколько "
                        "негативных сигналов. Рекомендуется провести короткую 1:1 встречу."
                    ),
                    level=RiskLevel.high,
                )
            ]

        if negative_count >= 2:
            return [
                RiskEngineService.create_or_update_risk(
                    db=db,
                    employee_id=employee_id,
                    title=title,
                    description=(
                        "В последних сообщениях есть повторяющиеся признаки сложности "
                        "или неудовлетворённости."
                    ),
                    level=RiskLevel.medium,
                )
            ]

        RiskEngineService.resolve_risk(db, employee_id, title)
        return []

    @staticmethod
    def check_low_nps(db: Session, employee_id: int) -> list[RiskFlag]:
        survey = (
            db.query(Survey)
            .filter(
                Survey.employee_id == employee_id,
                Survey.nps_score.isnot(None),
            )
            .order_by(Survey.created_at.desc())
            .first()
        )

        title = "Низкий NPS"

        if not survey:
            RiskEngineService.resolve_risk(db, employee_id, title)
            return []

        if survey.nps_score <= 4:
            return [
                RiskEngineService.create_or_update_risk(
                    db=db,
                    employee_id=employee_id,
                    title=title,
                    description=(
                        f"Последняя NPS-оценка сотрудника: {survey.nps_score}/10. "
                        "Это критический сигнал неудовлетворённости адаптацией."
                    ),
                    level=RiskLevel.high,
                )
            ]

        if survey.nps_score <= 6:
            return [
                RiskEngineService.create_or_update_risk(
                    db=db,
                    employee_id=employee_id,
                    title=title,
                    description=(
                        f"Последняя NPS-оценка сотрудника: {survey.nps_score}/10. "
                        "Рекомендуется уточнить причины низкой оценки."
                    ),
                    level=RiskLevel.medium,
                )
            ]

        RiskEngineService.resolve_risk(db, employee_id, title)
        return []

    @staticmethod
    def check_unfinished_tasks(db: Session, employee_id: int) -> list[RiskFlag]:
        unfinished_count = (
            db.query(OnboardingTask)
            .filter(
                OnboardingTask.employee_id == employee_id,
                OnboardingTask.status.in_(
                    [
                        TaskStatus.pending,
                        TaskStatus.in_progress,
                        TaskStatus.overdue,
                    ]
                ),
            )
            .count()
        )

        title = "Незавершённые задачи адаптации"

        if unfinished_count >= 5:
            return [
                RiskEngineService.create_or_update_risk(
                    db=db,
                    employee_id=employee_id,
                    title=title,
                    description=(
                        f"У сотрудника {unfinished_count} незавершённых задач. "
                        "Высокий риск отставания от маршрута адаптации."
                    ),
                    level=RiskLevel.high,
                )
            ]

        if unfinished_count >= 2:
            return [
                RiskEngineService.create_or_update_risk(
                    db=db,
                    employee_id=employee_id,
                    title=title,
                    description=(
                        f"У сотрудника {unfinished_count} незавершённых задач. "
                        "Рекомендуется напомнить о прохождении маршрута."
                    ),
                    level=RiskLevel.medium,
                )
            ]

        RiskEngineService.resolve_risk(db, employee_id, title)
        return []

    @staticmethod
    def check_overdue_learning(db: Session, employee_id: int) -> list[RiskFlag]:
        today = date.today()

        overdue_modules = (
            db.query(LearningModule)
            .filter(
                LearningModule.employee_id == employee_id,
                LearningModule.deadline < today,
                LearningModule.progress < 100,
            )
            .all()
        )

        title = "Просрочено обучение"

        if len(overdue_modules) >= 2:
            return [
                RiskEngineService.create_or_update_risk(
                    db=db,
                    employee_id=employee_id,
                    title=title,
                    description=(
                        f"У сотрудника {len(overdue_modules)} просроченных обучающих модулей. "
                        "Нужно проверить причины задержки."
                    ),
                    level=RiskLevel.high,
                )
            ]

        if len(overdue_modules) == 1:
            return [
                RiskEngineService.create_or_update_risk(
                    db=db,
                    employee_id=employee_id,
                    title=title,
                    description=(
                        f"Просрочен обучающий модуль: {overdue_modules[0].title}."
                    ),
                    level=RiskLevel.medium,
                )
            ]

        RiskEngineService.resolve_risk(db, employee_id, title)
        return []

    @staticmethod
    def check_no_activity(db: Session, employee_id: int) -> list[RiskFlag]:
        last_message = (
            db.query(ChatMessage)
            .filter(ChatMessage.employee_id == employee_id)
            .order_by(ChatMessage.created_at.desc())
            .first()
        )

        title = "Нет активности"

        if not last_message:
            return [
                RiskEngineService.create_or_update_risk(
                    db=db,
                    employee_id=employee_id,
                    title=title,
                    description=(
                        "Сотрудник ещё не взаимодействовал с Digital Buddy. "
                        "Рекомендуется проверить, получил ли он доступ к онбордингу."
                    ),
                    level=RiskLevel.medium,
                )
            ]

        inactive_threshold = date.today() - timedelta(days=7)

        if last_message.created_at.date() < inactive_threshold:
            return [
                RiskEngineService.create_or_update_risk(
                    db=db,
                    employee_id=employee_id,
                    title=title,
                    description=(
                        "Сотрудник не проявлял активности более 7 дней."
                    ),
                    level=RiskLevel.medium,
                )
            ]

        RiskEngineService.resolve_risk(db, employee_id, title)
        return []

    @staticmethod
    def analyze_employee(db: Session, employee_id: int) -> dict:
        created_or_updated_risks: list[RiskFlag] = []

        checks = [
            RiskEngineService.check_negative_sentiment,
            RiskEngineService.check_low_nps,
            RiskEngineService.check_unfinished_tasks,
            RiskEngineService.check_overdue_learning,
            RiskEngineService.check_no_activity,
        ]

        for check in checks:
            risks = check(db, employee_id)
            created_or_updated_risks.extend(risks)

        active_risks = (
            db.query(RiskFlag)
            .filter(
                RiskFlag.employee_id == employee_id,
                RiskFlag.status == RiskStatus.active,
            )
            .order_by(RiskFlag.created_at.desc())
            .all()
        )

        return {
            "employee_id": employee_id,
            "created_or_updated_count": len(created_or_updated_risks),
            "active_risks_count": len(active_risks),
            "active_risks": [
                {
                    "id": risk.id,
                    "title": risk.title,
                    "description": risk.description,
                    "level": risk.level.value,
                    "status": risk.status.value,
                }
                for risk in active_risks
            ],
        }
