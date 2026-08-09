from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: int
    document_id: str
    filename: str
    page_count: int
    chunk_count: int
    status: str
    version: int = 1
    is_active: bool = True
    supersedes_id: Optional[str] = None
    uploaded_at: datetime

    model_config = {
        "from_attributes": True
    }


class DocumentUploadResponse(DocumentResponse):
    message: str


class DocumentDeleteResponse(BaseModel):
    message: str
    document_id: str
    filename: str