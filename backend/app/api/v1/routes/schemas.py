"""HTTP response contracts for application-layer pipeline endpoints."""

from uuid import UUID

from pydantic import BaseModel, Field

from app.application.pipelines.models import QueryResult, RepositoryIndexingResult


class CitationDetail(BaseModel):
    """Citation details returned to the frontend."""

    filePath: str
    lineStart: int
    lineEnd: int


class IndexingResponse(BaseModel):
    """Pydantic contract for the repository indexing endpoint response."""

    repository_id: UUID
    success: bool
    elapsed_seconds: float
    errors: list[str]
    chunks_created: bool
    indexed: bool

    @classmethod
    def from_result(cls, result: RepositoryIndexingResult) -> "IndexingResponse":
        return cls(
            repository_id=result.repository_id,
            success=result.success,
            elapsed_seconds=result.elapsed_seconds,
            errors=list(result.errors),
            chunks_created=result.chunks is not None,
            indexed=result.repository_index is not None,
        )


class QueryRequest(BaseModel):
    """Request body for the repository query endpoint."""

    text: str
    preferences: dict[str, object] = Field(default_factory=dict)
    conversation_id: UUID | None = None


class QueryResponse(BaseModel):
    """Pydantic contract for the repository query endpoint response."""

    repository_id: UUID
    success: bool
    elapsed_seconds: float
    errors: list[str]
    response_text: str | None = None
    citation_count: int = 0
    citations: list[CitationDetail] = Field(default_factory=list)

    @classmethod
    def from_result(cls, result: QueryResult, repository_id: UUID) -> "QueryResponse":
        citations = []
        if result.response:
            for c in result.response.citations:
                if c.file_path:
                    citations.append(
                        CitationDetail(
                            filePath=c.file_path,
                            lineStart=c.line_start or 0,
                            lineEnd=c.line_end or 0,
                        )
                    )
        return cls(
            repository_id=repository_id,
            success=result.success,
            elapsed_seconds=result.elapsed_seconds,
            errors=list(result.errors),
            response_text=result.response.text if result.response else None,
            citation_count=len(citations),
            citations=citations,
        )
