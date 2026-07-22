from datetime import datetime

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: int
    document_id: str
    filename: str
    page_count: int
    chunk_count: int
    status: str
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