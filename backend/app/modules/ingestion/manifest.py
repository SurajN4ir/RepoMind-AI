"""Pure domain objects produced by repository workspace ingestion."""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal
from uuid import UUID

from app.shared.clock.utc import utc_now


@dataclass(frozen=True, slots=True)
class RepositoryFile:
    """Metadata for one accepted file in a repository workspace."""

    path: str
    size_bytes: int
    extension: str | None


@dataclass(frozen=True, slots=True)
class RepositoryStats:
    """Aggregate file-selection statistics for a repository manifest."""

    total_files: int
    total_bytes: int
    skipped_files: int
    skipped_binary_files: int
    skipped_oversized_files: int


@dataclass(frozen=True, slots=True)
class RepositoryManifest:
    """A clean inventory of repository files, without parsing their contents."""

    repository_id: UUID
    generated_at: datetime
    files: tuple[RepositoryFile, ...]
    stats: RepositoryStats
    version: Literal[1] = 1

    @classmethod
    def create(
        cls,
        repository_id: UUID,
        files: tuple[RepositoryFile, ...],
        stats: RepositoryStats,
    ) -> "RepositoryManifest":
        """Construct a versioned manifest using the shared UTC clock."""
        return cls(repository_id=repository_id, generated_at=utc_now(), files=files, stats=stats)
