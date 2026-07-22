from pydantic import BaseModel, Field


class ChatRequest(BaseModel):

    conversation_id: str = Field(
        ...,
        description="Conversation ID",
    )

    question: str = Field(
        ...,
        min_length=1,
        description="Student question",
    )


class Source(BaseModel):

    filename: str

    page: int


class ChatResponse(BaseModel):

    answer: str

    sources: list[Source] = []