"""HR-документооборот: версии, маршруты согласования, подпись."""

import logging
from pathlib import Path

from sqlalchemy.orm import Session

from app.integrations.bitrix.service import BitrixService
from app.models.hr_document import (
    HrDocument,
    HrDocumentApproval,
    HrDocumentInstance,
    HrDocumentVersion,
    HrDocumentWorkflow,
    HrDocumentWorkflowStep,
)

logger = logging.getLogger(__name__)

DOCUMENTS_DIR = Path(__file__).resolve().parents[1] / "data" / "hr_documents"

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc"}
MAX_FILE_SIZE = 10 * 1024 * 1024

DEFAULT_WORKFLOWS = [
    {
        "name": "Стандартное согласование",
        "description": "HR проверяет документ, руководитель согласует, HR подписывает.",
        "steps": [
            {"step_order": 1, "role": "hr", "approver_name": "HR-специалист"},
            {"step_order": 2, "role": "manager", "approver_name": "Руководитель"},
            {"step_order": 3, "role": "signer", "approver_name": "Уполномоченное лицо"},
        ],
    },
    {
        "name": "Быстрое подписание",
        "description": "Документ сразу уходит на подпись без промежуточного согласования.",
        "steps": [
            {"step_order": 1, "role": "signer", "approver_name": "Уполномоченное лицо"},
        ],
    },
]


class HrDocumentService:
    @staticmethod
    def ensure_default_workflows(db: Session) -> None:
        if db.query(HrDocumentWorkflow).count() > 0:
            return
        for item in DEFAULT_WORKFLOWS:
            workflow = HrDocumentWorkflow(
                name=item["name"],
                description=item["description"],
            )
            db.add(workflow)
            db.flush()
            for step in item["steps"]:
                db.add(HrDocumentWorkflowStep(workflow_id=workflow.id, **step))
        db.commit()

    @staticmethod
    def get_all(
        db: Session,
        status: str | None = None,
        employee_id: int | None = None,
        doc_type: str | None = None,
    ) -> list[HrDocument]:
        query = db.query(HrDocument)
        if status:
            query = query.filter(HrDocument.status == status)
        if employee_id:
            query = query.filter(HrDocument.owner_employee_id == employee_id)
        if doc_type:
            query = query.filter(HrDocument.doc_type == doc_type)
        return query.order_by(HrDocument.id.desc()).all()

    @staticmethod
    def get_by_id(db: Session, document_id: int) -> HrDocument | None:
        return db.query(HrDocument).filter(HrDocument.id == document_id).first()

    @staticmethod
    def _store_file(document_id: int, version_no: int, file_name: str, content: bytes) -> Path:
        target_dir = DOCUMENTS_DIR / str(document_id) / f"v{version_no}"
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / file_name
        target.write_bytes(content)
        return target

    @staticmethod
    def create_document(
        db: Session,
        title: str,
        doc_type: str,
        owner_employee_id: int | None,
        file_name: str,
        content: bytes,
        uploaded_by: str | None = None,
        comment: str | None = None,
    ) -> HrDocument:
        document = HrDocument(
            title=title,
            doc_type=doc_type or "other",
            owner_employee_id=owner_employee_id,
            status="draft",
            current_version_no=1,
        )
        db.add(document)
        db.flush()

        file_path = HrDocumentService._store_file(document.id, 1, file_name, content)
        db.add(
            HrDocumentVersion(
                document_id=document.id,
                version_no=1,
                file_path=str(file_path),
                file_name=file_name,
                uploaded_by=uploaded_by,
                comment=comment,
            )
        )
        db.commit()
        db.refresh(document)
        return document

    @staticmethod
    def add_version(
        db: Session,
        document: HrDocument,
        file_name: str,
        content: bytes,
        uploaded_by: str | None = None,
        comment: str | None = None,
    ) -> HrDocument:
        if document.status not in {"draft", "rejected"}:
            raise ValueError("Новую версию можно загрузить только для черновика или отклонённого документа.")
        next_no = document.current_version_no + 1
        file_path = HrDocumentService._store_file(document.id, next_no, file_name, content)
        db.add(
            HrDocumentVersion(
                document_id=document.id,
                version_no=next_no,
                file_path=str(file_path),
                file_name=file_name,
                uploaded_by=uploaded_by,
                comment=comment,
            )
        )
        document.current_version_no = next_no
        if document.status == "rejected":
            document.status = "draft"
        db.commit()
        db.refresh(document)
        return document

    @staticmethod
    def get_version(
        db: Session, document_id: int, version_no: int
    ) -> HrDocumentVersion | None:
        return (
            db.query(HrDocumentVersion)
            .filter(
                HrDocumentVersion.document_id == document_id,
                HrDocumentVersion.version_no == version_no,
            )
            .first()
        )

    @staticmethod
    def get_active_instance(
        db: Session, document: HrDocument
    ) -> HrDocumentInstance | None:
        return (
            db.query(HrDocumentInstance)
            .filter(
                HrDocumentInstance.document_id == document.id,
                HrDocumentInstance.status == "active",
            )
            .order_by(HrDocumentInstance.id.desc())
            .first()
        )

    @staticmethod
    def submit(
        db: Session,
        document: HrDocument,
        workflow: HrDocumentWorkflow,
    ) -> HrDocument:
        if document.status not in {"draft", "rejected"}:
            raise ValueError("На согласование можно отправить только черновик.")
        if not workflow.steps:
            raise ValueError("В маршруте нет шагов согласования.")

        db.add(
            HrDocumentInstance(
                document_id=document.id,
                workflow_id=workflow.id,
                employee_id=document.owner_employee_id,
                current_step_order=workflow.steps[0].step_order,
                status="active",
            )
        )
        document.status = "in_review"
        db.commit()
        db.refresh(document)
        HrDocumentService._notify(f"Документ «{document.title}» отправлен на согласование.")
        return document

    @staticmethod
    def _record_decision(
        db: Session,
        instance: HrDocumentInstance,
        decision: str,
        actor: str | None,
        comment: str | None,
    ) -> None:
        db.add(
            HrDocumentApproval(
                instance_id=instance.id,
                step_order=instance.current_step_order,
                decision=decision,
                actor=actor,
                comment=comment,
            )
        )

    @staticmethod
    def approve(
        db: Session,
        document: HrDocument,
        actor: str | None,
        comment: str | None,
    ) -> HrDocument:
        if document.status != "in_review":
            raise ValueError("Документ не находится на согласовании.")
        instance = HrDocumentService.get_active_instance(db, document)
        if not instance:
            raise ValueError("Активный маршрут согласования не найден.")

        HrDocumentService._record_decision(db, instance, "approved", actor, comment)

        steps = sorted(instance.workflow.steps, key=lambda step: step.step_order)
        next_steps = [
            step for step in steps if step.step_order > instance.current_step_order
        ]
        if next_steps:
            instance.current_step_order = next_steps[0].step_order
        else:
            instance.status = "completed"
            document.status = "approved"
            HrDocumentService._notify(f"Документ «{document.title}» полностью согласован.")
        db.commit()
        db.refresh(document)
        return document

    @staticmethod
    def reject(
        db: Session,
        document: HrDocument,
        actor: str | None,
        comment: str | None,
    ) -> HrDocument:
        if document.status != "in_review":
            raise ValueError("Документ не находится на согласовании.")
        instance = HrDocumentService.get_active_instance(db, document)
        if not instance:
            raise ValueError("Активный маршрут согласования не найден.")

        HrDocumentService._record_decision(db, instance, "rejected", actor, comment)
        instance.status = "rejected"
        document.status = "rejected"
        db.commit()
        db.refresh(document)
        HrDocumentService._notify(f"Документ «{document.title}» отклонён.")
        return document

    @staticmethod
    def sign(
        db: Session,
        document: HrDocument,
        actor: str | None,
        comment: str | None,
    ) -> HrDocument:
        if document.status != "approved":
            raise ValueError("Подписать можно только согласованный документ.")
        instance = (
            db.query(HrDocumentInstance)
            .filter(HrDocumentInstance.document_id == document.id)
            .order_by(HrDocumentInstance.id.desc())
            .first()
        )
        if instance:
            db.add(
                HrDocumentApproval(
                    instance_id=instance.id,
                    step_order=instance.current_step_order,
                    decision="signed",
                    actor=actor,
                    comment=comment,
                )
            )
        document.status = "signed"
        db.commit()
        db.refresh(document)
        HrDocumentService._notify(f"Документ «{document.title}» подписан.")
        return document

    @staticmethod
    def archive(db: Session, document: HrDocument) -> HrDocument:
        if document.status != "signed":
            raise ValueError("В архив можно отправить только подписанный документ.")
        document.status = "archived"
        db.commit()
        db.refresh(document)
        return document

    @staticmethod
    def get_workflows(db: Session) -> list[HrDocumentWorkflow]:
        return (
            db.query(HrDocumentWorkflow)
            .filter(HrDocumentWorkflow.is_active.is_(True))
            .order_by(HrDocumentWorkflow.id.asc())
            .all()
        )

    @staticmethod
    def get_workflow(db: Session, workflow_id: int) -> HrDocumentWorkflow | None:
        return (
            db.query(HrDocumentWorkflow)
            .filter(HrDocumentWorkflow.id == workflow_id)
            .first()
        )

    @staticmethod
    def create_workflow(
        db: Session,
        name: str,
        description: str | None,
        steps: list[dict],
    ) -> HrDocumentWorkflow:
        workflow = HrDocumentWorkflow(name=name, description=description)
        db.add(workflow)
        db.flush()
        for step in steps:
            db.add(HrDocumentWorkflowStep(workflow_id=workflow.id, **step))
        db.commit()
        db.refresh(workflow)
        return workflow

    @staticmethod
    def _notify(message: str) -> None:
        try:
            BitrixService.send_hr_alert(message)
        except Exception as error:
            logger.warning("Bitrix alert failed: %s", error)
