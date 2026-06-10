from datetime import date, datetime, time

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, Time, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import MeetingStatus


class OneToOneMeeting(Base):
    __tablename__ = "one_to_one_meetings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    meeting_date: Mapped[date] = mapped_column(Date, nullable=False)
    meeting_time: Mapped[time | None] = mapped_column(Time, nullable=True)

    status: Mapped[MeetingStatus] = mapped_column(
        default=MeetingStatus.planned,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    employee = relationship("Employee", back_populates="one_to_one_meetings")
