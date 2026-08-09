from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.models.conversation import Conversation
from backend.app.models.message import Message
from backend.app.models.user import User

from backend.app.schemas.conversation import (
    ConversationDetailResponse,
    MessageResponse,
)


# --------------------------------------------------------
# Create Conversation
# --------------------------------------------------------
def create_conversation(
    title: str,
    current_user: User,
    db: Session,
):
    conversation = Conversation(
        conversation_id=str(uuid4()),
        title=title,
        user_id=current_user.id,
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


# --------------------------------------------------------
# Get All Conversations
# --------------------------------------------------------
def get_conversations(
    current_user: User,
    db: Session,
    page: int = 1,
    limit: int = 20,
):
    offset = (page - 1) * limit

    conversations = (
        db.query(Conversation)
        .filter(
            Conversation.user_id == current_user.id,
        )
        .order_by(
            Conversation.created_at.desc(),
        )
        .offset(offset)
        .limit(limit)
        .all()
    )

    return conversations


# --------------------------------------------------------
# Get One Conversation
# --------------------------------------------------------
def get_conversation(
    conversation_id: str,
    current_user: User,
    db: Session,
) -> ConversationDetailResponse:

    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.conversation_id == conversation_id,
            Conversation.user_id == current_user.id,
        )
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    messages = (
        db.query(Message)
        .filter(
            Message.conversation_id == conversation_id,
        )
        .order_by(
            Message.created_at.asc(),
        )
        .all()
    )

    return ConversationDetailResponse(
        conversation_id=conversation.conversation_id,
        title=conversation.title,
        created_at=conversation.created_at,
        messages=[
            MessageResponse(
                id=message.id,
                role=message.role,
                content=message.content,
                created_at=message.created_at,
                sources=[
                    {
                        "filename": s.get("filename") if isinstance(s, dict) else getattr(s, "filename", ""),
                        "page": s.get("page") if isinstance(s, dict) else getattr(s, "page", 0),
                    }
                    for s in (message.sources or [])
                ],
                confidence=message.confidence,
                follow_up_questions=message.follow_up_questions or [],
            )
            for message in messages
        ],
    )


# --------------------------------------------------------
# Rename Conversation
# --------------------------------------------------------
def rename_conversation(
    conversation_id: str,
    title: str,
    current_user: User,
    db: Session,
):

    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.conversation_id == conversation_id,
            Conversation.user_id == current_user.id,
        )
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    conversation.title = title

    db.commit()
    db.refresh(conversation)

    return {
        "message": "Conversation renamed successfully",
        "conversation_id": conversation.conversation_id,
        "title": conversation.title,
    }


# --------------------------------------------------------
# Delete Conversation
# --------------------------------------------------------
def delete_conversation(
    conversation_id: str,
    current_user: User,
    db: Session,
):

    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.conversation_id == conversation_id,
            Conversation.user_id == current_user.id,
        )
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    (
        db.query(Message)
        .filter(
            Message.conversation_id == conversation_id,
        )
        .delete()
    )

    db.delete(conversation)

    db.commit()

    return {
        "message": "Conversation deleted successfully",
        "conversation_id": conversation_id,
    }


# --------------------------------------------------------
# Search Conversations
# --------------------------------------------------------
def search_conversations(
    query: str,
    current_user: User,
    db: Session,
):

    conversations = (
        db.query(Conversation)
        .filter(
            Conversation.user_id == current_user.id,
            Conversation.title.ilike(f"%{query}%"),
        )
        .order_by(
            Conversation.created_at.desc(),
        )
        .all()
    )

    return conversations
