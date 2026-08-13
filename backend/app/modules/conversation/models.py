"""Pure domain models for conversation and message storage."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class MessageRecord:
    """One message within a conversation."""

    conversation_id: UUID
    role: str
    content: str
    citation_json: str = ""
    id: UUID = field(default_factory=uuid4)
    created_at: datetime | None = None


@dataclass
class ConversationRecord:
    """A persisted conversation session for a repository."""

    repository_id: UUID
    id: UUID = field(default_factory=uuid4)
    created_at: datetime | None = None
    updated_at: datetime | None = None
