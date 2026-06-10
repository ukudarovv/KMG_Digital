from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.vnd_document import VndDocumentRead
from app.services.vnd_service import VndService

router = APIRouter(prefix="/vnd", tags=["VND Documents"])


@router.get("/documents", response_model=list[VndDocumentRead])
def list_vnd_documents(db: Session = Depends(get_db)):
    VndService.seed_default_documents(db)
    return VndService.get_all(db)


@router.get("/documents/{code}", response_model=VndDocumentRead)
def get_vnd_document(code: str, db: Session = Depends(get_db)):
    VndService.seed_default_documents(db)
    document = VndService.get_by_code(db, code)
    if not document:
        raise HTTPException(status_code=404, detail="VND document not found")
    return document


@router.get("/documents/{code}/file")
def download_vnd_document(code: str, db: Session = Depends(get_db)):
    VndService.seed_default_documents(db)
    document = VndService.get_by_code(db, code)
    if not document:
        raise HTTPException(status_code=404, detail="VND document not found")
    file_path = VndService.resolve_file_path(document)
    if not file_path:
        raise HTTPException(status_code=404, detail="VND file not available")
    return FileResponse(path=file_path, filename=Path(document.file_name or file_path.name).name, media_type="application/pdf")
