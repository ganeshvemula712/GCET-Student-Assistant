from fastapi import APIRouter, Depends, Form, Query, Request, UploadFile
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.rate_limiter import limiter
from backend.app.core.security import get_current_user, require_admin
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
    supersedes_id: str | None = Form(None),
    category: str | None = Form(None),
    tags: str | None = Form(None),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return await process_document(
        file=file,
        db=db,
        supersedes_id=supersedes_id,
        category=category,
        tags=tags,
    )


@router.get(
    "",
    response_model=list[DocumentResponse],
)
def get_all_documents(
    category: str | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_documents(db=db, category=category)


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