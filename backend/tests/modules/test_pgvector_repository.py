"""Integration tests for the PostgreSQL + pgvector-backed vector search adapter.

These prove pgvector itself works — database-side similarity ranking, top-K,
metadata filtering, repository isolation, and hybrid/RRF composition with the
existing keyword store — which a mock cannot demonstrate. They require a real
PostgreSQL instance with the pgvector extension available, pointed to via the
TEST_DATABASE_URL environment variable, e.g.:

    postgresql+psycopg://postgres:postgres@localhost:5433/repomind_test

and are skipped automatically when that variable is not set.
"""

import os
from collections.abc import AsyncGenerator
from datetime import UTC, datetime

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.config.settings import Settings, get_settings
from app.modules.embedding.models import EmbeddingVector, IndexDocument
from app.modules.indexing.db_models import IndexEntryModel
from app.modules.repository.enums import RepositoryProvider
from app.modules.repository.models import Repository
from app.modules.retrieval.db_repository import DbSearchStore
from app.modules.retrieval.models import SearchQuery
from app.modules.retrieval.pgvector_repository import PgVectorSearchStore
from app.modules.retrieval.service import RetrievalService
from app.shared.database.base import Base
from app.shared.database.session import build_async_engine
from app.shared.identifiers.uuid import new_uuid

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    not TEST_DATABASE_URL,
    reason="TEST_DATABASE_URL is not set; these tests require a real PostgreSQL+pgvector instance.",
)


def _vector(dominant_index: int, dimensions: int) -> tuple[float, ...]:
    """A unit vector with a 1.0 at one position so cosine distance is easy to reason about."""
    values = [0.0] * dimensions
    values[dominant_index % dimensions] = 1.0
    return tuple(values)


@pytest.fixture
async def engine() -> AsyncGenerator[AsyncEngine]:
    """Create the schema once per test if missing; never drop it.

    Each test scopes its own rows by a fresh repository_id, so sharing
    tables across tests in this throwaway database is safe. Dropping and
    recreating tables per test served no purpose here and only created an
    ACCESS EXCLUSIVE DROP TABLE that could contend with any earlier test's
    connection still releasing its read lock -- avoiding that entirely is
    simpler than chasing that race. The container itself is torn down after
    the run, so there is nothing left to clean up at the schema level.
    """
    async_engine = build_async_engine(Settings(database_url=TEST_DATABASE_URL))
    async with async_engine.begin() as connection:
        await connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await connection.run_sync(Base.metadata.create_all)
    yield async_engine
    await async_engine.dispose()


@pytest.fixture
def session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)


@pytest.fixture
async def session(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession]:
    async with session_factory() as db_session:
        yield db_session


async def _seed(
    session: AsyncSession,
    repository_id,
    entries: list[tuple[str, tuple[float, ...], str, dict]],
) -> None:
    # index_entries.repository_id carries a real FK to repositories.id (see
    # migration 0002_create_index_entries), so a row must exist here too --
    # create_all-based unit tests never exercised this constraint since the
    # ORM model itself declares no ForeignKey() (it's DB-only, added by raw
    # DDL in the migration), so the unit-of-work flush order can't infer the
    # dependency on its own; flushing it first makes the ordering explicit.
    session.add(
        Repository(
            id=repository_id,
            name=f"repo-{repository_id}",
            url=f"https://example.com/{repository_id}",
            provider=RepositoryProvider.GITHUB,
            default_branch="main",
        )
    )
    await session.flush()
    for document_id, vector, entry_text, metadata in entries:
        session.add(
            IndexEntryModel(
                document_id=document_id,
                repository_id=repository_id,
                embedding=list(vector),
                text=entry_text,
                entry_metadata=metadata,
                content_hash=document_id,
                provider="test",
                model="test-model",
            )
        )
    await session.commit()


@pytest.mark.asyncio
async def test_pgvector_search_orders_by_similarity(session: AsyncSession) -> None:
    dims = get_settings().embedding_dimensions
    repository_id = new_uuid()
    await _seed(
        session,
        repository_id,
        [
            ("closest", _vector(0, dims), "closest match", {"language": "python"}),
            ("farther", _vector(1, dims), "farther match", {"language": "python"}),
        ],
    )

    store = PgVectorSearchStore(session)
    results = await store.search(
        _vector(0, dims), repository_id=repository_id, filters={}, limit=10
    )

    assert [result.chunk_id for result in results] == ["closest", "farther"]
    assert results[0].score > results[1].score


@pytest.mark.asyncio
async def test_pgvector_search_respects_top_k(session: AsyncSession) -> None:
    dims = get_settings().embedding_dimensions
    repository_id = new_uuid()
    await _seed(
        session,
        repository_id,
        [(f"doc-{i}", _vector(i, dims), f"document {i}", {}) for i in range(5)],
    )

    store = PgVectorSearchStore(session)
    results = await store.search(_vector(0, dims), repository_id=repository_id, filters={}, limit=2)

    assert len(results) == 2


@pytest.mark.asyncio
async def test_pgvector_search_applies_metadata_filters(session: AsyncSession) -> None:
    dims = get_settings().embedding_dimensions
    repository_id = new_uuid()
    await _seed(
        session,
        repository_id,
        [
            ("py", _vector(0, dims), "python doc", {"language": "python"}),
            ("ts", _vector(0, dims), "typescript doc", {"language": "typescript"}),
        ],
    )

    store = PgVectorSearchStore(session)
    results = await store.search(
        _vector(0, dims),
        repository_id=repository_id,
        filters={"language": "typescript"},
        limit=10,
    )

    assert [result.chunk_id for result in results] == ["ts"]


@pytest.mark.asyncio
async def test_pgvector_search_isolates_by_repository(session: AsyncSession) -> None:
    dims = get_settings().embedding_dimensions
    repo_a, repo_b = new_uuid(), new_uuid()
    await _seed(session, repo_a, [("a-doc", _vector(0, dims), "doc a", {})])
    await _seed(session, repo_b, [("b-doc", _vector(0, dims), "doc b", {})])

    store = PgVectorSearchStore(session)
    results = await store.search(_vector(0, dims), repository_id=repo_a, filters={}, limit=10)

    assert [result.chunk_id for result in results] == ["a-doc"]


@pytest.mark.asyncio
async def test_pgvector_search_returns_empty_for_no_matches(session: AsyncSession) -> None:
    dims = get_settings().embedding_dimensions
    store = PgVectorSearchStore(session)

    results = await store.search(_vector(0, dims), repository_id=new_uuid(), filters={}, limit=10)

    assert list(results) == []


class _StaticQueryProvider:
    """Fake embedding provider that always returns a fixed query vector."""

    provider_name = "test"
    model_name = "test-model"

    def __init__(self, vector: tuple[float, ...]) -> None:
        self._vector = vector

    async def embed(self, documents: list[IndexDocument]) -> list[EmbeddingVector]:
        return [
            EmbeddingVector(
                document_id=document.id,
                vector=self._vector,
                dimensions=len(self._vector),
                provider=self.provider_name,
                model=self.model_name,
                created_at=datetime.now(UTC),
            )
            for document in documents
        ]


@pytest.mark.asyncio
async def test_pgvector_participates_in_hybrid_rrf_retrieval(
    session: AsyncSession, session_factory: async_sessionmaker[AsyncSession]
) -> None:
    """Vector hits from pgvector and keyword hits from DbSearchStore fuse via RRF.

    RetrievalService runs both ports concurrently via asyncio.gather, and
    AsyncSession is not safe for concurrent use from two coroutines, so this
    uses two independent sessions -- exactly as app.api.v1.dependencies does.
    """
    dims = get_settings().embedding_dimensions
    repository_id = new_uuid()
    await _seed(
        session,
        repository_id,
        [
            ("vector-only", _vector(0, dims), "unrelated text about caching", {}),
            ("both", _vector(1, dims), "authentication token handling", {}),
            ("keyword-only", _vector(2, dims), "authentication middleware setup", {}),
        ],
    )

    vector_store = PgVectorSearchStore(session)
    async with session_factory() as keyword_session:
        keyword_store = DbSearchStore(keyword_session)
        service = RetrievalService(
            _StaticQueryProvider(_vector(1, dims)),
            vector_store,
            keyword_store,
            keyword_store,
        )

        context = await service.retrieve(SearchQuery("authentication", repository_id))

    chunk_ids = {result.chunk_id for result in context.results}
    assert "both" in chunk_ids
    assert "keyword-only" in chunk_ids
    assert context.statistics.vector_hits >= 1
    assert context.statistics.keyword_hits >= 1
