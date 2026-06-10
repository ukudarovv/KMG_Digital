from datetime import datetime, time, timedelta

from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.models.enums import OnboardingStage, TaskStatus
from app.models.onboarding_task import OnboardingTask

DAY_ONE_TASKS = [
    {
        "title": "Просмотр видео Председателя Правления",
        "description": "Ознакомьтесь с приветственным видеообращением.",
        "external_link": "https://team.kmg.kz/onboarding/welcome-video",
        "confirmation_required": True,
        "initial_status": TaskStatus.in_progress,
    },
    {
        "title": "Инструктаж по технике безопасности",
        "description": "Пройдите обязательный инструктаж и тестирование.",
        "external_link": "https://team.kmg.kz/onboarding/safety-training",
        "confirmation_required": True,
    },
    {
        "title": "Инструктаж по информационной безопасности",
        "description": "Ознакомьтесь с правилами ИБ и подтвердите прохождение.",
        "external_link": "https://team.kmg.kz/onboarding/infosec-training",
        "confirmation_required": True,
    },
    {
        "title": "Ознакомление с пропускным режимом",
        "description": "Изучите правила доступа и использования пропуска.",
        "vnd_document_code": "KMG-PR-1186",
        "confirmation_required": True,
    },
    {
        "title": "Кодекс деловой этики",
        "description": "Ознакомьтесь с кодексом и подтвердите согласие.",
        "vnd_document_code": "KMG-VND-4071",
        "confirmation_required": True,
    },
    {
        "title": "Модуль Комплаенс",
        "description": "Антикоррупционная политика и линия доверия.",
        "vnd_document_code": "KMG-VND-6677",
        "confirmation_required": True,
    },
]

ENGAGEMENT_TASKS = [
    {
        "requirement_code": "F-10",
        "title": "Ознакомление с должностной инструкцией",
        "description": "Изучите должностную инструкцию и положение о подразделении.",
        "vnd_document_code": "KMG-DI-6241",
        "confirmation_required": True,
        "offset_days": 2,
    },
    {
        "requirement_code": "F-11",
        "title": "Постановка целей на испытательный срок в КПД",
        "description": "Совместно с руководителем зафиксируйте цели в системе КПД.",
        "confirmation_required": True,
        "offset_days": 4,
    },
]


class TaskService:
    @staticmethod
    def get_employee_tasks(db: Session, employee_id: int) -> list[OnboardingTask]:
        return (
            db.query(OnboardingTask)
            .filter(OnboardingTask.employee_id == employee_id)
            .order_by(OnboardingTask.id.asc())
            .all()
        )

    @staticmethod
    def get_day_one_tasks(db: Session, employee_id: int) -> list[OnboardingTask]:
        return (
            db.query(OnboardingTask)
            .filter(
                OnboardingTask.employee_id == employee_id,
                OnboardingTask.stage == OnboardingStage.introduction,
            )
            .order_by(OnboardingTask.id.asc())
            .all()
        )

    @staticmethod
    def get_engagement_tasks(db: Session, employee_id: int) -> list[OnboardingTask]:
        return (
            db.query(OnboardingTask)
            .filter(
                OnboardingTask.employee_id == employee_id,
                OnboardingTask.stage == OnboardingStage.engagement,
            )
            .order_by(OnboardingTask.id.asc())
            .all()
        )

    @staticmethod
    def ensure_day_one_tasks(db: Session, employee: Employee) -> list[OnboardingTask]:
        existing_tasks = TaskService.get_day_one_tasks(db, employee.id)
        if not existing_tasks:
            deadline_at = datetime.combine(employee.start_date, time(hour=18, minute=0))
            created_tasks: list[OnboardingTask] = []
            for item in DAY_ONE_TASKS:
                task = OnboardingTask(
                    employee_id=employee.id,
                    stage=OnboardingStage.introduction,
                    title=item["title"],
                    description=item["description"],
                    deadline_at=deadline_at,
                    status=item.get("initial_status", TaskStatus.pending),
                    is_required=True,
                    vnd_document_code=item.get("vnd_document_code"),
                    external_link=item.get("external_link"),
                    confirmation_required=item.get("confirmation_required", False),
                )
                db.add(task)
                created_tasks.append(task)
            db.commit()
            for task in created_tasks:
                db.refresh(task)
            existing_tasks = created_tasks
        else:
            TaskService._backfill_task_metadata(db, existing_tasks, DAY_ONE_TASKS)
        TaskService.ensure_engagement_tasks(db, employee)
        return existing_tasks

    @staticmethod
    def ensure_engagement_tasks(db: Session, employee: Employee) -> list[OnboardingTask]:
        existing_tasks = TaskService.get_engagement_tasks(db, employee.id)
        if existing_tasks:
            TaskService._backfill_task_metadata(db, existing_tasks, ENGAGEMENT_TASKS)
            return existing_tasks
        created_tasks: list[OnboardingTask] = []
        for item in ENGAGEMENT_TASKS:
            deadline_date = employee.start_date + timedelta(days=item["offset_days"])
            deadline_at = datetime.combine(deadline_date, time(hour=18, minute=0))
            task = OnboardingTask(
                employee_id=employee.id,
                stage=OnboardingStage.engagement,
                title=item["title"],
                description=item["description"],
                deadline_at=deadline_at,
                status=TaskStatus.pending,
                is_required=True,
                vnd_document_code=item.get("vnd_document_code"),
                external_link=item.get("external_link"),
                confirmation_required=item.get("confirmation_required", False),
            )
            db.add(task)
            created_tasks.append(task)
        db.commit()
        for task in created_tasks:
            db.refresh(task)
        return created_tasks

    @staticmethod
    def _backfill_task_metadata(db: Session, tasks: list[OnboardingTask], templates: list[dict]) -> None:
        changed = False
        for task in tasks:
            template = next((item for item in templates if item["title"] == task.title), None)
            if not template:
                continue
            if task.vnd_document_code is None and template.get("vnd_document_code"):
                task.vnd_document_code = template["vnd_document_code"]
                changed = True
            if task.external_link is None and template.get("external_link"):
                task.external_link = template["external_link"]
                changed = True
            if not task.confirmation_required and template.get("confirmation_required"):
                task.confirmation_required = True
                changed = True
        if changed:
            db.commit()

    @staticmethod
    def get_task_by_id(db: Session, task_id: int) -> OnboardingTask | None:
        return db.query(OnboardingTask).filter(OnboardingTask.id == task_id).first()

    @staticmethod
    def complete_task(db: Session, task: OnboardingTask) -> OnboardingTask:
        task.status = TaskStatus.completed
        task.completed_at = datetime.now()
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def reset_day_one_demo(db: Session, employee: Employee) -> list[OnboardingTask]:
        employee.start_date = datetime.now().date()
        db.query(OnboardingTask).filter(
            OnboardingTask.employee_id == employee.id,
            OnboardingTask.stage == OnboardingStage.introduction,
        ).delete()
        db.commit()
        db.refresh(employee)
        return TaskService.ensure_day_one_tasks(db, employee)
