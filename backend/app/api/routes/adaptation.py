from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.adaptation import (
    AdaptationContextResponse,
    LearningModuleCreate,
    LearningModuleRead,
    LearningModuleUpdate,
    OneToOneMeetingCreate,
    OneToOneMeetingRead,
    OneToOneMeetingUpdate,
    SmartGoalCreate,
    SmartGoalRead,
    SmartGoalUpdate,
)
from app.schemas.nudge import ShiftAdaptationDayResponse
from app.services.adaptation_service import AdaptationService
from app.services.adaptation_stage_service import AdaptationStageService
from app.services.employee_service import EmployeeService
from app.services.nudge_service import NudgeService


router = APIRouter(prefix="/adaptation", tags=["Adaptation"])


@router.get(
    "/context/{employee_id}",
    response_model=AdaptationContextResponse,
)
def get_adaptation_context(employee_id: int, db: Session = Depends(get_db)):
    employee = EmployeeService.get_by_id(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return AdaptationStageService.get_context(db, employee)


@router.post("/demo-setup/{employee_id}", response_model=ShiftAdaptationDayResponse)
def setup_adaptation_demo(employee_id: int, db: Session = Depends(get_db)):
    employee = EmployeeService.get_by_id(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    AdaptationStageService.ensure_adaptation_data(db, employee)
    adaptation_day = NudgeService.setup_adaptation_demo(db, employee)
    return {
        "success": True,
        "adaptation_day": adaptation_day,
        "nudge_day": min(adaptation_day, 23),
        "message": f"Этап «Адаптация»: день {adaptation_day}",
    }


@router.post("/touchpoints/{employee_id}")
def trigger_adaptation_touchpoints(employee_id: int, db: Session = Depends(get_db)):
    employee = EmployeeService.get_by_id(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return AdaptationStageService.process_login_touchpoints(db, employee)


def ensure_employee_exists(db: Session, employee_id: int):
    employee = EmployeeService.get_by_id(db, employee_id)

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    return employee


# --------------------
# Meetings
# --------------------

@router.get(
    "/employees/{employee_id}/meetings",
    response_model=list[OneToOneMeetingRead],
)
def get_employee_meetings(
    employee_id: int,
    db: Session = Depends(get_db),
):
    ensure_employee_exists(db, employee_id)
    return AdaptationService.get_meetings(db, employee_id)


@router.post(
    "/employees/{employee_id}/meetings",
    response_model=OneToOneMeetingRead,
    status_code=201,
)
def create_employee_meeting(
    employee_id: int,
    payload: OneToOneMeetingCreate,
    db: Session = Depends(get_db),
):
    ensure_employee_exists(db, employee_id)

    return AdaptationService.create_meeting(
        db=db,
        employee_id=employee_id,
        payload=payload,
    )


@router.patch(
    "/meetings/{meeting_id}",
    response_model=OneToOneMeetingRead,
)
def update_meeting(
    meeting_id: int,
    payload: OneToOneMeetingUpdate,
    db: Session = Depends(get_db),
):
    meeting = AdaptationService.get_meeting_by_id(db, meeting_id)

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    return AdaptationService.update_meeting(db, meeting, payload)


@router.delete("/meetings/{meeting_id}")
def delete_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
):
    meeting = AdaptationService.get_meeting_by_id(db, meeting_id)

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    AdaptationService.delete_meeting(db, meeting)

    return {
        "success": True,
        "message": "Meeting deleted successfully",
    }


# --------------------
# SMART goals
# --------------------

@router.get(
    "/employees/{employee_id}/goals",
    response_model=list[SmartGoalRead],
)
def get_employee_goals(
    employee_id: int,
    db: Session = Depends(get_db),
):
    ensure_employee_exists(db, employee_id)
    return AdaptationService.get_goals(db, employee_id)


@router.post(
    "/employees/{employee_id}/goals",
    response_model=SmartGoalRead,
    status_code=201,
)
def create_employee_goal(
    employee_id: int,
    payload: SmartGoalCreate,
    db: Session = Depends(get_db),
):
    ensure_employee_exists(db, employee_id)

    return AdaptationService.create_goal(
        db=db,
        employee_id=employee_id,
        payload=payload,
    )


@router.patch(
    "/goals/{goal_id}",
    response_model=SmartGoalRead,
)
def update_goal(
    goal_id: int,
    payload: SmartGoalUpdate,
    db: Session = Depends(get_db),
):
    goal = AdaptationService.get_goal_by_id(db, goal_id)

    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    return AdaptationService.update_goal(db, goal, payload)


@router.delete("/goals/{goal_id}")
def delete_goal(
    goal_id: int,
    db: Session = Depends(get_db),
):
    goal = AdaptationService.get_goal_by_id(db, goal_id)

    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    AdaptationService.delete_goal(db, goal)

    return {
        "success": True,
        "message": "Goal deleted successfully",
    }


# --------------------
# Learning modules
# --------------------

@router.get(
    "/employees/{employee_id}/learning-modules",
    response_model=list[LearningModuleRead],
)
def get_employee_learning_modules(
    employee_id: int,
    db: Session = Depends(get_db),
):
    ensure_employee_exists(db, employee_id)
    return AdaptationService.get_learning_modules(db, employee_id)


@router.post(
    "/employees/{employee_id}/learning-modules",
    response_model=LearningModuleRead,
    status_code=201,
)
def create_employee_learning_module(
    employee_id: int,
    payload: LearningModuleCreate,
    db: Session = Depends(get_db),
):
    ensure_employee_exists(db, employee_id)

    return AdaptationService.create_learning_module(
        db=db,
        employee_id=employee_id,
        payload=payload,
    )


@router.patch(
    "/learning-modules/{module_id}",
    response_model=LearningModuleRead,
)
def update_learning_module(
    module_id: int,
    payload: LearningModuleUpdate,
    db: Session = Depends(get_db),
):
    module = AdaptationService.get_learning_module_by_id(db, module_id)

    if not module:
        raise HTTPException(status_code=404, detail="Learning module not found")

    return AdaptationService.update_learning_module(db, module, payload)


@router.delete("/learning-modules/{module_id}")
def delete_learning_module(
    module_id: int,
    db: Session = Depends(get_db),
):
    module = AdaptationService.get_learning_module_by_id(db, module_id)

    if not module:
        raise HTTPException(status_code=404, detail="Learning module not found")

    AdaptationService.delete_learning_module(db, module)

    return {
        "success": True,
        "message": "Learning module deleted successfully",
    }
