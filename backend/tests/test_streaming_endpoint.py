"""Integration tests for the streaming query endpoint.

These tests verify that the transport layer correctly streams
Server-Sent Events by delegating to ``RepositoryQueryPipeline.stream()``.
The pipeline itself is mocked so that tests remain fast and deterministic.
"""

import json
from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from app.api.v1.dependencies import get_authorized_repository, get_query_pipeline
from app.api.v1.routes.query import router
from app.modules.orchestrator.models import (
    Citation,
    GeneratedResponse,
    StreamEvent,
    StreamEventType,
)


def _make_response(
    text: str = "The login function is defined in src/auth.py.",
    citations: tuple[Citation, ...] = (),
) -> GeneratedResponse:
    return GeneratedResponse(
        text=text,
        citations=citations,
        reasoning_metadata={"response_intent": "ANSWER"},
    )


def _app_with_mock_pipeline(pipeline: Any) -> FastAPI:
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


class TestQueryStreamEndpoint:
    """POST /repositories/{repository_id}/query/stream"""

    def test_stream_returns_200_with_sse_content_type(self) -> None:
        repository_id = uuid4()
        pipeline = AsyncMock(spec=["stream"])

        async def _stream(_request: Any) -> Any:
            yield StreamEvent(StreamEventType.START)
            yield StreamEvent(StreamEventType.TEXT, text="Hello ")
            yield StreamEvent(StreamEventType.END, response=_make_response())

        pipeline.stream = _stream

        client = TestClient(_app_with_mock_pipeline(pipeline))
        response = client.post(
            f"/repositories/{repository_id}/query/stream",
            json={"text": "find the login function"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert "text/event-stream" in response.headers["content-type"]

    def test_stream_emits_start_text_end_events(self) -> None:
        repository_id = uuid4()
        pipeline = AsyncMock(spec=["stream"])

        async def _stream(_request: Any) -> Any:
            yield StreamEvent(StreamEventType.START)
            yield StreamEvent(StreamEventType.TEXT, text="Hello ")
            yield StreamEvent(StreamEventType.TEXT, text="world")
            yield StreamEvent(StreamEventType.END, response=_make_response())

        pipeline.stream = _stream

        client = TestClient(_app_with_mock_pipeline(pipeline))
        response = client.post(
            f"/repositories/{repository_id}/query/stream",
            json={"text": "test"},
        )

        events = self._parse_sse(response.text)
        assert len(events) == 4
        assert events[0]["type"] == "START"
        assert events[1] == {"type": "TEXT", "token": "Hello "}
        assert events[2] == {"type": "TEXT", "token": "world"}
        assert events[3]["type"] == "END"

    def test_stream_includes_citation_count_in_end_event(self) -> None:
        repository_id = uuid4()
        citations = (
            Citation(
                chunk_id="c1",
                file_path="f1.py",
                qualified_symbol_name=None,
                line_start=None,
                line_end=None,
            ),
            Citation(
                chunk_id="c2",
                file_path="f2.py",
                qualified_symbol_name=None,
                line_start=None,
                line_end=None,
            ),
        )
        pipeline = AsyncMock(spec=["stream"])

        async def _stream(_request: Any) -> Any:
            yield StreamEvent(StreamEventType.START)
            yield StreamEvent(StreamEventType.TEXT, text="result")
            yield StreamEvent(StreamEventType.END, response=_make_response(citations=citations))

        pipeline.stream = _stream

        client = TestClient(_app_with_mock_pipeline(pipeline))
        response = client.post(
            f"/repositories/{repository_id}/query/stream",
            json={"text": "test"},
        )

        events = self._parse_sse(response.text)
        end_event = events[-1]
        assert len(end_event["sources"]) == 2
        assert end_event["sources"][0]["filePath"] == "f1.py"

    def test_stream_handles_pipeline_error(self) -> None:
        """When pipeline.stream() raises, the endpoint yields an ERROR event."""
        repository_id = uuid4()
        pipeline = AsyncMock(spec=["stream"])

        async def _raise_on_stream(_request: Any) -> Any:
            if False:
                yield  # make this an async generator
            raise RuntimeError("Setup failed")

        pipeline.stream = _raise_on_stream

        client = TestClient(_app_with_mock_pipeline(pipeline))
        response = client.post(
            f"/repositories/{repository_id}/query/stream",
            json={"text": "test"},
        )

        assert response.status_code == status.HTTP_200_OK
        events = self._parse_sse(response.text)
        assert len(events) == 1
        assert events[0]["type"] == "ERROR"

    def test_stream_passes_optional_preferences(self) -> None:
        repository_id = uuid4()
        captured_requests: list[Any] = []

        async def _capture_and_stream(_request: Any) -> Any:
            captured_requests.append(_request)
            yield StreamEvent(StreamEventType.START)
            yield StreamEvent(StreamEventType.END, response=_make_response())

        pipeline = AsyncMock(spec=["stream"])
        pipeline.stream = _capture_and_stream

        client = TestClient(_app_with_mock_pipeline(pipeline))
        response = client.post(
            f"/repositories/{repository_id}/query/stream",
            json={"text": "test", "preferences": {"limit": 20}},
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(captured_requests) == 1
        assert captured_requests[0].preferences == {"limit": 20}
        assert captured_requests[0].repository_id == repository_id

    @staticmethod
    def _parse_sse(text: str) -> list[dict[str, Any]]:
        """Parse SSE data frames from raw response text."""
        events: list[dict[str, Any]] = []
        for line in text.strip().split("\n"):
            if line.startswith("data: "):
                events.append(json.loads(line[6:]))
        return events
