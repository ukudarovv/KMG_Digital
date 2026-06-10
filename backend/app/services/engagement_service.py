from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.integrations.bitrix.service import BitrixService
from app.models.employee import Employee
from app.models.enums import LearningModuleStatus, OnboardingStage, TaskStatus
from app.models.learning_module import LearningModule
from app.models.onboarding_task import OnboardingTask
from app.services.adaptation_service import AdaptationService
from app.services.nudge_service import NudgeService
from app.services.survey_service import SurveyService

CORPORATE_CHANNELS_UNLOCK_DAY = 4
DUCHR_MEETING_DAY = 20
COURSE_REMINDER_DAYS = {7, 14, 21}

CORPORATE_CHANNELS = {
    "title": "Корпоративные каналы и структура",
    "description": (
        "Digital Buddy подсказывает, куда обращаться по рабочим вопросам "
        "и как устроена структура подразделений KMG."
    ),
    "channels": [
        {
            "name": "ДУЧР",
            "purpose": "Адаптация, обучение, кадровые вопросы",
            "contact": "hr@kmg.kz",
        },
        {
            "name": "Ваше подразделение",
            "purpose": "Операционные задачи, регламенты, цели КПД",
            "contact": "Руководитель / наставник",
        },
        {
            "name": "Служба ИТ",
            "purpose": "Доступы, портал, техподдержка",
            "contact": "helpdesk@kmg.kz",
        },
        {
            "name": "Битрикс-чат Digital Buddy",
            "purpose": "Вопросы по ВНД, культуре, адаптации 24/7",
            "contact": "imbot.send",
        },
    ],
}

DUCHR_MEETING = {
    "title": "Встреча с Директором ДУЧР",
    "description": (
        "На 20-й день адаптации Digital Buddy напомнит о встрече с Директором ДУЧР "
        "и поможет подготовить вопросы."
    ),
    "meeting_day": DUCHR_MEETING_DAY,
    "suggested_questions": [
        "Какие программы развития доступны в первые 90 дней?",
        "Как устроена обратная связь по итогам испытательного срока?",
        "Куда обращаться, если остались вопросы по адаптации?",
        "Какие корпоративные инициативы важны для новых сотрудников?",
    ],
}


class EngagementService:
    @staticmethod
    def ensure_learning_modules(db: Session, employee: Employee) -> list[LearningModule]:
        existing = (
            db.query(LearningModule)
            .filter(LearningModule.employee_id == employee.id)
            .count()
        )
        if existing == 0:
            db.add_all(
                [
                    LearningModule(
                        employee_id=employee.id,
                        title="Информационная безопасность",
                        deadline=employee.start_date + timedelta(days=14),
                        progress=40,
                        status=LearningModuleStatus.in_progress,
                    ),
                    LearningModule(
                        employee_id=employee.id,
                        title="Комплаенс и антикоррупционная политика",
                        deadline=employee.start_date + timedelta(days=21),
                        progress=20,
                        status=LearningModuleStatus.in_progress,
                    ),
                    LearningModule(
                        employee_id=employee.id,
                        title="Кодекс деловой этики",
                        deadline=employee.start_date + timedelta(days=10),
                        progress=60,
                        status=LearningModuleStatus.in_progress,
                    ),
                ]
            )
            db.commit()
        return AdaptationService.get_learning_modules(db, employee.id)

    @staticmethod
    def get_context(db: Session, employee: Employee) -> dict:
        adaptation_day = NudgeService.calculate_adaptation_day(employee)
        modules = EngagementService.ensure_learning_modules(db, employee)
        summary = SurveyService.get_summary(db, employee.id)
        engagement_tasks = (
            db.query(OnboardingTask)
            .filter(
                OnboardingTask.employee_id == employee.id,
                OnboardingTask.stage == OnboardingStage.engagement,
            )
            .order_by(OnboardingTask.id.asc())
            .all()
        )

        f10_completed = any(
            task.title.startswith("Ознакомление с должностной")
            and task.status == TaskStatus.completed
            for task in engagement_tasks
        )
        f11_completed = any(
            task.title.startswith("Постановка целей")
            and task.status == TaskStatus.completed
            for task in engagement_tasks
        )

        corporate_channels = None
        if adaptation_day >= CORPORATE_CHANNELS_UNLOCK_DAY:
            corporate_channels = {
                "requirement_code": "F-12",
                **CORPORATE_CHANNELS,
                "unlocked": True,
            }

        duchr_meeting = None
        if adaptation_day >= DUCHR_MEETING_DAY:
            duchr_meeting = {
                "requirement_code": "F-15",
                **DUCHR_MEETING,
                "unlocked": True,
            }

        return {
            "adaptation_day": adaptation_day,
            "corporate_channels": corporate_channels,
            "learning_modules": modules,
            "duchr_meeting": duchr_meeting,
            "feature_status": {
                "f10_completed": f10_completed,
                "f11_completed": f11_completed,
                "f12_unlocked": adaptation_day >= CORPORATE_CHANNELS_UNLOCK_DAY,
                "f13_has_courses": len(modules) > 0,
                "f14_completed": summary.get("pulse_day_14_completed", False),
                "f15_unlocked": adaptation_day >= DUCHR_MEETING_DAY,
                "f16_completed": summary.get("nps_day_30_completed", False),
            },
        }

    @staticmethod
    def _send_employee_message(employee: Employee, message: str) -> None:
        BitrixService.send_employee_message(employee, message)

    @staticmethod
    def process_login_touchpoints(db: Session, employee: Employee) -> dict:
        adaptation_day = NudgeService.calculate_adaptation_day(employee)
        summary = SurveyService.get_summary(db, employee.id)
        sent: list[str] = []

        if adaptation_day == CORPORATE_CHANNELS_UNLOCK_DAY:
            channels = "\n".join(
                f"• {item['name']}: {item['purpose']} ({item['contact']})"
                for item in CORPORATE_CHANNELS["channels"]
            )
            EngagementService._send_employee_message(
                employee,
                "Digital Buddy | F-12 Корпоративные каналы\n\n"
                f"{CORPORATE_CHANNELS['description']}\n\n{channels}",
            )
            sent.append("f12_corporate_channels")

        if adaptation_day in COURSE_REMINDER_DAYS:
            modules = EngagementService.ensure_learning_modules(db, employee)
            incomplete = [module for module in modules if module.progress < 100]
            if incomplete:
                lines = "\n".join(
                    f"• {module.title}: {module.progress}%"
                    for module in incomplete
                )
                EngagementService._send_employee_message(
                    employee,
                    "Digital Buddy | F-13 Обучающие курсы\n\n"
                    "Напоминание о назначенных курсах. Проверьте прогресс:\n\n"
                    f"{lines}",
                )
                sent.append("f13_course_reminder")

        if adaptation_day == 14 and not summary.get("pulse_day_14_completed"):
            EngagementService._send_employee_message(
                employee,
                "Digital Buddy | F-14 Пульс-опрос (День 14)\n\n"
                "Пройдите пульс-опрос о первых двух неделях адаптации "
                "на портале онбординга. Ответы увидит HR.",
            )
            sent.append("f14_pulse_invite")

        if adaptation_day == DUCHR_MEETING_DAY:
            questions = "\n".join(
                f"• {question}" for question in DUCHR_MEETING["suggested_questions"]
            )
            EngagementService._send_employee_message(
                employee,
                "Digital Buddy | F-15 Встреча с Директором ДУЧР\n\n"
                f"{DUCHR_MEETING['description']}\n\n"
                f"Примеры вопросов:\n{questions}",
            )
            sent.append("f15_duchr_meeting")

        if adaptation_day == 30 and not summary.get("nps_day_30_completed"):
            EngagementService._send_employee_message(
                employee,
                "Digital Buddy | F-16 NPS-опрос (День 30)\n\n"
                "Оцените удовлетворённость адаптацией (NPS) и оставьте комментарий "
                "на портале онбординга.",
            )
            sent.append("f16_nps_invite")

        return {"adaptation_day": adaptation_day, "touchpoints_sent": sent}

    @staticmethod
    def notify_hr_about_survey(db: Session, employee: Employee, survey) -> None:
        answers_text = ""
        if survey.answers:
            answers_text = "\n".join(
                f"• {key}: {value}" for key, value in survey.answers.items()
            )

        nps_part = (
            f"NPS: {survey.nps_score}/10\n" if survey.nps_score is not None else ""
        )
        comment_part = survey.comment or "—"

        BitrixService.send_hr_alert(
            "HR | Результат опроса сотрудника\n"
            f"Сотрудник: {employee.full_name}\n"
            f"Тип: {survey.survey_type.value}\n"
            f"День адаптации: {NudgeService.calculate_adaptation_day(employee)}\n"
            f"{nps_part}"
            f"Комментарий: {comment_part}\n"
            f"{answers_text}"
        )
