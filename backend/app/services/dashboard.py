from sqlalchemy.orm import Session

from backend.app.models.conversation import Conversation
from backend.app.models.document import Document
from backend.app.models.message import Message
from backend.app.models.user import User


def get_dashboard_stats(
    current_user: User,
    db: Session,
):
    user_role = (getattr(current_user, "role", None) or "student").lower()

    if user_role == "admin":
        conversation_count = db.query(Conversation.id).count()
        response_count = (
            db.query(Message.id)
            .filter(Message.role == "assistant")
            .count()
        )
        document_count = db.query(Document.id).count()
        account = "Admin"
    else:
        conversation_count = (
            db.query(Conversation.id)
            .filter(Conversation.user_id == current_user.id)
            .count()
        )

        response_count = (
            db.query(Message.id)
            .join(
                Conversation,
                Message.conversation_id == Conversation.conversation_id,
            )
            .filter(
                Conversation.user_id == current_user.id,
                Message.role == "assistant",
            )
            .count()
        )

        document_count = db.query(Document.id).count()
        account = "Active"

    return {
        "conversations": conversation_count,
        "responses": response_count,
        "documents": document_count,
        "account": account,
    }