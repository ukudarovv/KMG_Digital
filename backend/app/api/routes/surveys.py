from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.survey import SurveyCreate, SurveyRead, SurveySummary, SurveyUpdate
from app.services.employee_service import EmployeeService
from app.services.survey_service import SurveyService


router = APIRouter(prefix="/surveys", tags=["Surveys"])


def ensure_employee_exists(db: Session, employee_id: int):
    employee = EmployeeService.get_by_id(db, employee_id)

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    return employee


@router.get(
    "/employees/{employee_id}",
    response_model=list[SurveyRead],
)
def get_employee_surveys(
    employee_id: int,
    db: Session = Depends(get_db),
):
    ensure_employee_exists(db, employee_id)
    return SurveyService.get_employee_surveys(db, employee_id)


@router.get(
    "/employees/{employee_id}/summary",
    response_model=SurveySummary,
)
def get_employee_survey_summary(
    employee_id: int,
    db: Session = Depends(get_db),
):
    ensure_employee_exists(db, employee_id)
    return SurveyService.get_summary(db, employee_id)


@router.post(
    "/employees/{employee_id}",
    response_model=SurveyRead,
    status_code=201,
)
def create_employee_survey(
    employee_id: int,
    payload: SurveyCreate,
    db: Session = Depends(get_db),
):
    employee = ensure_employee_exists(db, employee_id)

    try:
        SurveyService.validate_survey_day(employee, payload.survey_type)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return SurveyService.create_survey(
        db=db,
        employee_id=employee_id,
        payload=payload,
    )


@router.patch("/{survey_id}", response_model=SurveyRead)
def update_survey(
    survey_id: int,
    payload: SurveyUpdate,
    db: Session = Depends(get_db),
):
    survey = SurveyService.get_survey_by_id(db, survey_id)

    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")

    return SurveyService.update_survey(db, survey, payload)


@router.delete("/employees/{employee_id}/demo-reset")
def reset_engagement_surveys(employee_id: int, db: Session = Depends(get_db)):
    ensure_employee_exists(db, employee_id)
    deleted_count = SurveyService.reset_engagement_surveys(db, employee_id)
    return {
        "success": True,
        "deleted_count": deleted_count,
        "message": "Пульс-опрос и NPS сброшены для демо",
    }


@router.delete("/{survey_id}")
def delete_survey(
    survey_id: int,
    db: Session = Depends(get_db),
):
    survey = SurveyService.get_survey_by_id(db, survey_id)

    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")

    SurveyService.delete_survey(db, survey)

    return {
        "success": True,
        "message": "Survey deleted successfully",
    }
