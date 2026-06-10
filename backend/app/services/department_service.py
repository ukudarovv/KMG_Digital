from sqlalchemy.orm import Session

from app.models.department import Department
from app.schemas.department import DepartmentCreate, DepartmentUpdate

DEFAULT_DEPARTMENTS = [
    {
        "code": "PROCUREMENT",
        "name": "Департамент закупок",
        "description": "Организация закупочных процедур, договорная работа с поставщиками.",
        "competencies": "закупки, тендеры, госзакупки, договоры, снабжение, логистика, SAP MM, анализ поставщиков",
    },
    {
        "code": "HR",
        "name": "Департамент управления персоналом",
        "description": "Подбор, адаптация, обучение и развитие персонала.",
        "competencies": "рекрутинг, подбор персонала, адаптация, обучение, кадровое делопроизводство, HR-аналитика, компенсации и льготы",
    },
    {
        "code": "IT",
        "name": "Департамент информационных технологий",
        "description": "Разработка и поддержка ИТ-систем, инфраструктура, информационная безопасность.",
        "competencies": "разработка ПО, Python, Java, SQL, DevOps, сети, информационная безопасность, поддержка пользователей, 1С, SAP",
    },
    {
        "code": "FINANCE",
        "name": "Финансовый департамент",
        "description": "Бюджетирование, отчётность, казначейство и финансовый контроль.",
        "competencies": "бухгалтерия, МСФО, бюджетирование, финансовый анализ, казначейство, аудит, налоги, Excel",
    },
    {
        "code": "LEGAL",
        "name": "Юридический департамент",
        "description": "Правовое сопровождение деятельности компании.",
        "competencies": "юриспруденция, договорное право, корпоративное право, претензионная работа, комплаенс",
    },
    {
        "code": "PRODUCTION",
        "name": "Производственный департамент",
        "description": "Добыча, переработка и транспортировка нефти и газа.",
        "competencies": "нефтегаз, добыча, бурение, переработка, геология, промышленная безопасность, инженерия, КИПиА",
    },
]


class DepartmentService:
    @staticmethod
    def get_all(db: Session, include_inactive: bool = True) -> list[Department]:
        query = db.query(Department)
        if not include_inactive:
            query = query.filter(Department.is_active.is_(True))
        return query.order_by(Department.name.asc()).all()

    @staticmethod
    def get_by_id(db: Session, department_id: int) -> Department | None:
        return db.query(Department).filter(Department.id == department_id).first()

    @staticmethod
    def create(db: Session, payload: DepartmentCreate) -> Department:
        department = Department(**payload.model_dump())
        db.add(department)
        db.commit()
        db.refresh(department)
        return department

    @staticmethod
    def update(
        db: Session,
        department: Department,
        payload: DepartmentUpdate,
    ) -> Department:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(department, field, value)
        db.commit()
        db.refresh(department)
        return department

    @staticmethod
    def ensure_default_departments(db: Session) -> None:
        if db.query(Department).count() > 0:
            return
        for item in DEFAULT_DEPARTMENTS:
            db.add(Department(**item))
        db.commit()
