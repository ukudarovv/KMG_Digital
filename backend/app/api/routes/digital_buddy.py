from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.digital_buddy import DigitalBuddyAnswer, DigitalBuddyQuestion
from app.services.digital_buddy_service import DigitalBuddyService
from app.services.employee_service import EmployeeService


router = APIRouter(prefix="/digital-buddy", tags=["Digital Buddy"])


@router.post("/ask", response_model=DigitalBuddyAnswer)
def ask_digital_buddy(
    payload: DigitalBuddyQuestion,
    db: Session = Depends(get_db),
):
    employee = EmployeeService.get_by_id(db, payload.employee_id)

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    return DigitalBuddyService.ask(
        db=db,
        employee_id=payload.employee_id,
        question=payload.question,
        preferred_language=payload.language,
    )


@router.get("/status")
def get_digital_buddy_status():
    return DigitalBuddyService.get_status()


@router.post("/reindex")
def reindex_digital_buddy_knowledge():
    return DigitalBuddyService.reindex_knowledge()
