"""Serialization contracts for write-side index synchronization results."""

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.indexing.models import RepositoryIndex


class IndexEntryResponse(BaseModel):
    document_id: str
    repository_id: UUID
    dimensions: int = Field(ge=1)
    metadata: dict[str, Any]
    content_hash: str
    provider: str
    model: str


class IndexStatisticsResponse(BaseModel):
    inserted: int = Field(ge=0)
    updated: int = Field(ge=0)
    deleted: int = Field(ge=0)
    unchanged: int = Field(ge=0)
    elapsed_time_seconds: float = Field(ge=0)


class RepositoryIndexResponse(BaseModel):
    repository_id: UUID
    vector_entries: list[IndexEntryResponse]
    keyword_document_ids: list[str]
    metadata_document_ids: list[str]
    statistics: IndexStatisticsResponse

    @classmethod
    def from_domain(cls, index: RepositoryIndex) -> "RepositoryIndexResponse":
        """Serialize index-write results without exposing search implementation details."""
        return cls(
            repository_id=index.repository_id,
            vector_entries=[
                IndexEntryResponse(
                    document_id=entry.document_id,
                    repository_id=entry.repository_id,
                    dimensions=len(entry.embedding),
                    metadata=dict(entry.metadata),
                    content_hash=entry.content_hash,
                    provider=entry.provider,
                    model=entry.model,
                )
                for entry in index.vector_entries
            ],
            keyword_document_ids=[entry.document_id for entry in index.keyword_entries],
            metadata_document_ids=[entry.document_id for entry in index.metadata_entries],
            statistics=IndexStatisticsResponse(
                inserted=index.statistics.inserted,
                updated=index.statistics.updated,
                deleted=index.statistics.deleted,
                unchanged=index.statistics.unchanged,
                elapsed_time_seconds=index.statistics.elapsed_time_seconds,
            ),
        )
