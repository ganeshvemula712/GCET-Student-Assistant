from datetime import datetime

from pydantic import BaseModel, Field


class ConversationResponse(BaseModel):
    conversation_id: str
    title: str
    created_at: datetime

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime
    sources: list[dict] = []
    confidence: int | None = None
    follow_up_questions: list[str] = []


class ConversationDetailResponse(BaseModel):
    conversation_id: str
    title: str
    created_at: datetime
    messages: list[MessageResponse]

class ConversationRenameRequest(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )


class ConversationRenameResponse(BaseModel):
    message: str
    conversation_id: str
    title: str

class ConversationDeleteResponse(BaseModel):
    message: str
    conversation_id: str


class ConversationCreateRequest(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )


class ConversationCreateResponse(BaseModel):
    conversation_id: str
    title: str
    created_at: datetime
