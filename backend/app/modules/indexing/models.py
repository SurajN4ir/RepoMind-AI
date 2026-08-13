"""Pure domain models for provider-neutral write-side indexing."""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class IndexEntry:
    """All write-side index representations for one embedding document."""

    document_id: str
    repository_id: UUID
    embedding: tuple[float, ...]
    text: str
    metadata: Mapping[str, object]
    content_hash: str
    provider: str
    model: str


@dataclass(frozen=True, slots=True)
class KeywordIndexEntry:
    """Keyword-index representation derived from an index entry."""

    document_id: str
    repository_id: UUID
    text: str


@dataclass(frozen=True, slots=True)
class MetadataIndexEntry:
    """Metadata-index representation derived from an index entry."""

    document_id: str
    repository_id: UUID
    metadata: Mapping[str, object]


@dataclass(frozen=True, slots=True)
class IndexStatistics:
    """Outcome metrics for one idempotent repository indexing operation."""

    inserted: int
    updated: int
    deleted: int
    unchanged: int
    elapsed_time_seconds: float


@dataclass(frozen=True, slots=True)
class RepositoryIndex:
    """Logical result of writing vector, keyword, and metadata index projections."""

    repository_id: UUID
    vector_entries: tuple[IndexEntry, ...]
    keyword_entries: tuple[KeywordIndexEntry, ...]
    metadata_entries: tuple[MetadataIndexEntry, ...]
    statistics: IndexStatistics


@dataclass(frozen=True, slots=True)
class FileContentRecord:
    """Full file content for one indexed repository file."""

    repository_id: UUID
    file_path: str
    content: str
    content_hash: str
    created_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class FileDependencyRecord:
    """One resolved cross-file dependency edge between two repository files."""

    repository_id: UUID
    source_path: str
    target_path: str


@dataclass(frozen=True, slots=True)
class ActivityEventRecord:
    """One recorded activity event for a repository."""

    repository_id: UUID
    event_type: str
    message: str
    created_at: datetime | None = None
