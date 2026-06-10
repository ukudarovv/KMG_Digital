from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source: Mapped[str] = mapped_column(String(50), default="manual", nullable=False)
    # new -> analyzed -> hired / rejected
    status: Mapped[str] = mapped_column(String(50), default="new", nullable=False)
    consent_given: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    confirmed_department_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
    )
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

    resumes = relationship(
        "Resume",
        back_populates="candidate",
        cascade="all, delete-orphan",
    )
    confirmed_department = relationship("Department")


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    candidate_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    file_name: Mapped[str] = mapped_column(String(512), nullable=False)
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    candidate = relationship("Candidate", back_populates="resumes")
    analyses = relationship(
        "ResumeAnalysis",
        back_populates="resume",
        cascade="all, delete-orphan",
    )


class ResumeAnalysis(Base):
    __tablename__ = "resume_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    resume_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    parsed_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    llm_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    resume = relationship("Resume", back_populates="analyses")
    department_matches = relationship(
        "DepartmentMatch",
        back_populates="analysis",
        cascade="all, delete-orphan",
    )


class DepartmentMatch(Base):
    __tablename__ = "department_matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    analysis_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("resume_analyses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    department_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("departments.id", ondelete="CASCADE"),
        nullable=False,
    )
    score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    rank: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    # Решение внешнего скрининга: pass / review / reject
    decision: Mapped[str | None] = mapped_column(String(20), nullable=True)

    analysis = relationship("ResumeAnalysis", back_populates="department_matches")
    department = relationship("Department")


class RecruitingSettings(Base):
    __tablename__ = "recruiting_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    prompt_template: Mapped[str | None] = mapped_column(Text, nullable=True)
    min_score: Mapped[int] = mapped_column(Integer, default=40, nullable=False)
    top_n: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    llm_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
