from sqlalchemy.orm import Session

from app.models.learning_module import LearningModule
from app.models.one_to_one_meeting import OneToOneMeeting
from app.models.smart_goal import SmartGoal
from app.schemas.adaptation import (
    LearningModuleCreate,
    LearningModuleUpdate,
    OneToOneMeetingCreate,
    OneToOneMeetingUpdate,
    SmartGoalCreate,
    SmartGoalUpdate,
)


class AdaptationService:
    # --------------------
    # Meetings
    # --------------------

    @staticmethod
    def get_meetings(db: Session, employee_id: int) -> list[OneToOneMeeting]:
        return (
            db.query(OneToOneMeeting)
            .filter(OneToOneMeeting.employee_id == employee_id)
            .order_by(OneToOneMeeting.meeting_date.asc())
            .all()
        )

    @staticmethod
    def get_meeting_by_id(
        db: Session,
        meeting_id: int,
    ) -> OneToOneMeeting | None:
        return (
            db.query(OneToOneMeeting)
            .filter(OneToOneMeeting.id == meeting_id)
            .first()
        )

    @staticmethod
    def create_meeting(
        db: Session,
        employee_id: int,
        payload: OneToOneMeetingCreate,
    ) -> OneToOneMeeting:
        meeting = OneToOneMeeting(
            employee_id=employee_id,
            **payload.model_dump(),
        )

        db.add(meeting)
        db.commit()
        db.refresh(meeting)

        return meeting

    @staticmethod
    def update_meeting(
        db: Session,
        meeting: OneToOneMeeting,
        payload: OneToOneMeetingUpdate,
    ) -> OneToOneMeeting:
        update_data = payload.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(meeting, field, value)

        db.commit()
        db.refresh(meeting)

        return meeting

    @staticmethod
    def delete_meeting(db: Session, meeting: OneToOneMeeting) -> None:
        db.delete(meeting)
        db.commit()

    # --------------------
    # SMART goals
    # --------------------

    @staticmethod
    def get_goals(db: Session, employee_id: int) -> list[SmartGoal]:
        return (
            db.query(SmartGoal)
            .filter(SmartGoal.employee_id == employee_id)
            .order_by(SmartGoal.deadline.asc())
            .all()
        )

    @staticmethod
    def get_goal_by_id(db: Session, goal_id: int) -> SmartGoal | None:
        return db.query(SmartGoal).filter(SmartGoal.id == goal_id).first()

    @staticmethod
    def create_goal(
        db: Session,
        employee_id: int,
        payload: SmartGoalCreate,
    ) -> SmartGoal:
        goal = SmartGoal(
            employee_id=employee_id,
            **payload.model_dump(),
        )

        db.add(goal)
        db.commit()
        db.refresh(goal)

        return goal

    @staticmethod
    def update_goal(
        db: Session,
        goal: SmartGoal,
        payload: SmartGoalUpdate,
    ) -> SmartGoal:
        update_data = payload.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(goal, field, value)

        db.commit()
        db.refresh(goal)

        return goal

    @staticmethod
    def delete_goal(db: Session, goal: SmartGoal) -> None:
        db.delete(goal)
        db.commit()

    # --------------------
    # Learning modules
    # --------------------

    @staticmethod
    def get_learning_modules(
        db: Session,
        employee_id: int,
    ) -> list[LearningModule]:
        return (
            db.query(LearningModule)
            .filter(LearningModule.employee_id == employee_id)
            .order_by(LearningModule.deadline.asc())
            .all()
        )

    @staticmethod
    def get_learning_module_by_id(
        db: Session,
        module_id: int,
    ) -> LearningModule | None:
        return (
            db.query(LearningModule)
            .filter(LearningModule.id == module_id)
            .first()
        )

    @staticmethod
    def create_learning_module(
        db: Session,
        employee_id: int,
        payload: LearningModuleCreate,
    ) -> LearningModule:
        module = LearningModule(
            employee_id=employee_id,
            **payload.model_dump(),
        )

        db.add(module)
        db.commit()
        db.refresh(module)

        return module

    @staticmethod
    def update_learning_module(
        db: Session,
        module: LearningModule,
        payload: LearningModuleUpdate,
    ) -> LearningModule:
        update_data = payload.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(module, field, value)

        db.commit()
        db.refresh(module)

        return module

    @staticmethod
    def delete_learning_module(db: Session, module: LearningModule) -> None:
        db.delete(module)
        db.commit()
