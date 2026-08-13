"""Pure, transient domain models for provider-agnostic embeddings."""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class IndexDocument:
    """Provider-facing text and metadata independent of RepoMind's Chunk model."""

    id: str
    text: str
    metadata: Mapping[str, object]


@dataclass(frozen=True, slots=True)
class EmbeddingVector:
    """A provider-generated vector for one index document."""

    document_id: str
    vector: tuple[float, ...]
    dimensions: int
    provider: str
    model: str
    created_at: datetime


@dataclass(frozen=True, slots=True)
class EmbeddingStatistics:
    """Batching and latency metrics for one transient embedding collection."""

    document_count: int
    total_tokens: int
    batch_count: int
    elapsed_time_seconds: float
    average_latency_seconds: float


@dataclass(frozen=True, slots=True)
class EmbeddingCollection:
    """Transient embedding output for all chunks in one repository collection."""

    repository_id: UUID
    provider: str
    model: str
    vectors: tuple[EmbeddingVector, ...]
    statistics: EmbeddingStatistics
    documents: tuple[IndexDocument, ...] = ()
