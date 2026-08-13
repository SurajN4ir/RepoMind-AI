"""Async unit tests for hybrid, read-side retrieval orchestration."""

from datetime import UTC, datetime
from uuid import UUID

import pytest

from app.modules.embedding.models import EmbeddingVector, IndexDocument
from app.modules.indexing.models import IndexEntry
from app.modules.retrieval.exceptions import QueryEmbeddingError
from app.modules.retrieval.models import SearchQuery, SearchResult
from app.modules.retrieval.repository import InMemorySearchStore
from app.modules.retrieval.rrf import ReciprocalRankFusion
from app.modules.retrieval.service import RetrievalService
from app.shared.identifiers.uuid import new_uuid


def _entry(
    document_id: str,
    repository_id: UUID,
    vector: tuple[float, ...],
    text: str,
    **metadata: object,
) -> IndexEntry:
    return IndexEntry(
        document_id=document_id,
        repository_id=repository_id,
        embedding=vector,
        text=text,
        metadata={
            "file_path": f"src/{document_id}.py",
            "qualified_symbol_name": document_id,
            "line_range": {"start": 1, "end": 4},
            "language": "python",
            **metadata,
        },
        content_hash=document_id,
        provider="test",
        model="test-model",
    )


class _QueryProvider:
    provider_name = "test"
    model_name = "test-model"

    async def embed(self, documents: list[IndexDocument]) -> list[EmbeddingVector]:
        return [
            EmbeddingVector(
                document_id=document.id,
                vector=(1.0, 0.0),
                dimensions=2,
                provider=self.provider_name,
                model=self.model_name,
                created_at=datetime.now(UTC),
            )
            for document in documents
        ]


class _FailingQueryProvider(_QueryProvider):
    async def embed(self, documents: list[IndexDocument]) -> list[EmbeddingVector]:
        from app.modules.embedding.exceptions import EmbeddingProviderError

        raise EmbeddingProviderError("provider unavailable")


def _service(store: InMemorySearchStore) -> RetrievalService:
    return RetrievalService(_QueryProvider(), store, store, store)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_hybrid_retrieval_fuses_results_deduplicates_and_builds_citations() -> None:
    repository_id = new_uuid()
    store = InMemorySearchStore(
        (
            _entry("auth", repository_id, (1.0, 0.0), "JWT authentication service"),
            _entry("token", repository_id, (0.0, 1.0), "authentication token utilities"),
        )
    )

    context = await _service(store).retrieve(SearchQuery("JWT authentication", repository_id))

    assert [result.chunk_id for result in context.results] == ["auth", "token"]
    assert len({result.chunk_id for result in context.results}) == 2
    assert context.statistics.vector_hits == 2
    assert context.statistics.keyword_hits == 2
    assert context.citations[0].file_path == "src/auth.py"
    assert context.citations[0].line_start == 1


@pytest.mark.asyncio
async def test_retrieval_applies_metadata_filters_and_pagination() -> None:
    repository_id = new_uuid()
    store = InMemorySearchStore(
        (
            _entry("python", repository_id, (1.0, 0.0), "authentication", language="python"),
            _entry(
                "typescript",
                repository_id,
                (0.9, 0.1),
                "authentication",
                language="typescript",
            ),
            _entry("second", repository_id, (0.8, 0.2), "authentication", language="python"),
        )
    )

    filtered = await _service(store).retrieve(
        SearchQuery(
            "authentication",
            repository_id,
            filters={"language": "python"},
            limit=1,
            offset=1,
        )
    )

    assert len(filtered.results) == 1
    assert filtered.results[0].metadata["language"] == "python"


def test_rrf_uses_configurable_fusion_and_deduplicates() -> None:
    first = SearchResult("shared", 1.0, "first", {})
    second = SearchResult("keyword", 0.5, "second", {})
    vector_only = SearchResult("vector", 0.5, "third", {})

    fused = ReciprocalRankFusion(fusion_constant=10).fuse(
        (first, vector_only),
        (first, second),
    )

    assert [result.chunk_id for result in fused] == ["shared", "keyword", "vector"]
    assert fused[0].score == pytest.approx(2 / 11)


def test_search_query_rejects_empty_text_and_invalid_pagination() -> None:
    with pytest.raises(ValueError):
        SearchQuery("   ")
    with pytest.raises(ValueError):
        SearchQuery("valid", limit=0)
    with pytest.raises(ValueError):
        SearchQuery("valid", offset=-1)


@pytest.mark.asyncio
async def test_retrieval_returns_empty_context_when_indexes_have_no_hits() -> None:
    context = await _service(InMemorySearchStore(())).retrieve(SearchQuery("authentication"))

    assert context.results == ()
    assert context.citations == ()
    assert context.statistics.vector_hits == 0
    assert context.statistics.keyword_hits == 0


@pytest.mark.asyncio
async def test_retrieval_translates_query_embedding_failures() -> None:
    store = InMemorySearchStore(())
    provider = _FailingQueryProvider()
    service = RetrievalService(provider, store, store, store)  # type: ignore[arg-type]

    with pytest.raises(QueryEmbeddingError):
        await service.retrieve(SearchQuery("authentication"))
