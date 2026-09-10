"""Integration tests for the repository indexing pipeline endpoint.

These tests verify that the transport layer correctly delegates to the
pipeline and returns appropriate HTTP responses. The pipeline itself is
mocked so that tests remain fast and deterministic.
"""

from dataclasses import dataclass
from unittest.mock import AsyncMock, sentinel
from uuid import UUID, uuid4

from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from app.api.v1.dependencies import get_authorized_repository, get_indexing_pipeline
from app.api.v1.routes.indexing import router
from app.application.pipelines.models import RepositoryIndexingResult


@dataclass
class _ResultBuilder:
    """Helper to construct deterministic pipeline results for tests."""

    repository_id: UUID

    def success(self) -> RepositoryIndexingResult:
        return RepositoryIndexingResult(
            repository_id=self.repository_id,
            success=True,
            manifest=None,
            parsed_repository=None,
            chunks=sentinel.CHUNKS,
            embedding_collection=sentinel.EMBEDDING,
            repository_index=sentinel.INDEX,
            elapsed_seconds=1.23,
            errors=(),
        )

    def failure(self, *errors: str) -> RepositoryIndexingResult:
        return RepositoryIndexingResult(
            repository_id=self.repository_id,
            success=False,
            manifest=None,
            parsed_repository=None,
            chunks=None,
            embedding_collection=None,
            repository_index=None,
            elapsed_seconds=0.5,
            errors=errors,
        )


def _app_with_mock_pipeline(pipeline: AsyncMock) -> FastAPI:
    """Build a test app with the pipeline mocked and ownership already authorized.

    Authentication/ownership are exercised in their own dedicated tests
    (test_repository_service.py, test_auth.py); these tests are about
    transport-layer delegation to the pipeline.
    """
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_indexing_pipeline] = lambda: pipeline
    app.dependency_overrides[get_authorized_repository] = lambda: None
    return app


class TestIndexRepositoryEndpoint:
    """POST /repositories/{repository_id}/index"""

    def test_returns_200_on_successful_indexing(self) -> None:
        repository_id = uuid4()
        builder = _ResultBuilder(repository_id)
        pipeline = AsyncMock(spec=["execute"])
        pipeline.execute = AsyncMock(return_value=builder.success())

        client = TestClient(_app_with_mock_pipeline(pipeline))
        response = client.post(f"/repositories/{repository_id}/index")

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["repository_id"] == str(repository_id)
        assert body["success"] is True
        assert body["elapsed_seconds"] == 1.23
        assert body["errors"] == []
        pipeline.execute.assert_awaited_once_with(repository_id)

    def test_returns_500_on_pipeline_failure(self) -> None:
        repository_id = uuid4()
        builder = _ResultBuilder(repository_id)
        pipeline = AsyncMock(spec=["execute"])
        pipeline.execute = AsyncMock(return_value=builder.failure("Clone failed: access denied"))

        client = TestClient(_app_with_mock_pipeline(pipeline))
        response = client.post(f"/repositories/{repository_id}/index")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        body = response.json()
        detail = body["detail"]
        assert detail["repository_id"] == str(repository_id)
        assert detail["success"] is False
        assert any("Clone failed" in e for e in detail["errors"])
        pipeline.execute.assert_awaited_once_with(repository_id)

    def test_reports_chunks_and_indexing_flags(self) -> None:
        repository_id = uuid4()
        pipeline = AsyncMock(spec=["execute"])
        pipeline.execute = AsyncMock(
            return_value=RepositoryIndexingResult(
                repository_id=repository_id,
                success=True,
                manifest=None,
                parsed_repository=None,
                chunks=sentinel.CHUNKS,
                embedding_collection=sentinel.EMBEDDING,
                repository_index=sentinel.INDEX,
                elapsed_seconds=2.5,
                errors=(),
            )
        )

        client = TestClient(_app_with_mock_pipeline(pipeline))
        response = client.post(f"/repositories/{repository_id}/index")

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["chunks_created"] is True
        assert body["indexed"] is True

    def test_endpoint_is_registered(self) -> None:
        """Verify the route exists and accepts repository_id parameter."""
        pipeline = AsyncMock(spec=["execute"])
        pipeline.execute = AsyncMock(return_value=_ResultBuilder(uuid4()).success())

        client = TestClient(_app_with_mock_pipeline(pipeline))
        response = client.post("/repositories/00000000-0000-0000-0000-000000000000/index")

        assert response.status_code == status.HTTP_200_OK
        pipeline.execute.assert_awaited_once()
