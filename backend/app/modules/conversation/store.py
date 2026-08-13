"""Thin persistence layer for conversations and messages."""

from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.conversation.db_models import ConversationModel, MessageModel
from app.modules.conversation.models import ConversationRecord, MessageRecord

logger = structlog.get_logger(__name__)


class ConversationStore:
    """Direct-to-database conversation persistence.

    No protocol abstraction, no in-memory variant.  Three operations:
    get-or-create a conversation by repository, add a message, fetch
    recent messages.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_or_create(self, repository_id: UUID) -> ConversationRecord:
        """Return existing conversation for a repository or create one."""
        stmt = (
            select(ConversationModel)
            .where(ConversationModel.repository_id == repository_id)
            .order_by(ConversationModel.created_at.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is not None:
            return ConversationRecord(
                id=model.id,
                repository_id=model.repository_id,
                created_at=model.created_at,
                updated_at=model.updated_at,
            )

        now = datetime.now(UTC)
        model = ConversationModel(
            repository_id=repository_id,
            created_at=now,
            updated_at=now,
        )
        self._session.add(model)
        await self._session.flush()
        logger.info(
            "conversation_created",
            repository_id=str(repository_id),
            conversation_id=str(model.id),
        )
        return ConversationRecord(
            id=model.id,
            repository_id=model.repository_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def add_message(
        self,
        conversation_id: UUID,
        role: str,
        content: str,
        citation_json: str = "",
    ) -> MessageRecord:
        """Persist a single message and return its record."""
        now = datetime.now(UTC)
        model = MessageModel(
            conversation_id=conversation_id,
            role=role,
            content=content,
            citation_json=citation_json,
            created_at=now,
            updated_at=now,
        )
        self._session.add(model)
        await self._session.flush()
        return MessageRecord(
            id=model.id,
            conversation_id=model.conversation_id,
            role=model.role,
            content=model.content,
            citation_json=model.citation_json,
            created_at=model.created_at,
        )

    async def get_messages(
        self,
        conversation_id: UUID,
        limit: int = 20,
    ) -> Sequence[MessageRecord]:
        """Return the most recent messages ordered by creation time."""
        stmt = (
            select(MessageModel)
            .where(MessageModel.conversation_id == conversation_id)
            .order_by(MessageModel.created_at.asc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return tuple(
            MessageRecord(
                id=model.id,
                conversation_id=model.conversation_id,
                role=model.role,
                content=model.content,
                citation_json=model.citation_json,
                created_at=model.created_at,
            )
            for model in result.scalars().all()
        )
