from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.models.conversation import Conversation
from backend.app.models.feedback import Feedback
from backend.app.models.message import Message
from backend.app.models.user import User


def save_feedback(db: Session, message_id: int, user: User, feedback_value: str):
    message = (
        db.query(Message)
        .join(Conversation, Conversation.conversation_id == Message.conversation_id)
        .filter(Message.id == message_id, Conversation.user_id == user.id)
        .first()
    )

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    existing = (
        db.query(Feedback)
        .filter(Feedback.message_id == message_id, Feedback.user_id == user.id)
        .first()
    )

    if existing:
        existing.feedback_value = feedback_value
        db.commit()
        db.refresh(existing)
        return existing

    feedback = Feedback(
        message_id=message_id,
        user_id=user.id,
        feedback_value=feedback_value,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


def get_feedback_for_message(db: Session, message_id: int, user: User):
    feedback = (
        db.query(Feedback)
        .filter(Feedback.message_id == message_id, Feedback.user_id == user.id)
        .first()
    )

    return feedback.feedback_value if feedback else None
