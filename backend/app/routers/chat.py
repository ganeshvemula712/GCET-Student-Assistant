from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user

from backend.app.models.user import User

from backend.app.schemas.chat import (
    ChatRequest,
    ChatResponse,
)

from backend.app.services.chat import (
    process_chat,
)

from backend.app.services.chat_stream import (
    stream_chat,
)

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


# ----------------------------------------------------
# Existing Chat Endpoint
# ----------------------------------------------------
@router.post(
    "",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return process_chat(
        request=request,
        current_user=current_user,
        db=db,
    )


# ----------------------------------------------------
# Streaming Chat Endpoint
# ----------------------------------------------------
@router.post(
    "/stream",
)
def stream(
    request: ChatRequest,
    http_request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    generator = stream_chat(
        conversation_id=request.conversation_id,
        question=request.question,
        current_user=current_user,
        db=db,
        request=http_request,
    )

    return StreamingResponse(
        generator,
        media_type="application/x-ndjson",
    )
