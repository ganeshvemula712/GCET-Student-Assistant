from sqlalchemy.orm import Session

from backend.app.models.message import Message


def get_conversation_history(
    conversation_id: str,
    db: Session,
    limit: int = 10,
) -> str:
    """
    Returns the latest conversation history formatted
    for the LLM prompt.
    """

    messages = (
        db.query(Message)
        .filter(
            Message.conversation_id == conversation_id
        )
        .order_by(Message.created_at.asc())
        .all()
    )

    history = []

    for message in messages[-limit:]:
        role = "User" if message.role == "user" else "Assistant"

        history.append(
            f"{role}: {message.content}"
        )

    return "\n".join(history)