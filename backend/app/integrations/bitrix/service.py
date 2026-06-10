from datetime import datetime

from sqlalchemy.orm import Session

from app.core.config import settings
from app.integrations.bitrix.client import BitrixClient
from app.models.employee import Employee
from app.models.onboarding_task import OnboardingTask
from app.services.nudge_service import NudgeService
from app.services.task_service import TaskService


class BitrixService:
    @staticmethod
    def send_employee_message(employee: Employee, message: str) -> dict:
        client = BitrixClient()
        if not employee.bitrix_user_id:
            return {"mock": True, "reason": "bitrix_user_id missing"}
        return client.send_bot_message(str(employee.bitrix_user_id), message)

    @staticmethod
    def send_nudge_message(employee: Employee, nudge_title: str, nudge_text: str, source: str) -> dict:
        client = BitrixClient()
        if not employee.bitrix_user_id:
            return {"mock": True, "reason": "bitrix_user_id missing"}
        message = (
            f"Digital Buddy | Culture Fit — {nudge_title}\n\n"
            f"{nudge_text}\n\n"
            f"Источник ВНД: {source}"
        )
        return client.send_bot_message(str(employee.bitrix_user_id), message)

    @staticmethod
    def send_hr_alert(message: str) -> dict:
        client = BitrixClient()
        dialog_id = str(settings.bitrix_hr_user_id or "hr")
        return client.send_bot_message(dialog_id, message)

    @staticmethod
    def sync_day_one_task(task: OnboardingTask, employee: Employee) -> int | None:
        client = BitrixClient()
        if not client.enabled or not employee.bitrix_user_id or task.bitrix_task_id:
            return task.bitrix_task_id
        deadline_iso = task.deadline_at.isoformat() if task.deadline_at else None
        response = client.create_task(task.title, task.description or "", employee.bitrix_user_id, deadline_iso)
        result = response.get("result")
        if isinstance(result, dict):
            task_id = result.get("task", {}).get("id") or result.get("id")
            if task_id:
                return int(task_id)
        return None

    @staticmethod
    def sync_employee_tasks(db: Session, employee: Employee) -> None:
        tasks = TaskService.get_day_one_tasks(db, employee.id)
        changed = False
        for task in tasks:
            bitrix_task_id = BitrixService.sync_day_one_task(task, employee)
            if bitrix_task_id and task.bitrix_task_id != bitrix_task_id:
                task.bitrix_task_id = bitrix_task_id
                changed = True
        if changed:
            db.commit()

    @staticmethod
    def build_login_popup_payload(db: Session, employee: Employee) -> dict:
        nudge, already_sent_today, adaptation_day = NudgeService.get_current_nudge(db, employee)
        day_one_tasks = TaskService.ensure_day_one_tasks(db, employee)
        next_task = next((task for task in day_one_tasks if task.status.value != "completed"), None)
        completed_count = sum(1 for task in day_one_tasks if task.status.value == "completed")
        return {
            "employee_id": employee.id,
            "employee_name": employee.full_name.split()[0],
            "adaptation_day": adaptation_day,
            "already_sent_today": already_sent_today,
            "completed_tasks": completed_count,
            "total_tasks": len(day_one_tasks),
            "next_task": {
                "title": next_task.title,
                "description": next_task.description,
                "deadline_at": next_task.deadline_at.isoformat() if next_task and next_task.deadline_at else None,
            } if next_task else None,
            "nudge": {
                "day_number": nudge.day_number,
                "title": nudge.title,
                "text": nudge.text,
                "source": nudge.source,
            } if nudge else None,
            "video_url": settings.chairman_video_url,
            "generated_at": datetime.now().isoformat(),
            "mode": "introduction" if adaptation_day == 1 else "engagement" if adaptation_day <= 30 else "adaptation",
        }

    @staticmethod
    def handle_user_login(db: Session, employee: Employee) -> dict:
        payload = BitrixService.build_login_popup_payload(db, employee)
        nudge, already_sent_today, adaptation_day = NudgeService.get_current_nudge(db, employee)
        if nudge and not already_sent_today and adaptation_day > 1:
            NudgeService.send_nudge_to_chat(db, employee)
            BitrixService.send_nudge_message(employee, nudge.title, nudge.text, nudge.source)
            payload["nudge_sent"] = True
        else:
            payload["nudge_sent"] = False

        touchpoints = {}
        if adaptation_day > 1:
            from app.services.engagement_service import EngagementService

            touchpoints = EngagementService.process_login_touchpoints(db, employee)

        from app.services.adaptation_stage_service import AdaptationStageService

        adaptation_touchpoints = AdaptationStageService.process_login_touchpoints(
            db, employee
        )

        payload["engagement_touchpoints"] = touchpoints
        payload["adaptation_touchpoints"] = adaptation_touchpoints
        BitrixService.sync_employee_tasks(db, employee)
        return payload
