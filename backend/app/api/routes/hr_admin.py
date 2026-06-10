from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.department import DepartmentCreate, DepartmentRead, DepartmentUpdate
from app.schemas.employee import EmployeeCreate, EmployeeRead, EmployeeUpdate
from app.services.department_service import DepartmentService
from app.services.employee_service import EmployeeService

router = APIRouter(prefix="/hr", tags=["HR Admin"])


@router.get("/departments", response_model=list[DepartmentRead])
def get_departments(db: Session = Depends(get_db)):
    return DepartmentService.get_all(db)


@router.post("/departments", response_model=DepartmentRead, status_code=201)
def create_department(payload: DepartmentCreate, db: Session = Depends(get_db)):
    return DepartmentService.create(db, payload)


@router.patch("/departments/{department_id}", response_model=DepartmentRead)
def update_department(
    department_id: int,
    payload: DepartmentUpdate,
    db: Session = Depends(get_db),
):
    department = DepartmentService.get_by_id(db, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    return DepartmentService.update(db, department, payload)


@router.post("/employees", response_model=EmployeeRead, status_code=201)
def create_employee_with_provisioning(
    payload: EmployeeCreate,
    db: Session = Depends(get_db),
):
    """Создание сотрудника HR-ом: профиль + маршрут онбординга + задачи Дня 1."""
    return EmployeeService.create(db, payload)


@router.patch("/employees/{employee_id}", response_model=EmployeeRead)
def update_employee_profile(
    employee_id: int,
    payload: EmployeeUpdate,
    db: Session = Depends(get_db),
):
    employee = EmployeeService.get_by_id(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return EmployeeService.update(db, employee, payload)
