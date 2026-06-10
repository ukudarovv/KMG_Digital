from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import LearningModuleStatus


class LearningModule(Base):
    __tablename__ = "learning_modules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)

    deadline: Mapped[date] = mapped_column(Date, nullable=False)

    progress: Mapped[int] = mapped_column(Integer, default=0)

    status: Mapped[LearningModuleStatus] = mapped_column(
        default=LearningModuleStatus.not_started,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    employee = relationship("Employee", back_populates="learning_modules")
