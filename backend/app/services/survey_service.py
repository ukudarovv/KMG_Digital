from sqlalchemy.orm import Session

from app.models.employee import Employee  # used in create_survey HR notify
from app.models.enums import SurveyType
from app.models.survey import Survey
from app.schemas.survey import SurveyCreate, SurveyUpdate
from app.services.nudge_service import NudgeService


class SurveyService:
    @staticmethod
    def get_employee_surveys(db: Session, employee_id: int) -> list[Survey]:
        return (
            db.query(Survey)
            .filter(Survey.employee_id == employee_id)
            .order_by(Survey.created_at.desc())
            .all()
        )

    @staticmethod
    def get_survey_by_id(db: Session, survey_id: int) -> Survey | None:
        return db.query(Survey).filter(Survey.id == survey_id).first()

    @staticmethod
    def validate_survey_day(employee: Employee, survey_type: SurveyType) -> None:
        adaptation_day = NudgeService.calculate_adaptation_day(employee)

        if survey_type == SurveyType.pulse_day_14 and adaptation_day < 14:
            raise ValueError("Пульс-опрос доступен с 14-го дня адаптации")
        if survey_type == SurveyType.nps_day_30 and adaptation_day < 30:
            raise ValueError("NPS-опрос доступен с 30-го дня адаптации")

    @staticmethod
    def reset_engagement_surveys(db: Session, employee_id: int) -> int:
        deleted_count = (
            db.query(Survey)
            .filter(
                Survey.employee_id == employee_id,
                Survey.survey_type.in_(
                    [SurveyType.pulse_day_14, SurveyType.nps_day_30]
                ),
            )
            .delete()
        )
        db.commit()
        return deleted_count

    @staticmethod
    def create_survey(
        db: Session,
        employee_id: int,
        payload: SurveyCreate,
    ) -> Survey:
        survey = Survey(
            employee_id=employee_id,
            **payload.model_dump(),
        )

        db.add(survey)
        db.commit()
        db.refresh(survey)

        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if employee and survey.survey_type.value in {
            "pulse_day_14",
            "nps_day_30",
        }:
            from app.services.engagement_service import EngagementService

            EngagementService.notify_hr_about_survey(db, employee, survey)

        return survey

    @staticmethod
    def update_survey(
        db: Session,
        survey: Survey,
        payload: SurveyUpdate,
    ) -> Survey:
        update_data = payload.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(survey, field, value)

        db.commit()
        db.refresh(survey)

        return survey

    @staticmethod
    def delete_survey(db: Session, survey: Survey) -> None:
        db.delete(survey)
        db.commit()

    @staticmethod
    def get_summary(db: Session, employee_id: int) -> dict:
        surveys = SurveyService.get_employee_surveys(db, employee_id)

        latest_nps = None

        for survey in surveys:
            if survey.nps_score is not None:
                latest_nps = survey.nps_score
                break

        return {
            "pulse_day_14_completed": any(
                survey.survey_type.value == "pulse_day_14" for survey in surveys
            ),
            "nps_day_30_completed": any(
                survey.survey_type.value == "nps_day_30" for survey in surveys
            ),
            "final_nps_completed": any(
                survey.survey_type.value == "final_nps" for survey in surveys
            ),
            "latest_nps": latest_nps,
        }
