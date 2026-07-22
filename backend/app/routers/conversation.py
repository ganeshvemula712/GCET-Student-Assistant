from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.models.user import User

from backend.app.schemas.conversation import (
    ConversationCreateRequest,
    ConversationCreateResponse,
    ConversationDeleteResponse,
    ConversationDetailResponse,
    ConversationRenameRequest,
    ConversationRenameResponse,
    ConversationResponse,
)

from backend.app.services.conversation import (
    create_conversation,
    delete_conversation,
    get_conversation,
    get_conversations,
    rename_conversation,
    search_conversations,
)

router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


@router.post(
    "",
    response_model=ConversationCreateResponse,
)
def create_new_conversation(
    request: ConversationCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return create_conversation(
        title=request.title,
        current_user=current_user,
        db=db,
    )


@router.get(
    "",
    response_model=list[ConversationResponse],
)
def list_conversations(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_conversations(
        current_user=current_user,
        db=db,
        page=page,
        limit=limit,
    )


@router.get(
    "/search",
    response_model=list[ConversationResponse],
)
def search(
    q: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return search_conversations(
        query=q,
        current_user=current_user,
        db=db,
    )


@router.get(
    "/{conversation_id}",
    response_model=ConversationDetailResponse,
)
def get_conversation_details(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_conversation(
        conversation_id=conversation_id,
        current_user=current_user,
        db=db,
    )


@router.patch(
    "/{conversation_id}",
    response_model=ConversationRenameResponse,
)
def rename(
    conversation_id: str,
    request: ConversationRenameRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return rename_conversation(
        conversation_id=conversation_id,
        title=request.title,
        current_user=current_user,
        db=db,
    )


@router.delete(
    "/{conversation_id}",
    response_model=ConversationDeleteResponse,
)
def delete(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return delete_conversation(
        conversation_id=conversation_id,
        current_user=current_user,
        db=db,
    )