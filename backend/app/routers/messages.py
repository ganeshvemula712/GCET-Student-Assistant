from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.models.user import User
from backend.app.schemas.message import (
    MessageDeleteResponse,
    MessageRegenerateResponse,
    MessageUpdateRequest,
    MessageUpdateResponse,
)
from backend.app.services.message import (
    delete_message,
    prepare_regenerate_assistant_message,
    update_user_message_and_truncate_history,
)

router = APIRouter(
    prefix="/messages",
    tags=["Messages"],
)


# ---------------------------------------------------------
# Edit User Question
# ---------------------------------------------------------
@router.patch(
    "/{message_id}",
    response_model=MessageUpdateResponse,
)
def edit_message(
    message_id: int,
    body: MessageUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conv_id, user_q = update_user_message_and_truncate_history(
        db=db,
        current_user=current_user,
        message_id=message_id,
        content=body.content,
    )

    return {
        "message": "Message updated successfully",
        "conversation_id": conv_id,
        "user_question": user_q,
    }


# ---------------------------------------------------------
# Regenerate Assistant Response
# ---------------------------------------------------------
@router.post(
    "/{message_id}/regenerate",
    response_model=MessageRegenerateResponse,
)
def regenerate(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conv_id, user_q = prepare_regenerate_assistant_message(
        db=db,
        current_user=current_user,
        target_message_id=message_id,
    )

    return {
        "message": "Assistant message reset for regeneration",
        "conversation_id": conv_id,
        "user_question": user_q,
    }


# ---------------------------------------------------------
# Delete Message
# ---------------------------------------------------------
@router.delete(
    "/{message_id}",
    response_model=MessageDeleteResponse,
)
def remove_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    deleted = delete_message(
        db=db,
        current_user=current_user,
        message_id=message_id,
    )

    if not deleted:
        raise HTTPException(status_code=404, detail="Message not found")

    return {"message": "Message deleted successfully"}
