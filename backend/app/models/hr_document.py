from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class HrDocument(Base):
    __tablename__ = "hr_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    doc_type: Mapped[str] = mapped_column(String(128), default="other", nullable=False)
    owner_employee_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("employees.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    # draft -> in_review -> approved / rejected -> signed -> archived
    status: Mapped[str] = mapped_column(String(50), default="draft", nullable=False)
    current_version_no: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
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

    owner_employee = relationship("Employee")
    versions = relationship(
        "HrDocumentVersion",
        back_populates="document",
        cascade="all, delete-orphan",
        order_by="HrDocumentVersion.version_no",
    )
    instances = relationship(
        "HrDocumentInstance",
        back_populates="document",
        cascade="all, delete-orphan",
    )


class HrDocumentVersion(Base):
    __tablename__ = "hr_document_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    document_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("hr_documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version_no: Mapped[int] = mapped_column(Integer, nullable=False)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    file_name: Mapped[str] = mapped_column(String(512), nullable=False)
    uploaded_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    document = relationship("HrDocument", back_populates="versions")


class HrDocumentWorkflow(Base):
    __tablename__ = "hr_document_workflows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    steps = relationship(
        "HrDocumentWorkflowStep",
        back_populates="workflow",
        cascade="all, delete-orphan",
        order_by="HrDocumentWorkflowStep.step_order",
    )


class HrDocumentWorkflowStep(Base):
    __tablename__ = "hr_document_workflow_steps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    workflow_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("hr_document_workflows.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    # hr / manager / employee / signer
    role: Mapped[str] = mapped_column(String(50), default="hr", nullable=False)
    approver_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    workflow = relationship("HrDocumentWorkflow", back_populates="steps")


class HrDocumentInstance(Base):
    __tablename__ = "hr_document_instances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    document_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("hr_documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    workflow_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("hr_document_workflows.id", ondelete="CASCADE"),
        nullable=False,
    )
    employee_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("employees.id", ondelete="SET NULL"),
        nullable=True,
    )
    current_step_order: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    # active / completed / rejected
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

    document = relationship("HrDocument", back_populates="instances")
    workflow = relationship("HrDocumentWorkflow")
    approvals = relationship(
        "HrDocumentApproval",
        back_populates="instance",
        cascade="all, delete-orphan",
        order_by="HrDocumentApproval.created_at",
    )


class HrDocumentApproval(Base):
    __tablename__ = "hr_document_approvals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    instance_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("hr_document_instances.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    # approved / rejected / signed
    decision: Mapped[str] = mapped_column(String(50), nullable=False)
    actor: Mapped[str | None] = mapped_column(String(255), nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    instance = relationship("HrDocumentInstance", back_populates="approvals")
