"""Storage interfaces and in-memory adapter for write-side indexing."""

from collections.abc import Mapping, Sequence
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import Protocol
from uuid import UUID

from app.modules.indexing.models import (
    ActivityEventRecord,
    FileContentRecord,
    FileDependencyRecord,
    IndexEntry,
    KeywordIndexEntry,
    MetadataIndexEntry,
)


class VectorIndexRepository(Protocol):
    """Port for persisting and comparing vector index records."""

    async def get_hashes(self, repository_id: UUID) -> Mapping[str, str]: ...

    async def upsert(self, entries: Sequence[IndexEntry]) -> None: ...

    async def delete(self, repository_id: UUID, document_ids: Sequence[str]) -> None: ...


class KeywordIndexRepository(Protocol):
    """Port for persisting searchable keyword text independently of retrieval."""

    async def upsert(self, entries: Sequence[KeywordIndexEntry]) -> None: ...

    async def delete(self, repository_id: UUID, document_ids: Sequence[str]) -> None: ...


class MetadataIndexRepository(Protocol):
    """Port for persisting metadata fields used by future retrieval filters."""

    async def upsert(self, entries: Sequence[MetadataIndexEntry]) -> None: ...

    async def delete(self, repository_id: UUID, document_ids: Sequence[str]) -> None: ...


class IndexingTransactionManager(Protocol):
    """Port that provides atomic write semantics across index projections."""

    def transaction(self) -> AbstractAsyncContextManager[None]: ...


class FileContentRepository(Protocol):
    """Port for persisting and retrieving full file contents."""

    async def store_file_content(
        self, repository_id: UUID, file_path: str, content: str, content_hash: str
    ) -> None: ...

    async def get_file_content(
        self, repository_id: UUID, file_path: str
    ) -> FileContentRecord | None: ...

    async def get_file_path_hashes(self, repository_id: UUID) -> Mapping[str, str]: ...

    async def delete_file_contents(
        self, repository_id: UUID, file_paths: Sequence[str]
    ) -> None: ...

    async def get_file_count(self, repository_id: UUID) -> int: ...


class ActivityRepository(Protocol):
    """Port for recording and retrieving repository activity events."""

    async def record_activity(self, repository_id: UUID, event_type: str, message: str) -> None: ...

    async def get_activity(
        self, repository_id: UUID, limit: int = 20
    ) -> Sequence[ActivityEventRecord]: ...

    async def delete_activity(self, repository_id: UUID) -> None: ...


class DependencyRepository(Protocol):
    """Port for persisting and retrieving resolved cross-file dependency edges."""

    async def store_dependencies(
        self, repository_id: UUID, edges: Sequence[tuple[str, str]]
    ) -> None: ...

    async def get_dependencies(self, repository_id: UUID) -> Sequence[FileDependencyRecord]: ...

    async def delete_dependencies(self, repository_id: UUID) -> None: ...


class InMemoryIndexStore(
    VectorIndexRepository,
    KeywordIndexRepository,
    MetadataIndexRepository,
    FileContentRepository,
    DependencyRepository,
    ActivityRepository,
):
    """Deterministic test adapter; production storage adapters implement the same ports."""

    def __init__(self) -> None:
        self.vector_entries: dict[tuple[UUID, str], IndexEntry] = {}
        self.keyword_entries: dict[tuple[UUID, str], KeywordIndexEntry] = {}
        self.metadata_entries: dict[tuple[UUID, str], MetadataIndexEntry] = {}
        self.file_contents: dict[tuple[UUID, str], FileContentRecord] = {}
        self.file_dependencies: dict[UUID, set[tuple[str, str]]] = {}
        self.activity_events: dict[UUID, list[ActivityEventRecord]] = {}

    async def get_hashes(self, repository_id: UUID) -> Mapping[str, str]:
        return {
            document_id: entry.content_hash
            for (stored_repository_id, document_id), entry in self.vector_entries.items()
            if stored_repository_id == repository_id
        }

    async def upsert(
        self,
        entries: Sequence[IndexEntry | KeywordIndexEntry | MetadataIndexEntry],
    ) -> None:
        for entry in entries:
            key = (entry.repository_id, entry.document_id)
            if isinstance(entry, IndexEntry):
                self.vector_entries[key] = entry
            elif isinstance(entry, KeywordIndexEntry):
                self.keyword_entries[key] = entry
            else:
                self.metadata_entries[key] = entry

    async def delete(self, repository_id: UUID, document_ids: Sequence[str]) -> None:
        for document_id in document_ids:
            key = (repository_id, document_id)
            self.vector_entries.pop(key, None)
            self.keyword_entries.pop(key, None)
            self.metadata_entries.pop(key, None)

    async def store_file_content(
        self, repository_id: UUID, file_path: str, content: str, content_hash: str
    ) -> None:
        key = (repository_id, file_path)
        self.file_contents[key] = FileContentRecord(
            repository_id=repository_id,
            file_path=file_path,
            content=content,
            content_hash=content_hash,
        )

    async def get_file_content(
        self, repository_id: UUID, file_path: str
    ) -> FileContentRecord | None:
        return self.file_contents.get((repository_id, file_path))

    async def get_file_path_hashes(self, repository_id: UUID) -> Mapping[str, str]:
        return {
            path: record.content_hash
            for (stored_repo_id, path), record in self.file_contents.items()
            if stored_repo_id == repository_id
        }

    async def delete_file_contents(self, repository_id: UUID, file_paths: Sequence[str]) -> None:
        for file_path in file_paths:
            self.file_contents.pop((repository_id, file_path), None)

    async def get_file_count(self, repository_id: UUID) -> int:
        return sum(1 for stored_repo_id, _ in self.file_contents if stored_repo_id == repository_id)

    async def store_dependencies(
        self, repository_id: UUID, edges: Sequence[tuple[str, str]]
    ) -> None:
        if repository_id not in self.file_dependencies:
            self.file_dependencies[repository_id] = set()
        self.file_dependencies[repository_id].update(edges)

    async def get_dependencies(self, repository_id: UUID) -> Sequence[FileDependencyRecord]:
        edges = self.file_dependencies.get(repository_id, set())
        return [
            FileDependencyRecord(
                repository_id=repository_id,
                source_path=source,
                target_path=target,
            )
            for source, target in edges
        ]

    async def delete_dependencies(self, repository_id: UUID) -> None:
        self.file_dependencies.pop(repository_id, None)

    async def record_activity(self, repository_id: UUID, event_type: str, message: str) -> None:
        if repository_id not in self.activity_events:
            self.activity_events[repository_id] = []
        self.activity_events[repository_id].append(
            ActivityEventRecord(
                repository_id=repository_id,
                event_type=event_type,
                message=message,
            )
        )

    async def get_activity(
        self, repository_id: UUID, limit: int = 20
    ) -> Sequence[ActivityEventRecord]:
        events = self.activity_events.get(repository_id, [])
        return events[-limit:]

    async def delete_activity(self, repository_id: UUID) -> None:
        self.activity_events.pop(repository_id, None)

    @asynccontextmanager
    async def transaction(self):
        """Rollback all in-memory projections if any index write fails."""
        vector_snapshot = self.vector_entries.copy()
        keyword_snapshot = self.keyword_entries.copy()
        metadata_snapshot = self.metadata_entries.copy()
        try:
            yield
        except Exception:
            self.vector_entries = vector_snapshot
            self.keyword_entries = keyword_snapshot
            self.metadata_entries = metadata_snapshot
            raise
