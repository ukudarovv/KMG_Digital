from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.enums import OnboardingStage


class VndDocument(Base):
    __tablename__ = "vnd_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    file_name: Mapped[str | None] = mapped_column(String(512), nullable=True)
    bitrix_file_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stage: Mapped[OnboardingStage | None] = mapped_column(nullable=True)
    task_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    section_hint: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
