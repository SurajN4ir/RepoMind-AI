"""Integration tests for the repository query pipeline endpoint.

These tests verify that the transport layer correctly delegates to the
pipeline and returns appropriate HTTP responses. The pipeline itself is
mocked so that tests remain fast and deterministic.
"""

from dataclasses import dataclass
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from app.api.v1.dependencies import get_authorized_repository, get_query_pipeline
from app.api.v1.routes.query import router
from app.application.pipelines.models import QueryResult
from app.modules.orchestrator.models import GeneratedResponse
from app.modules.query_engine.models import UserRequest
from app.modules.retrieval.models import Citation


@dataclass
class _ResultBuilder:
    """Helper to construct deterministic pipeline results for tests."""

    repository_id: UUID

    def success(self) -> QueryResult:
        return QueryResult(
            request=UserRequest(
                text="find the login function",
                repository_id=self.repository_id,
            ),
            success=True,
            response=GeneratedResponse(
                text="The login function is defined in src/auth.py.",
                citations=(
                    Citation(
                        chunk_id="c1",
                        file_path="src/auth.py",
                        qualified_symbol_name=None,
                        line_start=10,
                        line_end=20,
                    ),
                ),
                reasoning_metadata={"response_intent": "ANSWER"},
            ),
            plan=AsyncMock(),
            retrieved_context=AsyncMock(),
            llm_context=AsyncMock(),
            elapsed_seconds=2.34,
            errors=(),
        )

    def failure(self, *errors: str) -> QueryResult:
        return QueryResult(
            request=UserRequest(
                text="find the login function",
                repository_id=self.repository_id,
            ),
            success=False,
            response=None,
            plan=None,
            retrieved_context=None,
            llm_context=None,
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
    app.dependency_overrides[get_query_pipeline] = lambda: pipeline
    app.dependency_overrides[get_authorized_repository] = lambda: None
    return app


class TestQueryRepositoryEndpoint:
    """POST /repositories/{repository_id}/query"""

    def test_returns_200_on_successful_query(self) -> None:
        repository_id = uuid4()
        builder = _ResultBuilder(repository_id)
        pipeline = AsyncMock(spec=["execute"])
        pipeline.execute = AsyncMock(return_value=builder.success())

        client = TestClient(_app_with_mock_pipeline(pipeline))
        response = client.post(
            f"/repositories/{repository_id}/query",
            json={"text": "find the login function"},
        )

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["repository_id"] == str(repository_id)
        assert body["success"] is True
        assert body["response_text"] == "The login function is defined in src/auth.py."
        assert body["citation_count"] == 1
        assert body["elapsed_seconds"] == 2.34
        assert body["errors"] == []
        pipeline.execute.assert_awaited_once()

    def test_returns_500_on_pipeline_failure(self) -> None:
        repository_id = uuid4()
        builder = _ResultBuilder(repository_id)
        pipeline = AsyncMock(spec=["execute"])
        pipeline.execute = AsyncMock(return_value=builder.failure("Plan failed: ambiguous request"))

        client = TestClient(_app_with_mock_pipeline(pipeline))
        response = client.post(
            f"/repositories/{repository_id}/query",
            json={"text": "find the login function"},
        )

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        body = response.json()
        detail = body["detail"]
        assert detail["success"] is False
        assert any("Plan failed" in e for e in detail["errors"])
        pipeline.execute.assert_awaited_once()

    def test_reports_empty_response_and_citations_when_none(self) -> None:
        repository_id = uuid4()
        pipeline = AsyncMock(spec=["execute"])
        pipeline.execute = AsyncMock(
            return_value=QueryResult(
                request=UserRequest(
                    text="test",
                    repository_id=repository_id,
                ),
                success=True,
                response=None,
                plan=None,
                retrieved_context=None,
                llm_context=None,
                elapsed_seconds=1.0,
                errors=(),
            )
        )

        client = TestClient(_app_with_mock_pipeline(pipeline))
        response = client.post(
            f"/repositories/{repository_id}/query",
            json={"text": "test"},
        )

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["success"] is True
        assert body["response_text"] is None
        assert body["citation_count"] == 0

    def test_endpoint_is_registered(self) -> None:
        """Verify the route exists and accepts repository_id parameter."""
        pipeline = AsyncMock(spec=["execute"])
        pipeline.execute = AsyncMock(return_value=_ResultBuilder(uuid4()).success())

        client = TestClient(_app_with_mock_pipeline(pipeline))
        response = client.post(
            "/repositories/00000000-0000-0000-0000-000000000000/query",
            json={"text": "test"},
        )

        assert response.status_code == status.HTTP_200_OK
        pipeline.execute.assert_awaited_once()

    def test_accepts_optional_preferences(self) -> None:
        repository_id = uuid4()
        builder = _ResultBuilder(repository_id)
        pipeline = AsyncMock(spec=["execute"])
        pipeline.execute = AsyncMock(return_value=builder.success())

        client = TestClient(_app_with_mock_pipeline(pipeline))
        response = client.post(
            f"/repositories/{repository_id}/query",
            json={"text": "find the login function", "preferences": {"limit": 20}},
        )

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["success"] is True
        call_kwargs = pipeline.execute.call_args
        request = call_kwargs[0][0]
        assert request.preferences == {"limit": 20}
