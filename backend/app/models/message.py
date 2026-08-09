from datetime import datetime, timezone
from sqlalchemy import JSON, Column

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from backend.app.core.database import Base
from backend.app.models.conversation import Conversation
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.app.models.conversation import Conversation

class Message(Base):

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    conversation_id: Mapped[str] = mapped_column(
        ForeignKey("conversations.conversation_id"),
        nullable=False,
        index=True,
    )

    role: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    sources = Column(
        JSON,
        nullable=True,
        default=list,
    )

    confidence = Column(Integer, nullable=True, default=0)

    follow_up_questions = Column(JSON, nullable=True, default=list)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    conversation: Mapped["Conversation"] = relationship(
        back_populates="messages",
    )