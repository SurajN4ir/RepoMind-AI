"""Database-backed index store adapter implementing write-side ports."""

from collections.abc import AsyncGenerator, Mapping, Sequence
from contextlib import asynccontextmanager
from uuid import UUID

import structlog
from sqlalchemy import delete as sa_delete
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.indexing.db_models import (
    ActivityEventModel,
    FileContentModel,
    FileDependencyModel,
    IndexEntryModel,
    KeywordIndexEntryModel,
    MetadataIndexEntryModel,
)
from app.modules.indexing.models import (
    ActivityEventRecord,
    FileContentRecord,
    FileDependencyRecord,
    IndexEntry,
    KeywordIndexEntry,
    MetadataIndexEntry,
)
from app.modules.indexing.repository import (
    ActivityRepository,
    DependencyRepository,
    FileContentRepository,
    IndexingTransactionManager,
    KeywordIndexRepository,
    MetadataIndexRepository,
    VectorIndexRepository,
)

logger = structlog.get_logger(__name__)


class DbIndexStore(
    VectorIndexRepository,
    KeywordIndexRepository,
    MetadataIndexRepository,
    IndexingTransactionManager,
    FileContentRepository,
    DependencyRepository,
    ActivityRepository,
):
    """Persistent index store backed by SQLAlchemy async sessions.

    Implements all write-side ports so a single instance can be injected
    for all index projections, mirroring ``InMemoryIndexStore``.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def store_file_content(
        self, repository_id: UUID, file_path: str, content: str, content_hash: str
    ) -> None:
        await self._session.merge(
            FileContentModel(
                repository_id=repository_id,
                file_path=file_path,
                content=content,
                content_hash=content_hash,
            )
        )
        await self._session.flush()

    async def get_file_content(
        self, repository_id: UUID, file_path: str
    ) -> FileContentRecord | None:
        row = (
            await self._session.execute(
                select(FileContentModel).where(
                    FileContentModel.repository_id == repository_id,
                    FileContentModel.file_path == file_path,
                )
            )
        ).scalar_one_or_none()
        if row is None:
            return None
        return FileContentRecord(
            repository_id=row.repository_id,
            file_path=row.file_path,
            content=row.content,
            content_hash=row.content_hash,
            created_at=row.created_at,
        )

    async def get_file_path_hashes(self, repository_id: UUID) -> Mapping[str, str]:
        rows = await self._session.execute(
            select(FileContentModel.file_path, FileContentModel.content_hash).where(
                FileContentModel.repository_id == repository_id
            )
        )
        return {row.file_path: row.content_hash for row in rows}

    async def get_file_count(self, repository_id: UUID) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(FileContentModel)
            .where(FileContentModel.repository_id == repository_id)
        )
        return result.scalar() or 0

    async def delete_file_contents(self, repository_id: UUID, file_paths: Sequence[str]) -> None:
        if not file_paths:
            return
        stmt = sa_delete(FileContentModel).where(
            FileContentModel.repository_id == repository_id,
            FileContentModel.file_path.in_(file_paths),
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def store_dependencies(
        self, repository_id: UUID, edges: Sequence[tuple[str, str]]
    ) -> None:
        await self._session.execute(
            sa_delete(FileDependencyModel).where(
                FileDependencyModel.repository_id == repository_id,
            )
        )
        for source_path, target_path in edges:
            self._session.add(
                FileDependencyModel(
                    repository_id=repository_id,
                    source_path=source_path,
                    target_path=target_path,
                )
            )
        await self._session.flush()

    async def get_dependencies(self, repository_id: UUID) -> Sequence[FileDependencyRecord]:
        rows = (
            (
                await self._session.execute(
                    select(FileDependencyModel).where(
                        FileDependencyModel.repository_id == repository_id,
                    )
                )
            )
            .scalars()
            .all()
        )
        return [
            FileDependencyRecord(
                repository_id=row.repository_id,
                source_path=row.source_path,
                target_path=row.target_path,
            )
            for row in rows
        ]

    async def delete_dependencies(self, repository_id: UUID) -> None:
        await self._session.execute(
            sa_delete(FileDependencyModel).where(
                FileDependencyModel.repository_id == repository_id,
            )
        )
        await self._session.flush()

    async def record_activity(self, repository_id: UUID, event_type: str, message: str) -> None:
        self._session.add(
            ActivityEventModel(
                repository_id=repository_id,
                event_type=event_type,
                message=message,
            )
        )
        await self._session.flush()

    async def get_activity(
        self, repository_id: UUID, limit: int = 20
    ) -> Sequence[ActivityEventRecord]:
        rows = (
            (
                await self._session.execute(
                    select(ActivityEventModel)
                    .where(ActivityEventModel.repository_id == repository_id)
                    .order_by(ActivityEventModel.created_at.desc())
                    .limit(limit)
                )
            )
            .scalars()
            .all()
        )
        return [
            ActivityEventRecord(
                repository_id=row.repository_id,
                event_type=row.event_type,
                message=row.message,
                created_at=row.created_at,
            )
            for row in reversed(rows)
        ]

    async def delete_activity(self, repository_id: UUID) -> None:
        await self._session.execute(
            sa_delete(ActivityEventModel).where(
                ActivityEventModel.repository_id == repository_id,
            )
        )
        await self._session.flush()

    async def get_hashes(self, repository_id: UUID) -> Mapping[str, str]:
        rows = await self._session.execute(
            select(IndexEntryModel.document_id, IndexEntryModel.content_hash).where(
                IndexEntryModel.repository_id == repository_id
            )
        )
        return {row.document_id: row.content_hash for row in rows}

    async def upsert(
        self,
        entries: Sequence[IndexEntry | KeywordIndexEntry | MetadataIndexEntry],
    ) -> None:
        for entry in entries:
            if isinstance(entry, IndexEntry):
                await self._session.merge(
                    IndexEntryModel(
                        document_id=entry.document_id,
                        repository_id=entry.repository_id,
                        embedding=list(entry.embedding),
                        text=entry.text,
                        entry_metadata=dict(entry.metadata),
                        content_hash=entry.content_hash,
                        provider=entry.provider,
                        model=entry.model,
                    )
                )
            elif isinstance(entry, KeywordIndexEntry):
                await self._session.merge(
                    KeywordIndexEntryModel(
                        document_id=entry.document_id,
                        repository_id=entry.repository_id,
                        text=entry.text,
                    )
                )
            else:
                await self._session.merge(
                    MetadataIndexEntryModel(
                        document_id=entry.document_id,
                        repository_id=entry.repository_id,
                        entry_metadata=dict(entry.metadata),
                    )
                )
        await self._session.flush()
        logger.debug(
            "db_index_store_upserted",
            count=len(entries),
            types=[type(e).__name__ for e in entries],
        )

    async def delete(self, repository_id: UUID, document_ids: Sequence[str]) -> None:
        rows = (
            (
                await self._session.execute(
                    select(IndexEntryModel).where(
                        IndexEntryModel.repository_id == repository_id,
                        IndexEntryModel.document_id.in_(document_ids),
                    )
                )
            )
            .scalars()
            .all()
        )
        for row in rows:
            await self._session.delete(row)
        await self._session.flush()
        logger.debug("db_index_store_deleted", document_count=len(document_ids))

    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator[None]:
        """Rely on the caller's SQLAlchemy transaction context."""
        yield
