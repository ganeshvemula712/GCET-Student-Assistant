from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator


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
    category: str = "General Academic"
    tags: str = ""
    uploaded_at: datetime

    @field_validator("category", mode="before")
    @classmethod
    def default_category_if_none(cls, v):
        return v if v else "General Academic"

    @field_validator("tags", mode="before")
    @classmethod
    def default_tags_if_none(cls, v):
        return v if v is not None else ""

    model_config = {
        "from_attributes": True
    }


class DocumentUploadResponse(DocumentResponse):
    message: str


class DocumentDeleteResponse(BaseModel):
    message: str
    document_id: str
    filename: str