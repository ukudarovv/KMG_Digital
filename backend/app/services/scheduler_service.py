from datetime import date, datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.core.config import settings
from app.core.database import SessionLocal
from app.integrations.bitrix.service import BitrixService
from app.models.employee import Employee
from app.models.enums import OnboardingStage, TaskStatus
from app.models.onboarding_task import OnboardingTask
from app.services.adaptation_stage_service import AdaptationStageService
from app.services.hr_dashboard_service import HRDashboardService
from app.services.risk_engine_service import RiskEngineService
from app.services.survey_service import SurveyService

scheduler = BackgroundScheduler()


def analyze_all_employees_risks():
    db = SessionLocal()
    try:
        employees = db.query(Employee).all()
        for employee in employees:
            RiskEngineService.analyze_employee(db=db, employee_id=employee.id)
        print(f"[RiskEngine] Анализ завершён. Сотрудников: {len(employees)}")
    except Exception as error:
        print(f"[RiskEngine] Ошибка анализа: {error}")
    finally:
        db.close()


def send_day_one_hr_alerts():
    db = SessionLocal()
    try:
        today = date.today()
        employees = db.query(Employee).filter(Employee.start_date == today).all()
        for employee in employees:
            incomplete_tasks = (
                db.query(OnboardingTask)
                .filter(
                    OnboardingTask.employee_id == employee.id,
                    OnboardingTask.stage == OnboardingStage.introduction,
                    OnboardingTask.is_required == True,
                    OnboardingTask.status != TaskStatus.completed,
                )
                .all()
            )
            if incomplete_tasks:
                titles = ", ".join(task.title for task in incomplete_tasks)
                BitrixService.send_hr_alert(
                    f"HR-алерт: у {employee.full_name} не завершены инструктажи Дня 1 ({titles})."
                )
    except Exception as error:
        print(f"[Scheduler] Ошибка HR-алертов: {error}")
    finally:
        db.close()


def send_survey_reminders():
    db = SessionLocal()
    try:
        for employee in db.query(Employee).all():
            adaptation_day = max((date.today() - employee.start_date).days + 1, 1)
            summary = SurveyService.get_summary(db, employee.id)
            if adaptation_day == 14 and not summary.get("pulse_day_14_completed"):
                BitrixService.send_hr_alert(f"Пульс-опрос День 14 доступен для {employee.full_name}.")
            if adaptation_day == 30 and not summary.get("nps_day_30_completed"):
                BitrixService.send_hr_alert(f"NPS День 30 доступен для {employee.full_name}.")
    except Exception as error:
        print(f"[Scheduler] Ошибка опросов: {error}")
    finally:
        db.close()


def send_one_to_one_reminders():
    db = SessionLocal()
    try:
        count = AdaptationStageService.send_scheduled_one_to_one_reminders(db)
        if count:
            print(f"[Scheduler] F-17: отправлено напоминаний 1:1: {count}")
    except Exception as error:
        print(f"[Scheduler] Ошибка 1:1: {error}")
    finally:
        db.close()


def send_interim_assessment_reminders():
    db = SessionLocal()
    try:
        count = AdaptationStageService.send_scheduled_interim_reminders(db)
        if count:
            print(f"[Scheduler] F-20: напоминания о промежуточной оценке: {count}")
    except Exception as error:
        print(f"[Scheduler] Ошибка промежуточной оценки: {error}")
    finally:
        db.close()


def send_kpi_update_reminders():
    db = SessionLocal()
    try:
        count = AdaptationStageService.send_scheduled_kpi_update_reminders(db)
        if count:
            print(f"[Scheduler] F-22: напоминания об актуализации КПД: {count}")
    except Exception as error:
        print(f"[Scheduler] Ошибка актуализации КПД: {error}")
    finally:
        db.close()


def send_adaptation_learning_reminders():
    db = SessionLocal()
    try:
        count = AdaptationStageService.send_scheduled_learning_reminders(db)
        if count:
            print(f"[Scheduler] F-23: напоминания об обучении: {count}")
    except Exception as error:
        print(f"[Scheduler] Ошибка напоминаний об обучении: {error}")
    finally:
        db.close()


def send_day_90_reports():
    db = SessionLocal()
    try:
        today = date.today()
        for employee in db.query(Employee).all():
            if (today - employee.start_date).days + 1 != 90:
                continue
            progress, completed, total = HRDashboardService.calculate_progress(db, employee)
            BitrixService.send_hr_alert(
                f"HR-отчёт 90 дней: {employee.full_name} — {progress}%, задачи {completed}/{total}."
            )
    except Exception as error:
        print(f"[Scheduler] Ошибка отчёта 90 дня: {error}")
    finally:
        db.close()


def midnight_maintenance():
    db = SessionLocal()
    try:
        overdue_tasks = (
            db.query(OnboardingTask)
            .filter(
                OnboardingTask.status != TaskStatus.completed,
                OnboardingTask.deadline_at.isnot(None),
                OnboardingTask.deadline_at < datetime.now(),
            )
            .all()
        )
        for task in overdue_tasks:
            task.status = TaskStatus.overdue
        db.commit()
    except Exception as error:
        print(f"[Scheduler] Ошибка полночного обслуживания: {error}")
    finally:
        db.close()


def start_scheduler():
    if scheduler.running:
        return
    scheduler.add_job(analyze_all_employees_risks, trigger=IntervalTrigger(minutes=settings.risk_engine_interval_minutes), id="risk_engine", replace_existing=True)
    scheduler.add_job(send_day_one_hr_alerts, trigger=CronTrigger(hour=16, minute=0), id="day_one_hr_alerts", replace_existing=True)
    scheduler.add_job(send_survey_reminders, trigger=CronTrigger(hour=10, minute=0), id="survey_reminders", replace_existing=True)
    scheduler.add_job(send_one_to_one_reminders, trigger=CronTrigger(hour=9, minute=0), id="one_to_one_reminders", replace_existing=True)
    scheduler.add_job(send_interim_assessment_reminders, trigger=CronTrigger(hour=9, minute=15), id="interim_assessment_reminders", replace_existing=True)
    scheduler.add_job(send_kpi_update_reminders, trigger=CronTrigger(hour=9, minute=20), id="kpi_update_reminders", replace_existing=True)
    scheduler.add_job(send_adaptation_learning_reminders, trigger=CronTrigger(hour=10, minute=30), id="adaptation_learning_reminders", replace_existing=True)
    scheduler.add_job(send_day_90_reports, trigger=CronTrigger(hour=9, minute=30), id="day_90_reports", replace_existing=True)
    scheduler.add_job(midnight_maintenance, trigger=CronTrigger(hour=0, minute=5), id="midnight_maintenance", replace_existing=True)
    scheduler.start()
    print("[Scheduler] APScheduler запущен.")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
