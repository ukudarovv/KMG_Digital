from datetime import date, timedelta, time

from app.core.database import SessionLocal
from app.models.development_recommendation import DevelopmentRecommendation
from app.models.enums import (
    LearningModuleStatus,
    MeetingStatus,
    RecommendationPriority,
    SmartGoalStatus,
)
from app.models.learning_module import LearningModule
from app.models.one_to_one_meeting import OneToOneMeeting
from app.models.smart_goal import SmartGoal
from app.schemas.employee import EmployeeCreate
from app.services.employee_service import EmployeeService
from app.services.nudge_service import NudgeService
from app.services.task_service import TaskService
from app.services.vnd_service import VndService


def seed_adaptation_data(db, employee):
    existing_meetings = (
        db.query(OneToOneMeeting)
        .filter(OneToOneMeeting.employee_id == employee.id)
        .count()
    )

    if existing_meetings == 0:
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

    existing_goals = (
        db.query(SmartGoal)
        .filter(SmartGoal.employee_id == employee.id)
        .count()
    )

    if existing_goals == 0:
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
                SmartGoal(
                    employee_id=employee.id,
                    title="Пройти обязательное обучение",
                    description="Завершить назначенные курсы по безопасности, этике и комплаенс.",
                    deadline=employee.start_date + timedelta(days=30),
                    status=SmartGoalStatus.in_progress,
                ),
            ]
        )

    existing_modules = (
        db.query(LearningModule)
        .filter(LearningModule.employee_id == employee.id)
        .count()
    )

    if existing_modules == 0:
        db.add_all(
            [
                LearningModule(
                    employee_id=employee.id,
                    title="Информационная безопасность",
                    deadline=employee.start_date,
                    progress=40,
                    status=LearningModuleStatus.in_progress,
                ),
                LearningModule(
                    employee_id=employee.id,
                    title="Комплаенс и антикоррупционная политика",
                    deadline=employee.start_date,
                    progress=20,
                    status=LearningModuleStatus.in_progress,
                ),
                LearningModule(
                    employee_id=employee.id,
                    title="Кодекс деловой этики",
                    deadline=employee.start_date,
                    progress=60,
                    status=LearningModuleStatus.in_progress,
                ),
            ]
        )

    existing_recommendations = (
        db.query(DevelopmentRecommendation)
        .filter(DevelopmentRecommendation.employee_id == employee.id)
        .count()
    )

    if existing_recommendations == 0:
        db.add_all(
            [
                DevelopmentRecommendation(
                    employee_id=employee.id,
                    title="Проверить завершение задач Дня 1",
                    description="Важно завершить видео, инструктажи, Кодекс этики и Комплаенс до конца рабочего дня.",
                    priority=RecommendationPriority.high,
                ),
                DevelopmentRecommendation(
                    employee_id=employee.id,
                    title="Провести короткую 1:1 встречу",
                    description="Руководителю рекомендуется обсудить ожидания, задачи и возможные сложности сотрудника.",
                    priority=RecommendationPriority.medium,
                ),
                DevelopmentRecommendation(
                    employee_id=employee.id,
                    title="Проверить понятность SMART-целей",
                    description="Убедитесь, что сотрудник понимает цели испытательного срока и критерии оценки.",
                    priority=RecommendationPriority.medium,
                ),
            ]
        )

    db.commit()


def seed_employee():
    db = SessionLocal()

    try:
        VndService.seed_default_documents(db)
        NudgeService.seed_default_nudges(db)

        existing_employee = EmployeeService.get_by_bitrix_user_id(
            db=db,
            bitrix_user_id=1001,
        )

        if existing_employee:
            existing_employee.start_date = date.today()
            db.commit()
            db.refresh(existing_employee)
            print(f"Сотрудник уже существует: ID={existing_employee.id}")
            TaskService.ensure_day_one_tasks(db, existing_employee)
            TaskService.ensure_engagement_tasks(db, existing_employee)
            print("Задачи Дня 1 и Вовлечения проверены.")

            seed_adaptation_data(db, existing_employee)
            print("Данные адаптации проверены.")
            return

        employee_payload = EmployeeCreate(
            bitrix_user_id=1001,
            full_name="Азамат Нурланов",
            email="azamat.nurlanov@example.com",
            position="Специалист по закупкам",
            department="Департамент закупок",
            manager_name="Айгуль Сапарова",
            start_date=date.today(),
            language="ru",
            status="active",
        )

        employee = EmployeeService.create(db, employee_payload)

        TaskService.ensure_day_one_tasks(db, employee)
        TaskService.ensure_engagement_tasks(db, employee)
        seed_adaptation_data(db, employee)

        print("Seed успешно выполнен.")
        print(f"Создан сотрудник: ID={employee.id}, ФИО={employee.full_name}")
        print("Созданы 23 Culture Fit карточки.")
        print("Созданы задачи Дня 1 и Вовлечения.")
        print("Загружены документы ВНД.")
        print("Данные адаптации проверены.")

    finally:
        db.close()


if __name__ == "__main__":
    seed_employee()
