from pydantic import BaseModel


# ---------------------------------------------------------
# Update Message
# ---------------------------------------------------------
class MessageUpdateRequest(BaseModel):
    content: str


class MessageUpdateResponse(BaseModel):
    message: str
    conversation_id: str | None = None
    user_question: str | None = None


# ---------------------------------------------------------
# Delete Message
# ---------------------------------------------------------
class MessageDeleteResponse(BaseModel):
    message: str


# ---------------------------------------------------------
# Regenerate Assistant
# ---------------------------------------------------------
class MessageRegenerateResponse(BaseModel):
    message: str
    conversation_id: str | None = None
    user_question: str | None = None