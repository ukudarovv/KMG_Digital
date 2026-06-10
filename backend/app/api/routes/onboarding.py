from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.integrations.bitrix.service import BitrixService
from app.schemas.nudge import (
    CultureFitNudgeRead,
    CurrentNudgeResponse,
    NudgeDeliveryRead,
    ShiftAdaptationDayRequest,
    ShiftAdaptationDayResponse,
)
from app.schemas.engagement import EngagementContextResponse
from app.schemas.onboarding_task import OnboardingTaskRead
from app.services.employee_service import EmployeeService
from app.services.engagement_service import EngagementService
from app.services.nudge_service import NudgeService
from app.services.task_service import ENGAGEMENT_TASKS, TaskService
from app.services.vnd_service import VndService

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])


def enrich_task(task) -> dict:
    data = OnboardingTaskRead.model_validate(task).model_dump()
    data["document_url"] = VndService.get_document_url(task.vnd_document_code)
    template = next(
        (
            item
            for item in ENGAGEMENT_TASKS
            if item["title"] == task.title
        ),
        None,
    )
    data["requirement_code"] = template.get("requirement_code") if template else None
    return data


@router.get("/day-one/tasks/{employee_id}", response_model=list[OnboardingTaskRead])
def get_day_one_tasks(employee_id: int, db: Session = Depends(get_db)):
    employee = EmployeeService.get_by_id(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    VndService.seed_default_documents(db)
    tasks = TaskService.ensure_day_one_tasks(db, employee)
    BitrixService.sync_employee_tasks(db, employee)
    return [enrich_task(task) for task in tasks]


@router.get(
    "/engagement/context/{employee_id}",
    response_model=EngagementContextResponse,
)
def get_engagement_context(employee_id: int, db: Session = Depends(get_db)):
    employee = EmployeeService.get_by_id(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    TaskService.ensure_engagement_tasks(db, employee)
    return EngagementService.get_context(db, employee)


@router.get("/engagement/tasks/{employee_id}", response_model=list[OnboardingTaskRead])
def get_engagement_tasks(employee_id: int, db: Session = Depends(get_db)):
    employee = EmployeeService.get_by_id(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    VndService.seed_default_documents(db)
    TaskService.ensure_day_one_tasks(db, employee)
    tasks = TaskService.ensure_engagement_tasks(db, employee)
    return [enrich_task(task) for task in tasks]


@router.post("/tasks/{task_id}/complete", response_model=OnboardingTaskRead)
def complete_task(task_id: int, db: Session = Depends(get_db)):
    task = TaskService.get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return enrich_task(TaskService.complete_task(db, task))


@router.get("/nudges", response_model=list[CultureFitNudgeRead])
def get_nudges(db: Session = Depends(get_db)):
    VndService.seed_default_documents(db)
    NudgeService.seed_default_nudges(db)
    return NudgeService.get_all(db)


@router.get("/nudges/current/{employee_id}", response_model=CurrentNudgeResponse)
def get_current_nudge(employee_id: int, db: Session = Depends(get_db)):
    VndService.seed_default_documents(db)
    NudgeService.seed_default_nudges(db)
    employee = EmployeeService.get_by_id(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    nudge, already_sent_today, adaptation_day = NudgeService.get_current_nudge(db, employee)
    return {"nudge": nudge, "already_sent_today": already_sent_today, "adaptation_day": adaptation_day}


@router.post("/nudges/{employee_id}/send", response_model=NudgeDeliveryRead)
def send_current_nudge(employee_id: int, db: Session = Depends(get_db)):
    VndService.seed_default_documents(db)
    NudgeService.seed_default_nudges(db)
    employee = EmployeeService.get_by_id(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    try:
        return NudgeService.send_nudge_to_chat(db, employee)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.post("/day-one/demo-reset/{employee_id}")
def reset_day_one_demo(employee_id: int, db: Session = Depends(get_db)):
    employee = EmployeeService.get_by_id(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    tasks = TaskService.reset_day_one_demo(db, employee)
    return {
        "success": True,
        "message": "День 1 сброшен для демо",
        "tasks_count": len(tasks),
    }


@router.post("/engagement/demo-setup/{employee_id}", response_model=ShiftAdaptationDayResponse)
def setup_engagement_demo(employee_id: int, db: Session = Depends(get_db)):
    employee = EmployeeService.get_by_id(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    NudgeService.seed_default_nudges(db)
    adaptation_day = NudgeService.setup_engagement_demo(db, employee)
    nudge_day = min(adaptation_day, 23)
    return {
        "success": True,
        "adaptation_day": adaptation_day,
        "nudge_day": nudge_day,
        "message": f"Этап «Вовлечение»: день адаптации {adaptation_day}",
    }


@router.post("/nudges/demo-shift-day/{employee_id}", response_model=ShiftAdaptationDayResponse)
def shift_adaptation_day(
    employee_id: int,
    payload: ShiftAdaptationDayRequest,
    db: Session = Depends(get_db),
):
    employee = EmployeeService.get_by_id(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    NudgeService.seed_default_nudges(db)
    adaptation_day = NudgeService.shift_adaptation_day(
        db,
        employee,
        target_day=payload.target_day,
        delta=payload.delta,
    )
    nudge_day = min(adaptation_day, 23)
    return {
        "success": True,
        "adaptation_day": adaptation_day,
        "nudge_day": nudge_day,
        "message": f"День адаптации сдвинут на {adaptation_day}",
    }


@router.delete("/nudges/demo-reset/{employee_id}")
def reset_today_nudge_delivery(employee_id: int, db: Session = Depends(get_db)):
    employee = EmployeeService.get_by_id(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    deleted_count = NudgeService.reset_today_delivery(db, employee)
    return {"success": True, "deleted_count": deleted_count, "message": "Today's nudge delivery reset successfully"}
