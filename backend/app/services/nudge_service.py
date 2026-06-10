from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models.culture_fit_nudge import CultureFitNudge
from app.models.employee import Employee
from app.models.nudge_delivery import NudgeDelivery
from app.services.vnd_service import SOURCE_TO_VND_CODE


DEFAULT_NUDGES = [
    {
        "day_number": 1,
        "title": "Деловой внешний вид",
        "text": "Соблюдайте корпоративный дресс-код: аккуратность, сдержанность, деловой стиль.",
        "source": "Правила дресс-кода",
    },
    {
        "day_number": 2,
        "title": "Корректность и уважение",
        "text": "Общайтесь профессионально, уважительно, избегайте фамильярности.",
        "source": "Кодекс этики",
    },
    {
        "day_number": 3,
        "title": "Дисциплина и рабочее время",
        "text": "Приходите вовремя, соблюдайте график, эффективно используйте рабочее время.",
        "source": "ПВТР",
    },
    {
        "day_number": 4,
        "title": "Уведомление руководителя",
        "text": "Сообщайте о планируемом отсутствии или опоздании заранее.",
        "source": "ПВТР",
    },
    {
        "day_number": 5,
        "title": "Уточнение поручений",
        "text": "Если поручение неясно — задайте вопрос сразу.",
        "source": "ПВТР",
    },
    {
        "day_number": 6,
        "title": "Корпоративная переписка",
        "text": "Пишите кратко, корректно, уважительно; соблюдайте деловой стиль.",
        "source": "Кодекс этики",
    },
    {
        "day_number": 7,
        "title": "Эффективные совещания",
        "text": "Готовьтесь заранее, уважайте повестку, говорите по существу.",
        "source": "Кодекс этики",
    },
    {
        "day_number": 8,
        "title": "Умение слушать",
        "text": "Слушайте коллег внимательно, не перебивайте.",
        "source": "Кодекс этики",
    },
    {
        "day_number": 9,
        "title": "Работа с документами",
        "text": "Используйте корпоративные шаблоны, проверяйте оформление.",
        "source": "ПВТР",
    },
    {
        "day_number": 10,
        "title": "Конфиденциальность",
        "text": "Не оставляйте документы без присмотра, не обсуждайте рабочие темы вне офиса.",
        "source": "ПВТР",
    },
    {
        "day_number": 11,
        "title": "Проверка получателей",
        "text": "Перед отправкой писем проверяйте правильность адресатов.",
        "source": "ПВТР",
    },
    {
        "day_number": 12,
        "title": "Прозрачность поведения",
        "text": "При сомнениях обращайтесь к руководителю или Комплаенс.",
        "source": "Комплаенс",
    },
    {
        "day_number": 13,
        "title": "Конфликты интересов",
        "text": "Сообщайте о пересечениях личных и рабочих интересов.",
        "source": "Комплаенс",
    },
    {
        "day_number": 14,
        "title": "Представительство от КМГ",
        "text": "Нельзя выступать от имени компании без официальных полномочий.",
        "source": "Кодекс этики",
    },
    {
        "day_number": 15,
        "title": "Инструктажи и безопасность",
        "text": "Соблюдайте правила ТБ/ПБ/ИБ — это часть вашей ответственности.",
        "source": "ПВТР",
    },
    {
        "day_number": 16,
        "title": "Запрет на агрессию и опьянение",
        "text": "Опьянение и угрожающие действия строго запрещены.",
        "source": "ПВТР",
    },
    {
        "day_number": 17,
        "title": "Офисный этикет",
        "text": "Поддерживайте порядок в офисе и бережно относитесь к имуществу.",
        "source": "ПВТР",
    },
    {
        "day_number": 18,
        "title": "Репутация сотрудника",
        "text": "Ваше поведение влияет на репутацию КМГ и доверие коллег.",
        "source": "Кодекс этики",
    },
    {
        "day_number": 19,
        "title": "Профессиональное развитие",
        "text": "Поддерживайте и развивайте свои профессиональные навыки.",
        "source": "Кодекс этики",
    },
    {
        "day_number": 20,
        "title": "Smart Casual по пятницам",
        "text": "Более свободный стиль допускается, но в рамках корпоративных норм.",
        "source": "Правила дресс-кода",
    },
    {
        "day_number": 21,
        "title": "Корректность при звонках",
        "text": "Говорите вежливо, представляйесь, соблюдайте деловой тон.",
        "source": "Кодекс этики",
    },
    {
        "day_number": 22,
        "title": "Обновление личных данных",
        "text": "При смене персональных данных своевременно уведомляйте HR.",
        "source": "ПВТР",
    },
    {
        "day_number": 23,
        "title": "Материальная ответственность",
        "text": "Бережно относитесь к ресурсам компании — за причинённый ущерб предусмотрена материальная ответственность.",
        "source": "ПВТР",
    },
]


class NudgeService:
    @staticmethod
    def seed_default_nudges(db: Session) -> None:
        existing_count = db.query(CultureFitNudge).count()

        if existing_count > 0:
            NudgeService.sync_existing_nudge_codes(db)
            return

        for item in DEFAULT_NUDGES:
            payload = dict(item)
            payload["vnd_document_code"] = SOURCE_TO_VND_CODE.get(item["source"])
            db.add(CultureFitNudge(**payload))

        db.commit()

    @staticmethod
    def sync_existing_nudge_codes(db: Session) -> None:
        for nudge in db.query(CultureFitNudge).all():
            code = SOURCE_TO_VND_CODE.get(nudge.source)
            if code and nudge.vnd_document_code != code:
                nudge.vnd_document_code = code
        db.commit()

    @staticmethod
    def get_all(db: Session) -> list[CultureFitNudge]:
        return (
            db.query(CultureFitNudge)
            .filter(CultureFitNudge.is_active == True)
            .order_by(CultureFitNudge.day_number.asc())
            .all()
        )

    @staticmethod
    def calculate_adaptation_day(employee: Employee) -> int:
        today = date.today()
        delta = today - employee.start_date

        return max(delta.days + 1, 1)

    @staticmethod
    def get_current_nudge(
        db: Session,
        employee: Employee,
    ) -> tuple[CultureFitNudge | None, bool, int]:
        adaptation_day = NudgeService.calculate_adaptation_day(employee)
        nudge_day = min(adaptation_day, 23)

        today = date.today()

        delivery = (
            db.query(NudgeDelivery)
            .filter(
                NudgeDelivery.employee_id == employee.id,
                NudgeDelivery.delivery_date == today,
            )
            .first()
        )

        already_sent_today = delivery is not None

        nudge = (
            db.query(CultureFitNudge)
            .filter(CultureFitNudge.day_number == nudge_day)
            .first()
        )

        return nudge, already_sent_today, adaptation_day

    @staticmethod
    def send_nudge_to_chat(
        db: Session,
        employee: Employee,
    ) -> NudgeDelivery:
        nudge, _already_sent_today, _adaptation_day = NudgeService.get_current_nudge(
            db,
            employee,
        )

        if not nudge:
            raise ValueError("Nudge not found")

        today = date.today()

        existing_delivery = (
            db.query(NudgeDelivery)
            .filter(
                NudgeDelivery.employee_id == employee.id,
                NudgeDelivery.delivery_date == today,
            )
            .first()
        )

        if existing_delivery:
            return existing_delivery

        delivery = NudgeDelivery(
            employee_id=employee.id,
            nudge_id=nudge.id,
            delivery_date=today,
            sent_to_popup=True,
            sent_to_chat=True,
        )

        db.add(delivery)
        db.commit()
        db.refresh(delivery)

        from app.integrations.bitrix.service import BitrixService

        BitrixService.send_nudge_message(employee, nudge.title, nudge.text, nudge.source)

        return delivery

    @staticmethod
    def set_adaptation_day(db: Session, employee: Employee, target_day: int) -> int:
        clamped_day = max(1, min(target_day, 90))
        employee.start_date = date.today() - timedelta(days=clamped_day - 1)
        NudgeService.reset_today_delivery(db, employee)
        db.commit()
        db.refresh(employee)
        return clamped_day

    @staticmethod
    def shift_adaptation_day(
        db: Session,
        employee: Employee,
        *,
        target_day: int | None = None,
        delta: int | None = None,
    ) -> int:
        current_day = NudgeService.calculate_adaptation_day(employee)

        if target_day is not None:
            new_day = target_day
        elif delta is not None:
            new_day = current_day + delta
        else:
            new_day = current_day

        return NudgeService.set_adaptation_day(db, employee, new_day)

    @staticmethod
    def setup_engagement_demo(db: Session, employee: Employee) -> int:
        from app.services.survey_service import SurveyService

        SurveyService.reset_engagement_surveys(db, employee.id)
        current_day = NudgeService.calculate_adaptation_day(employee)
        if current_day < 2:
            return NudgeService.set_adaptation_day(db, employee, 2)
        return current_day

    @staticmethod
    def setup_adaptation_demo(db: Session, employee: Employee) -> int:
        current_day = NudgeService.calculate_adaptation_day(employee)
        if current_day < 31:
            return NudgeService.set_adaptation_day(db, employee, 35)
        return current_day

    @staticmethod
    def reset_today_delivery(
        db: Session,
        employee: Employee,
    ) -> int:
        today = date.today()

        deleted_count = (
            db.query(NudgeDelivery)
            .filter(
                NudgeDelivery.employee_id == employee.id,
                NudgeDelivery.delivery_date == today,
            )
            .delete()
        )

        db.commit()

        return deleted_count
