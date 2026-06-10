from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.hr_dashboard import (
    HRDashboardResponse,
    HREmployeeDashboardItem,
    HREmployeeDetailResponse,
)
from app.services.hr_dashboard_service import HRDashboardService


router = APIRouter(prefix="/hr", tags=["HR Dashboard"])


@router.get("/employees", response_model=HRDashboardResponse)
def get_hr_dashboard(db: Session = Depends(get_db)):
    return HRDashboardService.get_dashboard(db)


@router.get("/employees/{employee_id}", response_model=HREmployeeDashboardItem)
def get_hr_employee_detail(
    employee_id: int,
    db: Session = Depends(get_db),
):
    employee = HRDashboardService.get_employee_detail(db, employee_id)

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    return employee


@router.get(
    "/employees/{employee_id}/detail",
    response_model=HREmployeeDetailResponse,
)
def get_hr_employee_full_detail(
    employee_id: int,
    db: Session = Depends(get_db),
):
    employee_detail = HRDashboardService.get_employee_full_detail(
        db,
        employee_id,
    )

    if not employee_detail:
        raise HTTPException(status_code=404, detail="Employee not found")

    return employee_detail
