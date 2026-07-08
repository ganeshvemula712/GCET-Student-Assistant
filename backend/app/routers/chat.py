from fastapi import APIRouter

from backend.app.schemas.chat import ChatRequest, ChatResponse


router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    return ChatResponse(
        answer=f"You asked: {request.question}"
    )