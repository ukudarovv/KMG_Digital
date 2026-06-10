from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.employee import Employee
from app.schemas.risk_engine import RiskEngineAnalyzeResponse
from app.services.employee_service import EmployeeService
from app.services.risk_engine_service import RiskEngineService


router = APIRouter(prefix="/risk-engine", tags=["Risk Engine"])


@router.post(
    "/employees/{employee_id}/analyze",
    response_model=RiskEngineAnalyzeResponse,
)
def analyze_employee_risks(
    employee_id: int,
    db: Session = Depends(get_db),
):
    employee = EmployeeService.get_by_id(db, employee_id)

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    return RiskEngineService.analyze_employee(db, employee_id)


@router.post("/analyze-all")
def analyze_all_employees_risks(
    db: Session = Depends(get_db),
):
    employees = db.query(Employee).all()

    results = []

    for employee in employees:
        result = RiskEngineService.analyze_employee(
            db=db,
            employee_id=employee.id,
        )
        results.append(result)

    return {
        "success": True,
        "employees_count": len(employees),
        "results": results,
    }
