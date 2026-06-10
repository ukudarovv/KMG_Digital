from datetime import date, time, timedelta

from sqlalchemy.orm import Session

from app.integrations.bitrix.service import BitrixService
from app.models.employee import Employee
from app.models.enums import (
    LearningModuleStatus,
    MeetingStatus,
    SmartGoalStatus,
)
from app.models.learning_module import LearningModule
from app.models.one_to_one_meeting import OneToOneMeeting
from app.models.smart_goal import SmartGoal
from app.services.adaptation_service import AdaptationService
from app.services.engagement_service import EngagementService
from app.services.nudge_service import NudgeService

INTERIM_ASSESSMENT_KEYWORD = "промежуточн"
ADAPTATION_MODULE_REMINDER_DAYS = {35, 45, 60, 75}

ONE_TO_ONE_PREP_CHECKLIST = [
    "Прогресс по задачам и целям испытательного срока",
    "Сложности и блокеры — что мешает работе",
    "Обратная связь по качеству выполнения задач",
    "Обучение и развитие — какие навыки усилить",
    "Следующие шаги и приоритеты на ближайшие 2 недели",
]

ONE_TO_ONE_SUGGESTED_QUESTIONS = [
    "Какие задачи для меня приоритетны на этой неделе?",
    "Соответствует ли мой прогресс ожиданиям на испытательный срок?",
    "Какие регламенты или процессы мне стоит изучить глубже?",
    "Как лучше сформулировать цели в системе КПД?",
    "Какую обратную связь вы можете дать по моим последним задачам?",
]

SMART_CLARIFYING_QUESTIONS = [
    "Какой конкретный результат вы должны показать к дедлайну?",
    "Как измерить успех — в цифрах, сроках или качестве?",
    "Реалистичен ли объём задачи с учётом текущей нагрузки?",
    "Как цель связана с KPI подразделения и должностной инструкцией?",
    "К какой дате цель должна быть достигнута?",
]

INTERIM_EMPLOYEE_PREP = [
    "Подготовьте список выполненных задач и достижений",
    "Отметьте сложности и темы, где нужна поддержка руководителя",
    "Проверьте актуальность SMART-целей в системе КПД",
    "Сформулируйте вопросы по развитию и ожиданиям",
]

INTERIM_MANAGER_PREP = [
    "Оцените выполнение задач испытательного срока",
    "Подготовьте конструктивную обратную связь",
    "Проверьте соответствие целей KPI подразделения",
    "Определите корректировки плана адаптации при необходимости",
]

REFLECTION_DIALOG_STEPS = [
    {
        "step": 1,
        "question": "Что уже получилось хорошо?",
        "hint": "Задачи, процессы или коммуникации, где вы чувствуете прогресс.",
    },
    {
        "step": 2,
        "question": "Где сейчас есть сложности?",
        "hint": "Темы, документы, процессы или ожидания, которые нужно уточнить.",
    },
    {
        "step": 3,
        "question": "Что нужно скорректировать?",
        "hint": "Цели, обучение, приоритеты или формат взаимодействия с руководителем.",
    },
]


class AdaptationStageService:
    @staticmethod
    def ensure_adaptation_data(db: Session, employee: Employee) -> None:
        EngagementService.ensure_learning_modules(db, employee)

        if (
            db.query(OneToOneMeeting)
            .filter(OneToOneMeeting.employee_id == employee.id)
            .count()
            == 0
        ):
            db.add_all(
                [
                    OneToOneMeeting(
                        employee_id=employee.id,
                        title="Первая 1:1 встреча",
                        description="Обсуждение первых впечатлений, вопросов и ожиданий.",
                        meeting_date=employee.start_date + timedelta(days=7),
                        meeting_time=time(hour=15, minute=0),
                        status=MeetingStatus.planned,
                    ),
                    OneToOneMeeting(
                        employee_id=employee.id,
                        title="Промежуточная оценка",
                        description="Проверка прогресса, целей и вовлечённости.",
                        meeting_date=employee.start_date + timedelta(days=45),
                        meeting_time=time(hour=11, minute=0),
                        status=MeetingStatus.planned,
                    ),
                ]
            )

        if (
            db.query(SmartGoal)
            .filter(SmartGoal.employee_id == employee.id)
            .count()
            == 0
        ):
            db.add_all(
                [
                    SmartGoal(
                        employee_id=employee.id,
                        title="Освоить внутренние процессы",
                        description="Изучить основные регламенты, роли и порядок согласования задач.",
                        deadline=employee.start_date + timedelta(days=30),
                        status=SmartGoalStatus.in_progress,
                    ),
                    SmartGoal(
                        employee_id=employee.id,
                        title="Сформировать рабочий план",
                        description="Совместно с руководителем определить задачи испытательного срока.",
                        deadline=employee.start_date + timedelta(days=14),
                        status=SmartGoalStatus.planned,
                    ),
                ]
            )

        db.commit()

    @staticmethod
    def get_interim_meeting(
        meetings: list[OneToOneMeeting],
    ) -> OneToOneMeeting | None:
        for meeting in meetings:
            if INTERIM_ASSESSMENT_KEYWORD in meeting.title.lower():
                return meeting
        return None

    @staticmethod
    def format_meeting_datetime(meeting: OneToOneMeeting) -> str:
        date_str = meeting.meeting_date.strftime("%d.%m.%Y")
        if meeting.meeting_time:
            return f"{date_str} в {meeting.meeting_time.strftime('%H:%M')}"
        return date_str

    @staticmethod
    def build_one_to_one_reminder_message(meeting: OneToOneMeeting) -> str:
        checklist = "\n".join(f"• {item}" for item in ONE_TO_ONE_PREP_CHECKLIST)
        when = AdaptationStageService.format_meeting_datetime(meeting)
        return (
            "Digital Buddy | F-17 Напоминание о встрече 1:1\n\n"
            f"Через 2 дня состоится встреча «{meeting.title}».\n"
            f"Дата и время: {when}\n\n"
            "Что подготовить:\n"
            f"{checklist}\n\n"
            "Напишите мне «Подготовка к 1:1» — помогу сформулировать вопросы."
        )

    @staticmethod
    def build_interim_assessment_reminder(
        meeting: OneToOneMeeting,
        *,
        for_manager: bool = False,
    ) -> str:
        when = AdaptationStageService.format_meeting_datetime(meeting)
        if for_manager:
            prep = "\n".join(f"• {item}" for item in INTERIM_MANAGER_PREP)
            return (
                "Digital Buddy | F-20 Промежуточная оценка (руководитель)\n\n"
                f"Через неделю — промежуточная оценка сотрудника ({when}).\n\n"
                "Рекомендации по подготовке:\n"
                f"{prep}"
            )

        prep = "\n".join(f"• {item}" for item in INTERIM_EMPLOYEE_PREP)
        return (
            "Digital Buddy | F-20 Промежуточная оценка\n\n"
            f"Через неделю состоится промежуточная оценка ({when}).\n\n"
            "Рекомендации по подготовке:\n"
            f"{prep}\n\n"
            "Напишите «Рефлексия прогресса» — пройдём подготовку в формате диалога."
        )

    @staticmethod
    def build_kpi_update_reminder(goals: list[SmartGoal]) -> str:
        draft_goals = [
            goal
            for goal in goals
            if goal.status.value in {"planned", "needs_update", "in_progress"}
        ]
        goals_part = ""
        if draft_goals:
            lines = "\n".join(f"• {goal.title}" for goal in draft_goals[:5])
            goals_part = f"\n\nЦели для актуализации:\n{lines}"

        return (
            "Digital Buddy | F-22 Актуализация целей в КПД\n\n"
            "Промежуточная оценка завершена. Совместно с руководителем "
            "обновите цели в системе КПД с учётом обратной связи."
            f"{goals_part}\n\n"
            "Напишите «Помощь с SMART-целями» — помогу сформулировать цели."
        )

    @staticmethod
    def build_learning_module_reminder(modules: list[LearningModule]) -> str:
        incomplete = [
            module
            for module in modules
            if module.progress < 100
            and module.status != LearningModuleStatus.completed
        ]
        lines = "\n".join(
            f"• {module.title}: {module.progress}% "
            f"(дедлайн {module.deadline.strftime('%d.%m.%Y')})"
            for module in incomplete
        )
        return (
            "Digital Buddy | F-23 Обучающие модули\n\n"
            "Напоминание о незавершённых модулях. Проверьте прогресс:\n\n"
            f"{lines}"
        )

    @staticmethod
    def get_context(db: Session, employee: Employee) -> dict:
        AdaptationStageService.ensure_adaptation_data(db, employee)
        adaptation_day = NudgeService.calculate_adaptation_day(employee)
        meetings = AdaptationService.get_meetings(db, employee.id)
        goals = AdaptationService.get_goals(db, employee.id)
        modules = AdaptationService.get_learning_modules(db, employee.id)
        interim_meeting = AdaptationStageService.get_interim_meeting(meetings)
        today = date.today()

        upcoming_meetings = [
            meeting
            for meeting in meetings
            if meeting.status == MeetingStatus.planned
            and meeting.meeting_date >= today
        ]
        next_meeting = upcoming_meetings[0] if upcoming_meetings else None

        days_to_next = (
            (next_meeting.meeting_date - today).days if next_meeting else None
        )
        days_to_interim = (
            (interim_meeting.meeting_date - today).days if interim_meeting else None
        )

        incomplete_modules = [
            module for module in modules if module.progress < 100
        ]

        return {
            "adaptation_day": adaptation_day,
            "meetings": meetings,
            "goals": goals,
            "learning_modules": modules,
            "one_to_one_prep": {
                "requirement_code": "F-18",
                "topics": ONE_TO_ONE_PREP_CHECKLIST,
                "suggested_questions": ONE_TO_ONE_SUGGESTED_QUESTIONS,
            },
            "smart_goal_help": {
                "requirement_code": "F-19",
                "clarifying_questions": SMART_CLARIFYING_QUESTIONS,
                "document_code": "KMG-DI-6241",
            },
            "reflection_dialog": {
                "requirement_code": "F-21",
                "steps": REFLECTION_DIALOG_STEPS,
            },
            "interim_assessment": {
                "requirement_code": "F-20",
                "meeting_date": interim_meeting.meeting_date.isoformat()
                if interim_meeting
                else None,
                "employee_prep": INTERIM_EMPLOYEE_PREP,
                "manager_prep": INTERIM_MANAGER_PREP,
                "days_until": days_to_interim,
            },
            "feature_status": {
                "f17_has_upcoming_meeting": next_meeting is not None,
                "f17_days_until_meeting": days_to_next,
                "f18_prep_available": next_meeting is not None
                and days_to_next is not None
                and days_to_next <= 7,
                "f19_has_goals": len(goals) > 0,
                "f20_interim_scheduled": interim_meeting is not None,
                "f20_days_until_interim": days_to_interim,
                "f21_reflection_available": adaptation_day >= 14,
                "f22_needs_kpi_update": any(
                    goal.status.value in {"needs_update", "planned"}
                    for goal in goals
                ),
                "f23_incomplete_modules": len(incomplete_modules),
                "f24_vnd_available": True,
            },
        }

    @staticmethod
    def _send_employee_message(employee: Employee, message: str) -> None:
        BitrixService.send_employee_message(employee, message)

    @staticmethod
    def process_login_touchpoints(db: Session, employee: Employee) -> dict:
        AdaptationStageService.ensure_adaptation_data(db, employee)
        adaptation_day = NudgeService.calculate_adaptation_day(employee)
        meetings = AdaptationService.get_meetings(db, employee.id)
        goals = AdaptationService.get_goals(db, employee.id)
        modules = AdaptationService.get_learning_modules(db, employee.id)
        today = date.today()
        sent: list[str] = []

        reminder_date = today + timedelta(days=2)
        for meeting in meetings:
            if (
                meeting.status == MeetingStatus.planned
                and meeting.meeting_date == reminder_date
            ):
                AdaptationStageService._send_employee_message(
                    employee,
                    AdaptationStageService.build_one_to_one_reminder_message(meeting),
                )
                sent.append("f17_one_to_one_reminder")

        interim_meeting = AdaptationStageService.get_interim_meeting(meetings)
        if interim_meeting and interim_meeting.status == MeetingStatus.planned:
            days_until = (interim_meeting.meeting_date - today).days
            if days_until == 7:
                AdaptationStageService._send_employee_message(
                    employee,
                    AdaptationStageService.build_interim_assessment_reminder(
                        interim_meeting
                    ),
                )
                BitrixService.send_hr_alert(
                    AdaptationStageService.build_interim_assessment_reminder(
                        interim_meeting,
                        for_manager=True,
                    )
                )
                sent.append("f20_interim_assessment_reminder")

            if days_until == -1:
                AdaptationStageService._send_employee_message(
                    employee,
                    AdaptationStageService.build_kpi_update_reminder(goals),
                )
                sent.append("f22_kpi_update_reminder")

        if adaptation_day > 30 and adaptation_day in ADAPTATION_MODULE_REMINDER_DAYS:
            incomplete = [module for module in modules if module.progress < 100]
            if incomplete:
                AdaptationStageService._send_employee_message(
                    employee,
                    AdaptationStageService.build_learning_module_reminder(modules),
                )
                sent.append("f23_learning_module_reminder")

        return {"adaptation_day": adaptation_day, "touchpoints_sent": sent}

    @staticmethod
    def send_scheduled_one_to_one_reminders(db: Session) -> int:
        reminder_date = date.today() + timedelta(days=2)
        meetings = (
            db.query(OneToOneMeeting)
            .filter(
                OneToOneMeeting.meeting_date == reminder_date,
                OneToOneMeeting.status == MeetingStatus.planned,
            )
            .all()
        )
        count = 0
        for meeting in meetings:
            from app.services.employee_service import EmployeeService

            employee = EmployeeService.get_by_id(db, meeting.employee_id)
            if not employee:
                continue
            AdaptationStageService._send_employee_message(
                employee,
                AdaptationStageService.build_one_to_one_reminder_message(meeting),
            )
            count += 1
        return count

    @staticmethod
    def send_scheduled_interim_reminders(db: Session) -> int:
        reminder_date = date.today() + timedelta(days=7)
        meetings = (
            db.query(OneToOneMeeting)
            .filter(
                OneToOneMeeting.meeting_date == reminder_date,
                OneToOneMeeting.status == MeetingStatus.planned,
            )
            .all()
        )
        count = 0
        for meeting in meetings:
            if INTERIM_ASSESSMENT_KEYWORD not in meeting.title.lower():
                continue
            from app.services.employee_service import EmployeeService

            employee = EmployeeService.get_by_id(db, meeting.employee_id)
            if not employee:
                continue
            AdaptationStageService._send_employee_message(
                employee,
                AdaptationStageService.build_interim_assessment_reminder(meeting),
            )
            BitrixService.send_hr_alert(
                AdaptationStageService.build_interim_assessment_reminder(
                    meeting,
                    for_manager=True,
                )
            )
            count += 1
        return count

    @staticmethod
    def send_scheduled_kpi_update_reminders(db: Session) -> int:
        yesterday = date.today() - timedelta(days=1)
        meetings = (
            db.query(OneToOneMeeting)
            .filter(
                OneToOneMeeting.meeting_date == yesterday,
            )
            .all()
        )
        count = 0
        for meeting in meetings:
            if INTERIM_ASSESSMENT_KEYWORD not in meeting.title.lower():
                continue
            from app.services.employee_service import EmployeeService

            employee = EmployeeService.get_by_id(db, meeting.employee_id)
            if not employee:
                continue
            goals = AdaptationService.get_goals(db, employee.id)
            AdaptationStageService._send_employee_message(
                employee,
                AdaptationStageService.build_kpi_update_reminder(goals),
            )
            count += 1
        return count

    @staticmethod
    def send_scheduled_learning_reminders(db: Session) -> int:
        adaptation_day_marker = NudgeService.calculate_adaptation_day
        count = 0
        for employee in db.query(Employee).all():
            if adaptation_day_marker(employee) <= 30:
                continue
            if adaptation_day_marker(employee) not in ADAPTATION_MODULE_REMINDER_DAYS:
                continue
            modules = AdaptationService.get_learning_modules(db, employee.id)
            incomplete = [module for module in modules if module.progress < 100]
            if not incomplete:
                continue
            AdaptationStageService._send_employee_message(
                employee,
                AdaptationStageService.build_learning_module_reminder(modules),
            )
            count += 1
        return count
