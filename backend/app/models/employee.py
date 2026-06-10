from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    bitrix_user_id: Mapped[int | None] = mapped_column(Integer, unique=True, nullable=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    position: Mapped[str | None] = mapped_column(String(255), nullable=True)
    department: Mapped[str | None] = mapped_column(String(255), nullable=True)
    department_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
    )
    candidate_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("candidates.id", ondelete="SET NULL"),
        nullable=True,
    )
    manager_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="ru", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    department_ref = relationship("Department", back_populates="employees")
    tasks = relationship("OnboardingTask", back_populates="employee")
    nudge_deliveries = relationship("NudgeDelivery", back_populates="employee")
    chat_messages = relationship("ChatMessage", back_populates="employee")
    onboarding_routes = relationship("OnboardingRoute", back_populates="employee")
    risk_flags = relationship("RiskFlag", back_populates="employee")
    surveys = relationship("Survey", back_populates="employee")
    one_to_one_meetings = relationship(
        "OneToOneMeeting",
        back_populates="employee",
        cascade="all, delete-orphan",
    )
    smart_goals = relationship(
        "SmartGoal",
        back_populates="employee",
        cascade="all, delete-orphan",
    )
    learning_modules = relationship(
        "LearningModule",
        back_populates="employee",
        cascade="all, delete-orphan",
    )
    development_recommendations = relationship(
        "DevelopmentRecommendation",
        back_populates="employee",
        cascade="all, delete-orphan",
    )
