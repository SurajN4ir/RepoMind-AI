"""Serialization contracts for hybrid retrieval output."""

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.retrieval.models import RetrievedContext


class SearchQueryRequest(BaseModel):
    text: str = Field(min_length=1)
    repository_id: UUID | None = None
    filters: dict[str, Any] = Field(default_factory=dict)
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class SearchResultResponse(BaseModel):
    chunk_id: str
    score: float
    text: str
    metadata: dict[str, Any]


class CitationResponse(BaseModel):
    chunk_id: str
    file_path: str | None
    qualified_symbol_name: str | None
    line_start: int | None
    line_end: int | None


class RetrievalStatisticsResponse(BaseModel):
    vector_hits: int = Field(ge=0)
    keyword_hits: int = Field(ge=0)
    rrf_time_seconds: float = Field(ge=0)
    retrieval_time_seconds: float = Field(ge=0)
    rerank_time_seconds: float = Field(ge=0)


class RetrievedContextResponse(BaseModel):
    query: SearchQueryRequest
    results: list[SearchResultResponse]
    citations: list[CitationResponse]
    statistics: RetrievalStatisticsResponse

    @classmethod
    def from_domain(cls, context: RetrievedContext) -> "RetrievedContextResponse":
        """Serialize ordered retrieval context without any language-model interaction."""
        return cls(
            query=SearchQueryRequest(
                text=context.query.text,
                repository_id=context.query.repository_id,
                filters=dict(context.query.filters),
                limit=context.query.limit,
                offset=context.query.offset,
            ),
            results=[
                SearchResultResponse(
                    chunk_id=result.chunk_id,
                    score=result.score,
                    text=result.text,
                    metadata=dict(result.metadata),
                )
                for result in context.results
            ],
            citations=[
                CitationResponse(
                    chunk_id=citation.chunk_id,
                    file_path=citation.file_path,
                    qualified_symbol_name=citation.qualified_symbol_name,
                    line_start=citation.line_start,
                    line_end=citation.line_end,
                )
                for citation in context.citations
            ],
            statistics=RetrievalStatisticsResponse(
                vector_hits=context.statistics.vector_hits,
                keyword_hits=context.statistics.keyword_hits,
                rrf_time_seconds=context.statistics.rrf_time_seconds,
                retrieval_time_seconds=context.statistics.retrieval_time_seconds,
                rerank_time_seconds=context.statistics.rerank_time_seconds,
            ),
        )
