
from sqlalchemy.orm import Session

from backend.app.models.message import Message


def save_message(
    db: Session,
    conversation_id: str,
    role: str,
    content: str,
):
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message