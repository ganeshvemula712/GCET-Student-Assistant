from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import require_admin
from backend.app.models.user import User
from backend.app.schemas.document import (
    DocumentDeleteResponse,
    DocumentResponse,
    DocumentUploadResponse,
)
from backend.app.services.documents import (
    get_documents,
    process_document,
    remove_document,
)
from fastapi import APIRouter, Depends, Request, UploadFile
from backend.app.core.rate_limiter import limiter



router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
)
@limiter.limit("10/minute")
async def upload_document(
    request: Request,
    file: UploadFile,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return await process_document(
        file=file,
        current_user=current_user,
        db=db,
    )

@router.get(
    "",
    response_model=list[DocumentResponse],
)
def get_all_documents(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return get_documents(db)


@router.delete(
    "/{document_id}",
    response_model=DocumentDeleteResponse,
)
def delete_document(
    document_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return remove_document(
        document_id=document_id,
        db=db,
    )