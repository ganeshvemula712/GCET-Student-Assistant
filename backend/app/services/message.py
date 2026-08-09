from sqlalchemy.orm import Session
from fastapi import HTTPException

from backend.app.models.message import Message
from backend.app.models.conversation import Conversation
from backend.app.models.user import User
from backend.app.services.title_generator import generate_title_from_message


def save_message(
    db: Session,
    conversation_id: str,
    role: str,
    content: str,
    sources=None,
    confidence: int | None = None,
    follow_up_questions=None,
):
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        sources=sources or [],
        confidence=confidence,
        follow_up_questions=follow_up_questions or [],
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


def update_message(
    db: Session,
    message_id: int,
    content: str,
):
    message = (
        db.query(Message)
        .filter(Message.id == message_id)
        .first()
    )

    if not message:
        return None

    message.content = content
    db.commit()
    db.refresh(message)

    return message


def update_user_message_and_truncate_history(
    db: Session,
    current_user: User,
    message_id: int,
    content: str,
) -> tuple[str, str]:
    """
    Update edited user question and delete old assistant response + subsequent thread.
    """
    message = (
        db.query(Message)
        .join(
            Conversation,
            Conversation.conversation_id == Message.conversation_id,
        )
        .filter(
            Message.id == message_id,
            Conversation.user_id == current_user.id,
        )
        .first()
    )

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    # Update question content
    message.content = content
    db.commit()
    db.refresh(message)

    # Delete all messages after this edited question
    (
        db.query(Message)
        .filter(
            Message.conversation_id == message.conversation_id,
            Message.id > message.id,
        )
        .delete(synchronize_session=False)
    )
    db.commit()

    # Update conversation title if needed
    conversation = (
        db.query(Conversation)
        .filter(Conversation.conversation_id == message.conversation_id)
        .first()
    )
    if conversation and conversation.title in ("New Conversation", "New Chat", "Untitled"):
        conversation.title = generate_title_from_message(content)
        db.commit()

    return message.conversation_id, message.content


def prepare_regenerate_assistant_message(
    db: Session,
    current_user: User,
    target_message_id: int,
) -> tuple[str, str]:
    """
    Locate user prompt for regeneration and delete old assistant response.
    """
    target_msg = (
        db.query(Message)
        .join(
            Conversation,
            Conversation.conversation_id == Message.conversation_id,
        )
        .filter(
            Message.id == target_message_id,
            Conversation.user_id == current_user.id,
        )
        .first()
    )

    if not target_msg:
        raise HTTPException(status_code=404, detail="Message not found")

    if target_msg.role == "assistant":
        user_message = (
            db.query(Message)
            .filter(
                Message.conversation_id == target_msg.conversation_id,
                Message.id < target_msg.id,
                Message.role == "user",
            )
            .order_by(Message.id.desc())
            .first()
        )
        if not user_message:
            raise HTTPException(status_code=400, detail="Prior user message not found for regeneration")

        # Delete the assistant message and all messages after it
        (
            db.query(Message)
            .filter(
                Message.conversation_id == target_msg.conversation_id,
                Message.id >= target_msg.id,
            )
            .delete(synchronize_session=False)
        )
        db.commit()
        return user_message.conversation_id, user_message.content
    else:
        # Target message is a user message
        (
            db.query(Message)
            .filter(
                Message.conversation_id == target_msg.conversation_id,
                Message.id > target_msg.id,
            )
            .delete(synchronize_session=False)
        )
        db.commit()
        return target_msg.conversation_id, target_msg.content


def delete_message(
    db: Session,
    current_user: User,
    message_id: int,
):
    """
    Delete the selected message and every message after it.
    """
    message = (
        db.query(Message)
        .join(
            Conversation,
            Conversation.conversation_id == Message.conversation_id,
        )
        .filter(
            Message.id == message_id,
            Conversation.user_id == current_user.id,
        )
        .first()
    )

    if not message:
        return False

    (
        db.query(Message)
        .filter(
            Message.conversation_id == message.conversation_id,
            Message.id >= message.id,
        )
        .delete(synchronize_session=False)
    )
    db.commit()
    return True