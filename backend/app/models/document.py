from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.database import Base


VALID_CATEGORIES = [
    "Academic Regulations",
    "Course Syllabus",
    "Placements",
    "Timetables",
    "Examinations",
    "Attendance",
    "Notices & Circulars",
    "General Academic",
]
DEFAULT_CATEGORY = "General Academic"


class Document(Base):

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    document_id: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )

    filename: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    page_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    chunk_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="processed",
    )

    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    supersedes_id: Mapped[str] = mapped_column(
        String,
        nullable=True,
    )

    category: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
        default=DEFAULT_CATEGORY,
    )

    tags: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
        default="",
    )

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )