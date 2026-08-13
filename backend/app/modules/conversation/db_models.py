"""SQLAlchemy models for conversation and message persistence."""

from uuid import UUID

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.database.base import Base
from app.shared.database.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class ConversationModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Persistent conversation session for a repository."""

    __tablename__ = "conversations"

    repository_id: Mapped[UUID] = mapped_column(nullable=False, index=True)


class MessageModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Persistent message within a conversation."""

    __tablename__ = "messages"

    conversation_id: Mapped[UUID] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    citation_json: Mapped[str] = mapped_column(Text, nullable=False, default="")
