"""Serialization contracts for transient embedding pipeline output."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.embedding.models import EmbeddingCollection


class IndexDocumentResponse(BaseModel):
    id: str
    text: str
    metadata: dict[str, Any]


class EmbeddingVectorResponse(BaseModel):
    document_id: str
    vector: list[float]
    dimensions: int = Field(ge=1)
    provider: str
    model: str
    created_at: datetime


class EmbeddingStatisticsResponse(BaseModel):
    document_count: int = Field(ge=0)
    total_tokens: int = Field(ge=0)
    batch_count: int = Field(ge=0)
    elapsed_time_seconds: float = Field(ge=0)
    average_latency_seconds: float = Field(ge=0)


class EmbeddingCollectionResponse(BaseModel):
    repository_id: UUID
    provider: str
    model: str
    vectors: list[EmbeddingVectorResponse]
    statistics: EmbeddingStatisticsResponse

    @classmethod
    def from_domain(cls, collection: EmbeddingCollection) -> "EmbeddingCollectionResponse":
        """Serialize transient vectors without adding persistence concerns."""
        return cls(
            repository_id=collection.repository_id,
            provider=collection.provider,
            model=collection.model,
            vectors=[
                EmbeddingVectorResponse(
                    document_id=vector.document_id,
                    vector=list(vector.vector),
                    dimensions=vector.dimensions,
                    provider=vector.provider,
                    model=vector.model,
                    created_at=vector.created_at,
                )
                for vector in collection.vectors
            ],
            statistics=EmbeddingStatisticsResponse(
                document_count=collection.statistics.document_count,
                total_tokens=collection.statistics.total_tokens,
                batch_count=collection.statistics.batch_count,
                elapsed_time_seconds=collection.statistics.elapsed_time_seconds,
                average_latency_seconds=collection.statistics.average_latency_seconds,
            ),
        )
