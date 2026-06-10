from datetime import datetime

from pydantic import BaseModel


class HrDocumentVersionRead(BaseModel):
    id: int
    version_no: int
    file_name: str
    uploaded_by: str | None = None
    comment: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class HrWorkflowStepBase(BaseModel):
    step_order: int
    role: str = "hr"
    approver_name: str | None = None


class HrWorkflowStepRead(HrWorkflowStepBase):
    id: int

    model_config = {"from_attributes": True}


class HrWorkflowCreate(BaseModel):
    name: str
    description: str | None = None
    steps: list[HrWorkflowStepBase]


class HrWorkflowRead(BaseModel):
    id: int
    name: str
    description: str | None = None
    is_active: bool
    steps: list[HrWorkflowStepRead] = []

    model_config = {"from_attributes": True}


class HrApprovalRead(BaseModel):
    id: int
    step_order: int
    decision: str
    actor: str | None = None
    comment: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class HrDocumentRead(BaseModel):
    id: int
    title: str
    doc_type: str
    status: str
    current_version_no: int
    owner_employee_id: int | None = None
    owner_employee_name: str | None = None
    created_at: datetime
    updated_at: datetime


class HrDocumentDetailRead(HrDocumentRead):
    versions: list[HrDocumentVersionRead] = []
    workflow_name: str | None = None
    current_step_order: int | None = None
    current_step_role: str | None = None
    workflow_steps: list[HrWorkflowStepRead] = []
    approvals: list[HrApprovalRead] = []


class HrDocumentSubmitRequest(BaseModel):
    workflow_id: int


class HrDocumentDecisionRequest(BaseModel):
    actor: str | None = None
    comment: str | None = None
