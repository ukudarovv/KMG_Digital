from sqlalchemy.orm import Session

from app.models.department import Department
from app.models.employee import Employee
from app.models.enums import OnboardingStage
from app.models.onboarding_route import OnboardingRoute
from app.schemas.employee import EmployeeCreate, EmployeeUpdate


class EmployeeService:
    @staticmethod
    def get_all(db: Session) -> list[Employee]:
        return db.query(Employee).order_by(Employee.id.desc()).all()

    @staticmethod
    def get_by_id(db: Session, employee_id: int) -> Employee | None:
        return db.query(Employee).filter(Employee.id == employee_id).first()

    @staticmethod
    def get_by_bitrix_user_id(db: Session, bitrix_user_id: int) -> Employee | None:
        return (
            db.query(Employee)
            .filter(Employee.bitrix_user_id == bitrix_user_id)
            .first()
        )

    @staticmethod
    def _sync_department_name(db: Session, data: dict) -> dict:
        department_id = data.get("department_id")
        if department_id:
            department = (
                db.query(Department).filter(Department.id == department_id).first()
            )
            if department:
                data["department"] = department.name
        return data

    @staticmethod
    def create(db: Session, payload: EmployeeCreate) -> Employee:
        data = EmployeeService._sync_department_name(db, payload.model_dump())
        employee = Employee(**data)

        db.add(employee)
        db.commit()
        db.refresh(employee)

        EmployeeService.provision_onboarding(db, employee)

        return employee

    @staticmethod
    def provision_onboarding(db: Session, employee: Employee) -> None:
        """Создаёт маршрут онбординга и стартовые задачи для нового сотрудника."""
        from app.services.task_service import TaskService

        TaskService.ensure_day_one_tasks(db, employee)

        has_route = (
            db.query(OnboardingRoute)
            .filter(OnboardingRoute.employee_id == employee.id)
            .first()
        )
        if not has_route:
            db.add(
                OnboardingRoute(
                    employee_id=employee.id,
                    current_stage=OnboardingStage.introduction,
                )
            )
            db.commit()

    @staticmethod
    def update(
        db: Session,
        employee: Employee,
        payload: EmployeeUpdate,
    ) -> Employee:
        update_data = EmployeeService._sync_department_name(
            db, payload.model_dump(exclude_unset=True)
        )

        for field, value in update_data.items():
            setattr(employee, field, value)

        db.commit()
        db.refresh(employee)

        return employee
