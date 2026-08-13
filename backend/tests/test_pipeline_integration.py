"""Integration tests for the complete RepositoryIndexingPipeline.

Exercises the full pipeline flow — including embed and index steps —
using a mock embedding provider and the in-memory index store so tests
remain fast and deterministic.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from app.application.pipelines.models import PipelineContext, RepositoryIndexingResult
from app.application.pipelines.repository_indexing_pipeline import (
    RepositoryIndexingPipeline,
)
from app.modules.chunker.models import Chunk, ChunkCollection, ChunkType
from app.modules.embedding.models import EmbeddingVector
from app.modules.embedding.service import EmbeddingService
from app.modules.indexing.repository import InMemoryIndexStore
from app.modules.indexing.service import IndexingService
from app.modules.parser.language import SupportedLanguage
from app.modules.parser.models import SymbolKind
from app.modules.repository.enums import RepositoryStatus
from app.modules.repository.models import Repository
from app.shared.identifiers.uuid import new_uuid


@dataclass
class _FakeRepositoryService:
    """Simulates RepositoryApplicationService for pipeline tests."""

    record: Repository
    status_updates: list[tuple[RepositoryStatus, datetime | None]] = field(default_factory=list)

    async def get(self, repository_id: UUID) -> Repository:
        if repository_id != self.record.id:
            from app.application.exceptions import EntityNotFoundError

            raise EntityNotFoundError("Repository not found")
        return self.record

    async def update_status(
        self,
        repository_id: UUID,
        status: RepositoryStatus,
        *,
        last_indexed_at: datetime | None = None,
    ) -> Repository:
        if repository_id != self.record.id:
            from app.application.exceptions import EntityNotFoundError

            raise EntityNotFoundError("Repository not found")
        self.record.status = status
        self.status_updates.append((status, last_indexed_at))
        return self.record


@pytest.fixture
def repository() -> Repository:
    return Repository(
        id=new_uuid(),
        name="test-repo",
        url="https://github.com/example/test-repo",
        provider="github",
        status=RepositoryStatus.REGISTERED,
    )


@pytest.fixture
def chunk_collection(repository: Repository) -> ChunkCollection:
    chunk = Chunk(
        id="chunk-1",
        repository_id=repository.id,
        file_path="src/main.py",
        language=SupportedLanguage.PYTHON,
        symbol_name="hello",
        qualified_symbol_name="hello",
        symbol_kind=SymbolKind.FUNCTION,
        content="def hello():\n    print('hello')\n",
        start_line=1,
        end_line=5,
        token_count=5,
        chunk_type=ChunkType.FUNCTION,
        metadata={},
    )
    return ChunkCollection.create(repository.id, (chunk,))


@pytest.fixture
def context(repository: Repository) -> PipelineContext:
    return PipelineContext(repository_id=repository.id, repository=repository)


def _fake_embedding_service() -> EmbeddingService:
    provider = AsyncMock()
    provider.provider_name = "test-provider"
    provider.model_name = "test-model"
    provider.embed.return_value = [
        EmbeddingVector(
            document_id="chunk-1",
            vector=(0.1, 0.2, 0.3),
            dimensions=3,
            provider="test-provider",
            model="test-model",
            created_at=datetime.now(UTC),
        )
    ]
    return EmbeddingService(provider)


def _fake_repo_service(repository: Repository) -> _FakeRepositoryService:
    return _FakeRepositoryService(repository)


class TestPipelineEmbedStep:
    """Verify that embedding executes when an EmbeddingService is injected."""

    @pytest.mark.asyncio
    async def test_embed_produces_collection(
        self, repository: Repository, chunk_collection: ChunkCollection, context: PipelineContext
    ) -> None:
        repo_service = _fake_repo_service(repository)
        embedding = _fake_embedding_service()
        pipeline = RepositoryIndexingPipeline(
            repository_service=repo_service,  # type: ignore[arg-type]
            embedding_service=embedding,
        )
        context.chunks = chunk_collection

        collection = await pipeline._embed(context)

        assert collection is not None
        assert collection.repository_id == repository.id
        assert len(collection.vectors) == 1
        assert collection.vectors[0].document_id == "chunk-1"

    @pytest.mark.asyncio
    async def test_embed_raises_without_chunks(self, context: PipelineContext) -> None:
        pipeline = RepositoryIndexingPipeline(
            repository_service=_fake_repo_service(  # type: ignore[arg-type]
                Repository(
                    id=new_uuid(),
                    name="test",
                    url="https://example.com/test",
                    provider="github",
                    status=RepositoryStatus.REGISTERED,
                )
            ),
            embedding_service=_fake_embedding_service(),
        )

        with pytest.raises(Exception, match="Cannot embed without chunks"):
            await pipeline._embed(context)


class TestPipelineIndexStep:
    """Verify that indexing executes when an IndexingService is injected."""

    @pytest.mark.asyncio
    async def test_index_writes_to_store(
        self, repository: Repository, chunk_collection: ChunkCollection, context: PipelineContext
    ) -> None:
        repo_service = _fake_repo_service(repository)
        store = InMemoryIndexStore()
        indexing = IndexingService(store, store, store, store)
        embedding = _fake_embedding_service()
        pipeline = RepositoryIndexingPipeline(
            repository_service=repo_service,  # type: ignore[arg-type]
            embedding_service=embedding,
            indexing_service=indexing,
        )

        context.chunks = chunk_collection
        context.embedding_collection = await pipeline._embed(context)
        result = await pipeline._index(context)

        assert result is not None
        assert result.repository_id == repository.id
        assert len(store.vector_entries) >= 1
        assert len(store.keyword_entries) >= 1
        assert len(store.metadata_entries) >= 1


class TestPipelineStatusTransitions:
    """Verify that the pipeline owns status transitions correctly."""

    @pytest.mark.asyncio
    async def test_validate_rejects_archived(self, repository: Repository) -> None:
        repository.status = RepositoryStatus.ARCHIVED
        repo_service = _fake_repo_service(repository)
        pipeline = RepositoryIndexingPipeline(
            repository_service=repo_service  # type: ignore[arg-type]
        )

        result = await pipeline.execute(repository.id)

        assert result.success is False
        assert any("ARCHIVED" in e for e in result.errors)
        assert repo_service.status_updates == []

    @pytest.mark.asyncio
    async def test_execute_sets_indexing_then_failed_on_error(self, repository: Repository) -> None:
        repo_service = _fake_repo_service(repository)
        pipeline = RepositoryIndexingPipeline(
            repository_service=repo_service  # type: ignore[arg-type]
        )

        result = await pipeline.execute(repository.id)

        assert result.success is False
        assert len(repo_service.status_updates) == 2
        assert repo_service.status_updates[0][0] == RepositoryStatus.INDEXING
        assert repo_service.status_updates[1][0] == RepositoryStatus.FAILED


class TestPipelineFullWiring:
    """End-to-end pipeline with all services wired."""

    @pytest.mark.asyncio
    async def test_pipeline_returns_result_object(
        self, repository: Repository, chunk_collection: ChunkCollection
    ) -> None:
        repo_service = _fake_repo_service(repository)
        store = InMemoryIndexStore()
        indexing = IndexingService(store, store, store, store)
        pipeline = RepositoryIndexingPipeline(
            repository_service=repo_service,  # type: ignore[arg-type]
            embedding_service=_fake_embedding_service(),
            indexing_service=indexing,
        )

        result = await pipeline.execute(
            repository.id,
            clone_url="https://github.com/example/test-repo.git",
        )

        assert isinstance(result, RepositoryIndexingResult)
        assert result.repository_id == repository.id
        assert result.success is False

    @pytest.mark.asyncio
    async def test_embedding_service_guarded_when_none(self, repository: Repository) -> None:
        pipeline = RepositoryIndexingPipeline(
            repository_service=_fake_repo_service(repository),  # type: ignore[arg-type]
            embedding_service=None,
            indexing_service=None,
        )

        context = PipelineContext(repository_id=repository.id, repository=repository)
        context.chunks = ChunkCollection.create(repository.id, ())

        with pytest.raises(Exception, match="Embedding service is not configured"):
            await pipeline._embed(context)
