from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.hr_document import HrDocument
from app.schemas.hr_document import (
    HrApprovalRead,
    HrDocumentDecisionRequest,
    HrDocumentDetailRead,
    HrDocumentRead,
    HrDocumentSubmitRequest,
    HrDocumentVersionRead,
    HrWorkflowCreate,
    HrWorkflowRead,
    HrWorkflowStepRead,
)
from app.services.hr_document_service import (
    ALLOWED_EXTENSIONS,
    MAX_FILE_SIZE,
    HrDocumentService,
)

router = APIRouter(prefix="/hr/documents", tags=["HR Documents"])


def _validate_upload(file: UploadFile, content: bytes) -> None:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Недопустимый формат файла. Разрешены: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Файл превышает лимит 10 МБ.")
    if not content:
        raise HTTPException(status_code=400, detail="Пустой файл.")


def _to_read(document: HrDocument) -> HrDocumentRead:
    return HrDocumentRead(
        id=document.id,
        title=document.title,
        doc_type=document.doc_type,
        status=document.status,
        current_version_no=document.current_version_no,
        owner_employee_id=document.owner_employee_id,
        owner_employee_name=(
            document.owner_employee.full_name if document.owner_employee else None
        ),
        created_at=document.created_at,
        updated_at=document.updated_at,
    )


def _to_detail(db: Session, document: HrDocument) -> HrDocumentDetailRead:
    base = _to_read(document)
    instance = HrDocumentService.get_active_instance(db, document)
    if not instance and document.instances:
        instance = document.instances[-1]

    workflow_steps: list[HrWorkflowStepRead] = []
    approvals: list[HrApprovalRead] = []
    workflow_name = None
    current_step_order = None
    current_step_role = None

    if instance:
        workflow_name = instance.workflow.name
        current_step_order = instance.current_step_order
        steps = sorted(instance.workflow.steps, key=lambda step: step.step_order)
        workflow_steps = [HrWorkflowStepRead.model_validate(step) for step in steps]
        current_step = next(
            (step for step in steps if step.step_order == instance.current_step_order),
            None,
        )
        current_step_role = current_step.role if current_step else None
        approvals = [
            HrApprovalRead.model_validate(approval) for approval in instance.approvals
        ]

    return HrDocumentDetailRead(
        **base.model_dump(),
        versions=[
            HrDocumentVersionRead.model_validate(version)
            for version in document.versions
        ],
        workflow_name=workflow_name,
        current_step_order=current_step_order,
        current_step_role=current_step_role,
        workflow_steps=workflow_steps,
        approvals=approvals,
    )


@router.get("/workflows", response_model=list[HrWorkflowRead])
def get_workflows(db: Session = Depends(get_db)):
    return HrDocumentService.get_workflows(db)


@router.post("/workflows", response_model=HrWorkflowRead, status_code=201)
def create_workflow(payload: HrWorkflowCreate, db: Session = Depends(get_db)):
    if not payload.steps:
        raise HTTPException(status_code=400, detail="Маршрут должен содержать хотя бы один шаг.")
    return HrDocumentService.create_workflow(
        db,
        payload.name,
        payload.description,
        [step.model_dump() for step in payload.steps],
    )


@router.get("", response_model=list[HrDocumentRead])
def get_documents(
    status: str | None = None,
    employee_id: int | None = None,
    doc_type: str | None = None,
    db: Session = Depends(get_db),
):
    documents = HrDocumentService.get_all(db, status, employee_id, doc_type)
    return [_to_read(document) for document in documents]


@router.post("", response_model=HrDocumentDetailRead, status_code=201)
async def create_document(
    title: str = Form(...),
    doc_type: str = Form("other"),
    owner_employee_id: int | None = Form(None),
    uploaded_by: str | None = Form(None),
    comment: str | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    content = await file.read()
    _validate_upload(file, content)
    document = HrDocumentService.create_document(
        db,
        title=title,
        doc_type=doc_type,
        owner_employee_id=owner_employee_id,
        file_name=file.filename or "document.pdf",
        content=content,
        uploaded_by=uploaded_by,
        comment=comment,
    )
    return _to_detail(db, document)


@router.get("/{document_id}", response_model=HrDocumentDetailRead)
def get_document(document_id: int, db: Session = Depends(get_db)):
    document = HrDocumentService.get_by_id(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return _to_detail(db, document)


@router.post("/{document_id}/versions", response_model=HrDocumentDetailRead)
async def add_document_version(
    document_id: int,
    uploaded_by: str | None = Form(None),
    comment: str | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    document = HrDocumentService.get_by_id(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    content = await file.read()
    _validate_upload(file, content)
    try:
        document = HrDocumentService.add_version(
            db,
            document,
            file_name=file.filename or "document.pdf",
            content=content,
            uploaded_by=uploaded_by,
            comment=comment,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return _to_detail(db, document)


@router.get("/{document_id}/versions/{version_no}/file")
def download_document_version(
    document_id: int,
    version_no: int,
    db: Session = Depends(get_db),
):
    version = HrDocumentService.get_version(db, document_id, version_no)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    file_path = Path(version.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File is missing on disk")
    return FileResponse(path=file_path, filename=version.file_name)


@router.post("/{document_id}/submit", response_model=HrDocumentDetailRead)
def submit_document(
    document_id: int,
    payload: HrDocumentSubmitRequest,
    db: Session = Depends(get_db),
):
    document = HrDocumentService.get_by_id(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    workflow = HrDocumentService.get_workflow(db, payload.workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    try:
        document = HrDocumentService.submit(db, document, workflow)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return _to_detail(db, document)


def _apply_decision(
    db: Session,
    document_id: int,
    payload: HrDocumentDecisionRequest,
    action,
) -> HrDocumentDetailRead:
    document = HrDocumentService.get_by_id(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    try:
        document = action(db, document, payload.actor, payload.comment)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return _to_detail(db, document)


@router.post("/{document_id}/approve", response_model=HrDocumentDetailRead)
def approve_document(
    document_id: int,
    payload: HrDocumentDecisionRequest,
    db: Session = Depends(get_db),
):
    return _apply_decision(db, document_id, payload, HrDocumentService.approve)


@router.post("/{document_id}/reject", response_model=HrDocumentDetailRead)
def reject_document(
    document_id: int,
    payload: HrDocumentDecisionRequest,
    db: Session = Depends(get_db),
):
    return _apply_decision(db, document_id, payload, HrDocumentService.reject)


@router.post("/{document_id}/sign", response_model=HrDocumentDetailRead)
def sign_document(
    document_id: int,
    payload: HrDocumentDecisionRequest,
    db: Session = Depends(get_db),
):
    return _apply_decision(db, document_id, payload, HrDocumentService.sign)


@router.post("/{document_id}/archive", response_model=HrDocumentDetailRead)
def archive_document(document_id: int, db: Session = Depends(get_db)):
    document = HrDocumentService.get_by_id(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    try:
        document = HrDocumentService.archive(db, document)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return _to_detail(db, document)


@router.get("/{document_id}/history", response_model=list[HrApprovalRead])
def get_document_history(document_id: int, db: Session = Depends(get_db)):
    document = HrDocumentService.get_by_id(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    approvals: list[HrApprovalRead] = []
    for instance in document.instances:
        approvals.extend(
            HrApprovalRead.model_validate(approval) for approval in instance.approvals
        )
    approvals.sort(key=lambda approval: approval.created_at)
    return approvals
