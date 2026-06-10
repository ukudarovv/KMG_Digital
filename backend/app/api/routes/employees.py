from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.employee import EmployeeCreate, EmployeeRead, EmployeeUpdate
from app.services.employee_service import EmployeeService


router = APIRouter(prefix="/employees", tags=["Employees"])


@router.get("", response_model=list[EmployeeRead])
def get_employees(db: Session = Depends(get_db)):
    return EmployeeService.get_all(db)


@router.get("/{employee_id}", response_model=EmployeeRead)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = EmployeeService.get_by_id(db, employee_id)

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    return employee


@router.post("", response_model=EmployeeRead, status_code=201)
def create_employee(
    payload: EmployeeCreate,
    db: Session = Depends(get_db),
):
    return EmployeeService.create(db, payload)


@router.patch("/{employee_id}", response_model=EmployeeRead)
def update_employee(
    employee_id: int,
    payload: EmployeeUpdate,
    db: Session = Depends(get_db),
):
    employee = EmployeeService.get_by_id(db, employee_id)

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    return EmployeeService.update(db, employee, payload)
