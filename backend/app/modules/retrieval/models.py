"""Pure domain models for read-side hybrid retrieval."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from uuid import UUID


@dataclass(frozen=True, slots=True)
class SearchQuery:
    """A normalized repository search request with filters and pagination."""

    text: str
    repository_id: UUID | None = None
    filters: Mapping[str, object] = field(default_factory=dict)
    limit: int = 10
    offset: int = 0

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise ValueError("Search query text must not be blank.")
        if self.limit < 1 or self.limit > 100:
            raise ValueError("Search query limit must be between 1 and 100.")
        if self.offset < 0:
            raise ValueError("Search query offset cannot be negative.")


@dataclass(frozen=True, slots=True)
class SearchResult:
    """One deduplicated retrieval hit with a fused ranking score."""

    chunk_id: str
    score: float
    text: str
    metadata: Mapping[str, object]


@dataclass(frozen=True, slots=True)
class Citation:
    """Source reference derived from retrieval result metadata."""

    chunk_id: str
    file_path: str | None
    qualified_symbol_name: str | None
    line_start: int | None
    line_end: int | None


@dataclass(frozen=True, slots=True)
class RetrievalStatistics:
    """Observability metrics for one hybrid retrieval request."""

    vector_hits: int
    keyword_hits: int
    rrf_time_seconds: float
    retrieval_time_seconds: float
    rerank_time_seconds: float


@dataclass(frozen=True, slots=True)
class RetrievedContext:
    """Ordered retrieval output consumed later by agent or presentation layers."""

    query: SearchQuery
    results: tuple[SearchResult, ...]
    citations: tuple[Citation, ...]
    statistics: RetrievalStatistics
