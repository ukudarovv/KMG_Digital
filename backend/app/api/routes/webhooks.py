from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.integrations.bitrix.service import BitrixService
from app.services.employee_service import EmployeeService
from app.services.nudge_service import NudgeService

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/on-user-login/{employee_id}")
def on_user_login(employee_id: int, db: Session = Depends(get_db)):
    employee = EmployeeService.get_by_id(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    NudgeService.seed_default_nudges(db)
    return {"success": True, "popup": BitrixService.handle_user_login(db, employee)}


@router.post("/on-user-login/bitrix/{bitrix_user_id}")
def on_user_login_by_bitrix_id(bitrix_user_id: int, db: Session = Depends(get_db)):
    employee = EmployeeService.get_by_bitrix_user_id(db, bitrix_user_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    NudgeService.seed_default_nudges(db)
    return {"success": True, "popup": BitrixService.handle_user_login(db, employee)}
