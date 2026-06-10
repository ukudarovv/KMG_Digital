from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class NudgeDelivery(Base):
    __tablename__ = "nudge_deliveries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    nudge_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("culture_fit_nudges.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    delivery_date: Mapped[date] = mapped_column(Date, nullable=False)
    sent_to_popup: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sent_to_chat: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    employee = relationship("Employee", back_populates="nudge_deliveries")
    nudge = relationship("CultureFitNudge", back_populates="deliveries")
