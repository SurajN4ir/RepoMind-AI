"""HTTP-level authentication and cross-user authorization tests.

Exercises the real FastAPI app (real routing, real dependency wiring, real
ownership checks in RepositoryService) against a real SQLite database.
Only genuinely external concerns are faked: the Clerk JWKS network call
(get_current_user is overridden to return a deterministic identity instead of
verifying a real bearer token -- that verification is covered on its own in
test_auth.py) and the indexing/query pipelines (mocked, so these tests don't
require a real git remote, Ollama, or LLM -- they prove the authorization
gate runs before the pipeline, not that the pipeline itself works).
"""

from collections.abc import AsyncGenerator
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.api.v1.dependencies import (
    get_current_user,
    get_indexing_pipeline,
    get_query_pipeline,
    get_token_verifier,
)
from app.application.services.repository import RepositoryApplicationService
from app.config.settings import Settings
from app.main import create_app
from app.modules.auth.models import AuthenticatedUser
from app.modules.auth.verifier import ClerkTokenVerifier
from app.modules.repository.enums import RepositoryProvider
from app.modules.repository.repository import RepositoryRepository
from app.modules.repository.schemas import CreateRepositoryRequest
from app.modules.repository.service import RepositoryService
from app.shared.database.base import Base
from app.shared.database.session import build_async_engine, get_db_session, get_secondary_db_session

USER_A = "user_a"
USER_B = "user_b"

_TEST_PRIVATE_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)


class _FakeSigningKey:
    def __init__(self, key: object) -> None:
        self.key = key


class _FakeKeyResolver:
    """Stands in for a real JWKS fetch: always resolves to our test public key."""

    def get_signing_key_from_jwt(self, token: str) -> _FakeSigningKey:
        return _FakeSigningKey(_TEST_PRIVATE_KEY.public_key())


@pytest.fixture
async def engine(tmp_path: Path) -> AsyncGenerator[AsyncEngine]:
    database_path = tmp_path / "authz.db"
    async_engine = build_async_engine(Settings(database_url=f"sqlite+aiosqlite:///{database_path}"))
    async with async_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield async_engine
    await async_engine.dispose()


@pytest.fixture
def session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)


@pytest.fixture
def indexing_pipeline() -> AsyncMock:
    return AsyncMock(spec=["execute"])


@pytest.fixture
def query_pipeline() -> AsyncMock:
    return AsyncMock(spec=["execute", "stream"])


@pytest.fixture
def app(
    session_factory: async_sessionmaker[AsyncSession],
    indexing_pipeline: AsyncMock,
    query_pipeline: AsyncMock,
) -> FastAPI:
    async def fake_session() -> AsyncGenerator[AsyncSession]:
        async with session_factory() as session:
            yield session

    application = create_app()
    application.dependency_overrides[get_db_session] = fake_session
    application.dependency_overrides[get_secondary_db_session] = fake_session
    # Phase 4: legacy /ingest now delegates to the same canonical
    # get_indexing_pipeline as /index -- one override covers both routes.
    application.dependency_overrides[get_indexing_pipeline] = lambda: indexing_pipeline
    application.dependency_overrides[get_query_pipeline] = lambda: query_pipeline
    # Real get_current_user, real ClerkTokenVerifier, real jwt.decode -- only
    # the JWKS network fetch is faked, so "invalid token" tests exercise real
    # signature/claim verification without needing a reachable Clerk instance.
    application.dependency_overrides[get_token_verifier] = lambda: ClerkTokenVerifier(
        "https://example.invalid/.well-known/jwks.json", key_resolver=_FakeKeyResolver()
    )
    return application


def _login_as(app: FastAPI, user_id: str) -> None:
    app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(user_id=user_id)


def _logout(app: FastAPI) -> None:
    app.dependency_overrides.pop(get_current_user, None)


async def _register_repository(
    session_factory: async_sessionmaker[AsyncSession], owner_id: str, name: str = "repo-a"
) -> str:
    async with session_factory() as session:
        service = RepositoryService(session, RepositoryRepository(session))
        repository = await service.register(
            CreateRepositoryRequest(
                name=name,
                url=f"https://github.com/example/{name}",
                provider=RepositoryProvider.GITHUB,
                default_branch="main",
            ),
            owner_id,
        )
        return str(repository.id)


class TestAuthenticationRequired:
    """Missing/invalid credentials must be rejected before any business logic runs."""

    def test_missing_authorization_header_returns_401(self, app: FastAPI) -> None:
        client = TestClient(app)

        response = client.get("/api/repositories")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_malformed_authorization_header_returns_401(self, app: FastAPI) -> None:
        client = TestClient(app)

        response = client.get(
            "/api/repositories", headers={"Authorization": "NotBearer something"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_invalid_token_returns_401(self, app: FastAPI) -> None:
        """Exercises the real verifier (no get_current_user override): an
        unparseable/unverifiable token must be rejected, not just a missing one."""
        client = TestClient(app)

        response = client.get(
            "/api/repositories", headers={"Authorization": "Bearer not-a-real-jwt"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestRepositoryOwnershipHttp:
    """POST/GET/PATCH/DELETE /repositories, exercised over real HTTP."""

    def test_create_repository_persists_authenticated_user_as_owner(
        self, app: FastAPI, session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        _login_as(app, USER_A)
        client = TestClient(app)

        response = client.post(
            "/api/repositories",
            json={
                "name": "owned-repo",
                "url": "https://github.com/example/owned-repo",
                "provider": "GITHUB",
                "default_branch": "main",
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        repository_id = response.json()["id"]

        async def _check() -> None:
            async with session_factory() as session:
                service = RepositoryApplicationService(
                    RepositoryService(session, RepositoryRepository(session))
                )
                repo = await service.get_trusted(__import__("uuid").UUID(repository_id))
                assert repo.owner_id == USER_A

        import asyncio

        asyncio.run(_check())

    def test_list_only_returns_callers_own_repositories(
        self, app: FastAPI, session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        import asyncio

        asyncio.run(_register_repository(session_factory, USER_A, "a-repo"))
        asyncio.run(_register_repository(session_factory, USER_B, "b-repo"))
        _login_as(app, USER_A)
        client = TestClient(app)

        response = client.get("/api/repositories")

        assert response.status_code == status.HTTP_200_OK
        names = [item["name"] for item in response.json()["items"]]
        assert names == ["a-repo"]

    def test_owner_can_get_their_own_repository(
        self, app: FastAPI, session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        import asyncio

        repository_id = asyncio.run(_register_repository(session_factory, USER_A))
        _login_as(app, USER_A)
        client = TestClient(app)

        response = client.get(f"/api/repositories/{repository_id}")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == repository_id

    def test_other_user_cannot_get_repository(
        self, app: FastAPI, session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        import asyncio

        repository_id = asyncio.run(_register_repository(session_factory, USER_A))
        _login_as(app, USER_B)
        client = TestClient(app)

        response = client.get(f"/api/repositories/{repository_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_other_user_cannot_update_repository(
        self, app: FastAPI, session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        import asyncio

        repository_id = asyncio.run(_register_repository(session_factory, USER_A))
        _login_as(app, USER_B)
        client = TestClient(app)

        response = client.patch(
            f"/api/repositories/{repository_id}", json={"description": "hijacked"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_other_user_cannot_delete_repository(
        self, app: FastAPI, session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        import asyncio

        repository_id = asyncio.run(_register_repository(session_factory, USER_A))
        _login_as(app, USER_B)
        client = TestClient(app)

        response = client.delete(f"/api/repositories/{repository_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_other_user_cannot_list_repository_files(
        self, app: FastAPI, session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        import asyncio

        repository_id = asyncio.run(_register_repository(session_factory, USER_A))
        _login_as(app, USER_B)
        client = TestClient(app)

        response = client.get(f"/api/repositories/{repository_id}/files")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_other_user_cannot_read_repository_activity(
        self, app: FastAPI, session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        import asyncio

        repository_id = asyncio.run(_register_repository(session_factory, USER_A))
        _login_as(app, USER_B)
        client = TestClient(app)

        response = client.get(f"/api/repositories/{repository_id}/activity")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestIndexingOwnershipHttp:
    """POST /repositories/{id}/index"""

    def test_owner_can_index_their_repository(
        self,
        app: FastAPI,
        session_factory: async_sessionmaker[AsyncSession],
        indexing_pipeline: AsyncMock,
    ) -> None:
        import asyncio

        repository_id = asyncio.run(_register_repository(session_factory, USER_A))
        indexing_pipeline.execute = AsyncMock(
            return_value=_indexing_success(repository_id)
        )
        _login_as(app, USER_A)
        client = TestClient(app)

        response = client.post(f"/api/repositories/{repository_id}/index")

        assert response.status_code == status.HTTP_200_OK
        indexing_pipeline.execute.assert_awaited_once()

    def test_other_user_cannot_index_repository(
        self,
        app: FastAPI,
        session_factory: async_sessionmaker[AsyncSession],
        indexing_pipeline: AsyncMock,
    ) -> None:
        import asyncio

        repository_id = asyncio.run(_register_repository(session_factory, USER_A))
        _login_as(app, USER_B)
        client = TestClient(app)

        response = client.post(f"/api/repositories/{repository_id}/index")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        indexing_pipeline.execute.assert_not_called()


class TestQueryOwnershipHttp:
    """POST /repositories/{id}/query and /query/stream"""

    def test_owner_can_query_their_repository(
        self,
        app: FastAPI,
        session_factory: async_sessionmaker[AsyncSession],
        query_pipeline: AsyncMock,
    ) -> None:
        import asyncio

        repository_id = asyncio.run(_register_repository(session_factory, USER_A))
        query_pipeline.execute = AsyncMock(return_value=_query_success(repository_id))
        _login_as(app, USER_A)
        client = TestClient(app)

        response = client.post(
            f"/api/repositories/{repository_id}/query", json={"text": "how does auth work?"}
        )

        assert response.status_code == status.HTTP_200_OK
        query_pipeline.execute.assert_awaited_once()

    def test_other_user_cannot_query_repository(
        self,
        app: FastAPI,
        session_factory: async_sessionmaker[AsyncSession],
        query_pipeline: AsyncMock,
    ) -> None:
        import asyncio

        repository_id = asyncio.run(_register_repository(session_factory, USER_A))
        _login_as(app, USER_B)
        client = TestClient(app)

        response = client.post(
            f"/api/repositories/{repository_id}/query", json={"text": "how does auth work?"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        query_pipeline.execute.assert_not_called()

    def test_other_user_cannot_stream_query_repository(
        self,
        app: FastAPI,
        session_factory: async_sessionmaker[AsyncSession],
        query_pipeline: AsyncMock,
    ) -> None:
        import asyncio

        repository_id = asyncio.run(_register_repository(session_factory, USER_A))
        _login_as(app, USER_B)
        client = TestClient(app)

        response = client.post(
            f"/api/repositories/{repository_id}/query/stream", json={"text": "test"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        query_pipeline.stream.assert_not_called()

    def test_owner_can_stream_query_their_repository(
        self,
        app: FastAPI,
        session_factory: async_sessionmaker[AsyncSession],
        query_pipeline: AsyncMock,
    ) -> None:
        import asyncio

        from app.modules.orchestrator.models import GeneratedResponse, StreamEvent, StreamEventType

        repository_id = asyncio.run(_register_repository(session_factory, USER_A))

        async def _stream(_request: object):
            yield StreamEvent(StreamEventType.START)
            yield StreamEvent(
                StreamEventType.END,
                response=GeneratedResponse(text="ok", citations=(), reasoning_metadata={}),
            )

        query_pipeline.stream = _stream
        _login_as(app, USER_A)
        client = TestClient(app)

        response = client.post(
            f"/api/repositories/{repository_id}/query/stream", json={"text": "test"}
        )

        assert response.status_code == status.HTTP_200_OK
        assert "text/event-stream" in response.headers["content-type"]


class TestSearchOwnershipHttp:
    """GET /search?repository_id=..."""

    def test_other_user_search_scoped_to_repository_returns_empty(
        self, app: FastAPI, session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        import asyncio

        repository_id = asyncio.run(_register_repository(session_factory, USER_A))
        _login_as(app, USER_B)
        client = TestClient(app)

        response = client.get("/api/search", params={"q": "auth", "repository_id": repository_id})

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_search_requires_authentication(self, app: FastAPI) -> None:
        client = TestClient(app)

        response = client.get("/api/search", params={"q": "auth"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestLegacyIngestionOwnershipHttp:
    """POST /repositories/{id}/ingest -- Phase 4: a thin adapter over the same
    canonical pipeline /index uses, not a second implementation."""

    def test_owner_can_trigger_legacy_ingestion(
        self,
        app: FastAPI,
        session_factory: async_sessionmaker[AsyncSession],
        indexing_pipeline: AsyncMock,
    ) -> None:
        import asyncio

        repository_id = asyncio.run(_register_repository(session_factory, USER_A))
        indexing_pipeline.execute = AsyncMock(
            return_value=_indexing_success_with_manifest(repository_id)
        )
        _login_as(app, USER_A)
        client = TestClient(app)

        response = client.post(f"/api/repositories/{repository_id}/ingest")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["repository_id"] == repository_id
        indexing_pipeline.execute.assert_awaited_once()

    def test_other_user_cannot_trigger_legacy_ingestion(
        self,
        app: FastAPI,
        session_factory: async_sessionmaker[AsyncSession],
        indexing_pipeline: AsyncMock,
    ) -> None:
        import asyncio

        repository_id = asyncio.run(_register_repository(session_factory, USER_A))
        _login_as(app, USER_B)
        client = TestClient(app)

        response = client.post(f"/api/repositories/{repository_id}/ingest")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        indexing_pipeline.execute.assert_not_called()

    def test_legacy_ingest_and_canonical_index_invoke_the_same_pipeline(
        self,
        app: FastAPI,
        session_factory: async_sessionmaker[AsyncSession],
        indexing_pipeline: AsyncMock,
    ) -> None:
        """Direct proof of delegation: both routes drive the one mock pipeline
        object (the dependency override is identical for both), so there is
        no way for /ingest to run different indexing logic than /index."""
        import asyncio

        repository_id = asyncio.run(_register_repository(session_factory, USER_A))
        indexing_pipeline.execute = AsyncMock(
            return_value=_indexing_success_with_manifest(repository_id)
        )
        _login_as(app, USER_A)
        client = TestClient(app)

        ingest_response = client.post(f"/api/repositories/{repository_id}/ingest")
        index_response = client.post(f"/api/repositories/{repository_id}/index")

        assert ingest_response.status_code == status.HTTP_200_OK
        assert index_response.status_code == status.HTTP_200_OK
        assert indexing_pipeline.execute.await_count == 2
        for call in indexing_pipeline.execute.await_args_list:
            assert call.args[0] == __import__("uuid").UUID(repository_id)

    def test_legacy_ingest_returns_502_when_manifest_step_never_completed(
        self,
        app: FastAPI,
        session_factory: async_sessionmaker[AsyncSession],
        indexing_pipeline: AsyncMock,
    ) -> None:
        """If the pipeline fails before producing a manifest (e.g. clone
        failure), /ingest has nothing to report and must not fake a 200."""
        import asyncio

        from app.application.pipelines.models import RepositoryIndexingResult

        repository_id = asyncio.run(_register_repository(session_factory, USER_A))
        indexing_pipeline.execute = AsyncMock(
            return_value=RepositoryIndexingResult(
                repository_id=__import__("uuid").UUID(repository_id),
                success=False,
                manifest=None,
                parsed_repository=None,
                chunks=None,
                embedding_collection=None,
                repository_index=None,
                elapsed_seconds=0.1,
                errors=("Failed to clone repository: not found",),
            )
        )
        _login_as(app, USER_A)
        client = TestClient(app)

        response = client.post(f"/api/repositories/{repository_id}/ingest")

        assert response.status_code == status.HTTP_502_BAD_GATEWAY


def _indexing_success(repository_id: str):
    from app.application.pipelines.models import RepositoryIndexingResult

    return RepositoryIndexingResult(
        repository_id=__import__("uuid").UUID(repository_id),
        success=True,
        manifest=None,
        parsed_repository=None,
        chunks=None,
        embedding_collection=None,
        repository_index=None,
        elapsed_seconds=0.1,
        errors=(),
    )


def _indexing_success_with_manifest(repository_id: str):
    from app.application.pipelines.models import RepositoryIndexingResult
    from app.modules.ingestion.manifest import RepositoryManifest

    repo_uuid = __import__("uuid").UUID(repository_id)
    return RepositoryIndexingResult(
        repository_id=repo_uuid,
        success=True,
        manifest=RepositoryManifest.create(repo_uuid, (), _empty_stats()),
        parsed_repository=None,
        chunks=None,
        embedding_collection=None,
        repository_index=None,
        elapsed_seconds=0.1,
        errors=(),
    )


def _query_success(repository_id: str):
    from app.application.pipelines.models import QueryResult
    from app.modules.query_engine.models import UserRequest

    return QueryResult(
        request=UserRequest(text="test", repository_id=__import__("uuid").UUID(repository_id)),
        success=True,
        response=None,
        plan=None,
        retrieved_context=None,
        llm_context=None,
        elapsed_seconds=0.1,
        errors=(),
    )


def _empty_stats():
    from app.modules.ingestion.manifest import RepositoryStats

    return RepositoryStats(
        total_files=0,
        total_bytes=0,
        skipped_files=0,
        skipped_binary_files=0,
        skipped_oversized_files=0,
    )
