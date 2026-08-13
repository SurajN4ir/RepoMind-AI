"""HTTP response contracts for repository workspace ingestion."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.ingestion.manifest import RepositoryManifest


class RepositoryFileResponse(BaseModel):
    """Serializable metadata for one accepted repository file."""

    path: str
    size_bytes: int = Field(ge=0)
    extension: str | None


class RepositoryStatsResponse(BaseModel):
    """Serializable aggregate repository manifest statistics."""

    total_files: int = Field(ge=0)
    total_bytes: int = Field(ge=0)
    skipped_files: int = Field(ge=0)
    skipped_binary_files: int = Field(ge=0)
    skipped_oversized_files: int = Field(ge=0)


class RepositoryManifestResponse(BaseModel):
    """HTTP representation of a generated, non-persistent repository manifest."""

    version: int
    repository_id: UUID
    generated_at: datetime
    files: list[RepositoryFileResponse]
    stats: RepositoryStatsResponse

    @classmethod
    def from_manifest(cls, manifest: RepositoryManifest) -> "RepositoryManifestResponse":
        """Map pure manifest objects to the feature's response contract."""
        return cls(
            version=manifest.version,
            repository_id=manifest.repository_id,
            generated_at=manifest.generated_at,
            files=[
                RepositoryFileResponse(
                    path=file.path,
                    size_bytes=file.size_bytes,
                    extension=file.extension,
                )
                for file in manifest.files
            ],
            stats=RepositoryStatsResponse(
                total_files=manifest.stats.total_files,
                total_bytes=manifest.stats.total_bytes,
                skipped_files=manifest.stats.skipped_files,
                skipped_binary_files=manifest.stats.skipped_binary_files,
                skipped_oversized_files=manifest.stats.skipped_oversized_files,
            ),
        )
