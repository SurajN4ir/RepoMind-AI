"""Integration tests for the complete RepositoryQueryPipeline.

Exercises the full query pipeline flow — planning, retrieval, context
building, and response generation — using fake or mock adapters so
tests remain fast and deterministic.
"""

from collections.abc import Sequence
from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from app.application.pipelines.models import QueryPipelineContext, QueryResult
from app.application.pipelines.repository_query_pipeline import (
    RepositoryQueryPipeline,
)
from app.modules.context_builder.models import LLMContext
from app.modules.context_builder.service import ContextBuilderService
from app.modules.embedding.models import EmbeddingVector
from app.modules.indexing.models import IndexEntry
from app.modules.orchestrator.models import GeneratedResponse
from app.modules.orchestrator.service import OrchestratorService
from app.modules.query_engine.models import QueryIntent, QueryPlan, RepositoryReference, UserRequest
from app.modules.query_engine.service import QueryEngineService
from app.modules.retrieval.models import (
    Citation,
    RetrievalStatistics,
    RetrievedContext,
    SearchQuery,
    SearchResult,
)
from app.modules.retrieval.repository import InMemorySearchStore
from app.modules.retrieval.service import RetrievalService
from app.shared.identifiers.uuid import new_uuid


@pytest.fixture
def repository_id() -> UUID:
    return new_uuid()


@pytest.fixture
def search_query(repository_id: UUID) -> SearchQuery:
    return SearchQuery(text="find the login function", repository_id=repository_id)


@pytest.fixture
def search_results(repository_id: UUID) -> tuple[SearchResult, ...]:
    return (
        SearchResult(
            chunk_id="chunk-1",
            score=0.95,
            text="def login(username, password):\n    return authenticate(username, password)",
            metadata={"file_path": "src/auth.py", "language": "python"},
        ),
        SearchResult(
            chunk_id="chunk-2",
            score=0.85,
            text="class LoginForm:\n    def validate(self):\n        return self.is_valid()",
            metadata={"file_path": "src/forms.py", "language": "python"},
        ),
    )


@pytest.fixture
def citations() -> tuple[Citation, ...]:
    return (
        Citation(
            chunk_id="chunk-1",
            file_path="src/auth.py",
            qualified_symbol_name="login",
            line_start=1,
            line_end=3,
        ),
        Citation(
            chunk_id="chunk-2",
            file_path="src/forms.py",
            qualified_symbol_name="LoginForm",
            line_start=1,
            line_end=3,
        ),
    )


@pytest.fixture
def retrieved_context(
    search_query: SearchQuery,
    search_results: tuple[SearchResult, ...],
    citations: tuple[Citation, ...],
) -> RetrievedContext:
    return RetrievedContext(
        query=search_query,
        results=search_results,
        citations=citations,
        statistics=RetrievalStatistics(
            vector_hits=2,
            keyword_hits=2,
            rrf_time_seconds=0.01,
            retrieval_time_seconds=0.05,
            rerank_time_seconds=0.0,
        ),
    )


class _FakeRepositoryResolver:
    """Returns a fixed set of repositories for query engine scope resolution."""

    def __init__(self, repositories: Sequence[RepositoryReference]) -> None:
        self._repositories = repositories

    async def list_repositories(self) -> Sequence[RepositoryReference]:
        return self._repositories


class TestQueryPipelinePlanStep:
    """Verify that the plan step produces a QueryPlan through the injected engine."""

    @pytest.mark.asyncio
    async def test_plan_creates_query_plan(self, repository_id: UUID) -> None:
        resolver = _FakeRepositoryResolver(
            [RepositoryReference(id=repository_id, name="test-repo")]
        )
        query_engine = QueryEngineService(resolver)
        pipeline = RepositoryQueryPipeline(
            query_engine=query_engine,
            retrieval_service=AsyncMock(),  # type: ignore[arg-type]
            context_builder=AsyncMock(),  # type: ignore[arg-type]
            orchestrator=AsyncMock(),  # type: ignore[arg-type]
        )
        request = UserRequest(text="find the login function", repository_id=repository_id)

        plan = await pipeline._plan(QueryPipelineContext(request=request))

        assert isinstance(plan, QueryPlan)
        assert plan.intent is QueryIntent.SEARCH_SYMBOL
        assert plan.search_query.text == "the login function"
        assert plan.search_query.repository_id == repository_id

    @pytest.mark.asyncio
    async def test_plan_updates_context(self, repository_id: UUID) -> None:
        resolver = _FakeRepositoryResolver(
            [RepositoryReference(id=repository_id, name="test-repo")]
        )
        query_engine = QueryEngineService(resolver)
        pipeline = RepositoryQueryPipeline(
            query_engine=query_engine,
            retrieval_service=AsyncMock(),  # type: ignore[arg-type]
            context_builder=AsyncMock(),  # type: ignore[arg-type]
            orchestrator=AsyncMock(),  # type: ignore[arg-type]
        )
        request = UserRequest(text="explain the architecture", repository_id=repository_id)
        context = QueryPipelineContext(request=request)

        await pipeline._plan(context)

        assert context.plan is not None
        assert context.plan.search_query.repository_id == repository_id


class TestQueryPipelineRetrieveStep:
    """Verify that the retrieve step runs retrieval through the injected service."""

    @pytest.mark.asyncio
    async def test_retrieve_returns_context(
        self,
        repository_id: UUID,
        search_query: SearchQuery,
    ) -> None:
        entries = [
            IndexEntry(
                document_id="chunk-1",
                repository_id=repository_id,
                embedding=(0.1, 0.2, 0.3),
                text="def login(username, password):\n    return authenticate(username, password)",
                metadata={"file_path": "src/auth.py", "language": "python"},
                content_hash="abc",
                provider="test",
                model="test",
            ),
        ]
        store = InMemorySearchStore(entries)
        embed_provider = AsyncMock()
        embed_provider.provider_name = "test"
        embed_provider.model_name = "test"
        embed_provider.embed.return_value = [
            EmbeddingVector(
                document_id="query:abc",
                vector=(0.1, 0.2, 0.3),
                dimensions=3,
                provider="test",
                model="test",
                created_at=datetime.now(UTC),
            )
        ]
        retrieval = RetrievalService(embed_provider, store, store, store)
        pipeline = RepositoryQueryPipeline(
            query_engine=AsyncMock(),  # type: ignore[arg-type]
            retrieval_service=retrieval,
            context_builder=AsyncMock(),  # type: ignore[arg-type]
            orchestrator=AsyncMock(),  # type: ignore[arg-type]
        )
        plan = QueryPlan(
            intent=QueryIntent.SEARCH_CODE,
            search_query=search_query,
            confidence=0.9,
        )

        retrieved = await pipeline._retrieve(
            QueryPipelineContext(request=UserRequest(text="test")), plan
        )

        assert isinstance(retrieved, RetrievedContext)
        assert len(retrieved.results) >= 1
        assert retrieved.results[0].chunk_id == "chunk-1"

    @pytest.mark.asyncio
    async def test_retrieve_returns_empty_when_no_match(
        self,
        repository_id: UUID,
        search_query: SearchQuery,
    ) -> None:
        store = InMemorySearchStore(())
        embed_provider = AsyncMock()
        embed_provider.provider_name = "test"
        embed_provider.model_name = "test"
        embed_provider.embed.return_value = [
            EmbeddingVector(
                document_id="query:abc",
                vector=(0.9, 0.8, 0.7),
                dimensions=3,
                provider="test",
                model="test",
                created_at=datetime.now(UTC),
            )
        ]
        retrieval = RetrievalService(embed_provider, store, store, store)
        pipeline = RepositoryQueryPipeline(
            query_engine=AsyncMock(),  # type: ignore[arg-type]
            retrieval_service=retrieval,
            context_builder=AsyncMock(),  # type: ignore[arg-type]
            orchestrator=AsyncMock(),  # type: ignore[arg-type]
        )
        plan = QueryPlan(
            intent=QueryIntent.SEARCH_CODE,
            search_query=search_query,
            confidence=0.9,
        )

        retrieved = await pipeline._retrieve(
            QueryPipelineContext(request=UserRequest(text="test")), plan
        )

        assert len(retrieved.results) == 0
        assert len(retrieved.citations) == 0


class TestQueryPipelineContextBuildStep:
    """Verify the context building step converts RetrievedContext to LLMContext."""

    @pytest.mark.asyncio
    async def test_build_context_returns_llm_context(
        self,
        retrieved_context: RetrievedContext,
    ) -> None:
        pipeline = RepositoryQueryPipeline(
            query_engine=AsyncMock(),  # type: ignore[arg-type]
            retrieval_service=AsyncMock(),  # type: ignore[arg-type]
            context_builder=ContextBuilderService(),
            orchestrator=AsyncMock(),  # type: ignore[arg-type]
        )

        llm_context = await pipeline._build_context(
            QueryPipelineContext(request=UserRequest(text="test")),
            retrieved_context,
        )

        assert isinstance(llm_context, LLMContext)
        assert llm_context.query.text == retrieved_context.query.text
        assert len(llm_context.sections) >= 1
        assert llm_context.statistics.retained_chunk_count > 0
        assert llm_context.formatted_text

    @pytest.mark.asyncio
    async def test_build_context_handles_empty_results(self) -> None:
        query = SearchQuery(text="nothing")
        empty = RetrievedContext(
            query=query,
            results=(),
            citations=(),
            statistics=RetrievalStatistics(
                vector_hits=0,
                keyword_hits=0,
                rrf_time_seconds=0.0,
                retrieval_time_seconds=0.0,
                rerank_time_seconds=0.0,
            ),
        )
        pipeline = RepositoryQueryPipeline(
            query_engine=AsyncMock(),  # type: ignore[arg-type]
            retrieval_service=AsyncMock(),  # type: ignore[arg-type]
            context_builder=ContextBuilderService(),
            orchestrator=AsyncMock(),  # type: ignore[arg-type]
        )

        llm_context = await pipeline._build_context(
            QueryPipelineContext(request=UserRequest(text="test")),
            empty,
        )

        assert isinstance(llm_context, LLMContext)
        assert len(llm_context.sections) == 0
        assert llm_context.statistics.retained_chunk_count == 0


class TestQueryPipelineRespondStep:
    """Verify the respond step generates a response through the orchestrator."""

    @pytest.mark.asyncio
    async def test_respond_returns_generated_response(
        self,
        retrieved_context: RetrievedContext,
    ) -> None:
        context_builder = ContextBuilderService()
        llm_context = await context_builder.build(retrieved_context)

        workflow_engine = AsyncMock()
        workflow_engine.execute.return_value = (
            "The login function is defined in src/auth.py.",
            (),
            0.15,
        )
        orchestrator = OrchestratorService(workflow_engine)
        pipeline = RepositoryQueryPipeline(
            query_engine=AsyncMock(),  # type: ignore[arg-type]
            retrieval_service=AsyncMock(),  # type: ignore[arg-type]
            context_builder=context_builder,
            orchestrator=orchestrator,
        )

        response = await pipeline._respond(
            QueryPipelineContext(request=UserRequest(text="test")),
            llm_context,
        )

        assert isinstance(response, GeneratedResponse)
        assert response.text == "The login function is defined in src/auth.py."
        assert len(response.citations) > 0


class TestQueryPipelineFullFlow:
    """End-to-end query pipeline with all services wired via fake adapters."""

    @pytest.mark.asyncio
    async def test_execute_returns_query_result_with_success(
        self,
        repository_id: UUID,
    ) -> None:
        resolver = _FakeRepositoryResolver(
            [RepositoryReference(id=repository_id, name="test-repo")]
        )
        query_engine = QueryEngineService(resolver)

        entries = [
            IndexEntry(
                document_id="chunk-1",
                repository_id=repository_id,
                embedding=(0.1, 0.2, 0.3),
                text="def login(username, password):\n    return authenticate(username, password)",
                metadata={"file_path": "src/auth.py", "language": "python"},
                content_hash="abc",
                provider="test",
                model="test",
            ),
        ]
        store = InMemorySearchStore(entries)
        embed_provider = AsyncMock()
        embed_provider.provider_name = "test"
        embed_provider.model_name = "test"
        embed_provider.embed.return_value = [
            EmbeddingVector(
                document_id="query:abc",
                vector=(0.1, 0.2, 0.3),
                dimensions=3,
                provider="test",
                model="test",
                created_at=datetime.now(UTC),
            )
        ]
        retrieval = RetrievalService(embed_provider, store, store, store)
        context_builder = ContextBuilderService()

        workflow_engine = AsyncMock()
        workflow_engine.execute.return_value = (
            "The login function is defined in src/auth.py.",
            (),
            0.15,
        )
        orchestrator = OrchestratorService(workflow_engine)

        pipeline = RepositoryQueryPipeline(
            query_engine=query_engine,
            retrieval_service=retrieval,
            context_builder=context_builder,
            orchestrator=orchestrator,
        )
        request = UserRequest(text="find the login function", repository_id=repository_id)

        result = await pipeline.execute(request)

        assert isinstance(result, QueryResult)
        assert result.success
        assert result.request is request
        assert result.plan is not None
        assert result.retrieved_context is not None
        assert result.llm_context is not None
        assert result.response is not None
        assert result.response.text == "The login function is defined in src/auth.py."
        assert len(result.errors) == 0
        assert result.elapsed_seconds >= 0

    @pytest.mark.asyncio
    async def test_execute_sets_success_true_and_populates_all_intermediates(
        self,
        repository_id: UUID,
    ) -> None:
        resolver = _FakeRepositoryResolver(
            [RepositoryReference(id=repository_id, name="test-repo")]
        )
        query_engine = QueryEngineService(resolver)

        store = InMemorySearchStore(())
        embed_provider = AsyncMock()
        embed_provider.provider_name = "test"
        embed_provider.model_name = "test"
        embed_provider.embed.return_value = [
            EmbeddingVector(
                document_id="query:abc",
                vector=(0.1, 0.2, 0.3),
                dimensions=3,
                provider="test",
                model="test",
                created_at=datetime.now(UTC),
            )
        ]
        retrieval = RetrievalService(embed_provider, store, store, store)
        context_builder = ContextBuilderService()

        workflow_engine = AsyncMock()
        workflow_engine.execute.return_value = (
            "No relevant code found.",
            (),
            0.1,
        )
        orchestrator = OrchestratorService(workflow_engine)

        pipeline = RepositoryQueryPipeline(
            query_engine=query_engine,
            retrieval_service=retrieval,
            context_builder=context_builder,
            orchestrator=orchestrator,
        )
        request = UserRequest(text="find the login function", repository_id=repository_id)

        result = await pipeline.execute(request)

        assert result.success
        assert result.plan is not None
        assert result.retrieved_context is not None
        assert len(result.retrieved_context.results) == 0
        assert result.llm_context is not None
        assert result.response is not None


class TestQueryPipelineErrorHandling:
    """Verify the pipeline catches step failures and returns a structured error result."""

    @pytest.mark.asyncio
    async def test_execute_returns_failed_result_on_plan_error(self, repository_id: UUID) -> None:
        failing_engine = AsyncMock()
        failing_engine.plan.side_effect = ValueError("Plan failed")
        pipeline = RepositoryQueryPipeline(
            query_engine=failing_engine,  # type: ignore[arg-type]
            retrieval_service=AsyncMock(),  # type: ignore[arg-type]
            context_builder=AsyncMock(),  # type: ignore[arg-type]
            orchestrator=AsyncMock(),  # type: ignore[arg-type]
        )
        request = UserRequest(text="test", repository_id=repository_id)

        result = await pipeline.execute(request)

        assert result.success is False
        assert result.response is None
        assert len(result.errors) > 0

    @pytest.mark.asyncio
    async def test_execute_returns_failed_result_on_retrieval_error(
        self, repository_id: UUID
    ) -> None:
        resolver = _FakeRepositoryResolver(
            [RepositoryReference(id=repository_id, name="test-repo")]
        )
        query_engine = QueryEngineService(resolver)
        failing_retrieval = AsyncMock()
        failing_retrieval.retrieve.side_effect = RuntimeError("Retrieval failed")
        pipeline = RepositoryQueryPipeline(
            query_engine=query_engine,
            retrieval_service=failing_retrieval,  # type: ignore[arg-type]
            context_builder=AsyncMock(),  # type: ignore[arg-type]
            orchestrator=AsyncMock(),  # type: ignore[arg-type]
        )
        request = UserRequest(text="test", repository_id=repository_id)

        result = await pipeline.execute(request)

        assert result.success is False
        assert result.plan is not None
        assert result.response is None
        assert len(result.errors) > 0

    @pytest.mark.asyncio
    async def test_execute_returns_failed_result_on_context_error(
        self, repository_id: UUID
    ) -> None:
        resolver = _FakeRepositoryResolver(
            [RepositoryReference(id=repository_id, name="test-repo")]
        )
        query_engine = QueryEngineService(resolver)

        store = InMemorySearchStore(())
        embed_provider = AsyncMock()
        embed_provider.provider_name = "test"
        embed_provider.model_name = "test"
        embed_provider.embed.return_value = [
            EmbeddingVector(
                document_id="query:abc",
                vector=(0.1, 0.2, 0.3),
                dimensions=3,
                provider="test",
                model="test",
                created_at=datetime.now(UTC),
            )
        ]
        retrieval = RetrievalService(embed_provider, store, store, store)
        failing_context = AsyncMock()
        failing_context.build.side_effect = ValueError("Context build failed")
        pipeline = RepositoryQueryPipeline(
            query_engine=query_engine,
            retrieval_service=retrieval,
            context_builder=failing_context,  # type: ignore[arg-type]
            orchestrator=AsyncMock(),  # type: ignore[arg-type]
        )
        request = UserRequest(text="test", repository_id=repository_id)

        result = await pipeline.execute(request)

        assert result.success is False
        assert result.plan is not None
        assert result.retrieved_context is not None
        assert result.response is None
        assert len(result.errors) > 0

    @pytest.mark.asyncio
    async def test_execute_returns_failed_result_on_orchestrator_error(
        self, repository_id: UUID
    ) -> None:
        resolver = _FakeRepositoryResolver(
            [RepositoryReference(id=repository_id, name="test-repo")]
        )
        query_engine = QueryEngineService(resolver)

        store = InMemorySearchStore(())
        embed_provider = AsyncMock()
        embed_provider.provider_name = "test"
        embed_provider.model_name = "test"
        embed_provider.embed.return_value = [
            EmbeddingVector(
                document_id="query:abc",
                vector=(0.1, 0.2, 0.3),
                dimensions=3,
                provider="test",
                model="test",
                created_at=datetime.now(UTC),
            )
        ]
        retrieval = RetrievalService(embed_provider, store, store, store)
        context_builder = ContextBuilderService()
        failing_orchestrator = AsyncMock()
        failing_orchestrator.respond.side_effect = RuntimeError("Orchestrator failed")
        pipeline = RepositoryQueryPipeline(
            query_engine=query_engine,
            retrieval_service=retrieval,
            context_builder=context_builder,
            orchestrator=failing_orchestrator,  # type: ignore[arg-type]
        )
        request = UserRequest(text="test", repository_id=repository_id)

        result = await pipeline.execute(request)

        assert result.success is False
        assert result.plan is not None
        assert result.retrieved_context is not None
        assert result.llm_context is not None
        assert result.response is None
        assert len(result.errors) > 0
