"""Application-layer HTTP endpoint that delegates querying to the pipeline.

This route lives at the application layer (not in a domain module) because
the ``RepositoryQueryPipeline`` it invokes is an application construct that
composes multiple domain services.
"""

import json
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from starlette.responses import StreamingResponse

from app.api.v1.dependencies import QueryPipelineDependency
from app.api.v1.routes.schemas import QueryRequest, QueryResponse
from app.modules.orchestrator.models import StreamEvent, StreamEventType
from app.modules.query_engine.models import UserRequest

router = APIRouter(prefix="/repositories", tags=["query"])


@router.post(
    "/{repository_id}/query",
    response_model=QueryResponse,
)
async def query_repository(
    repository_id: UUID,
    body: QueryRequest,
    pipeline: QueryPipelineDependency,
) -> QueryResponse:
    """Plan, retrieve, build context, and respond to a user query.

    The entire workflow is delegated to ``RepositoryQueryPipeline``.
    This route contains no orchestration logic.
    """
    prefs = dict(body.preferences)
    if body.conversation_id is not None:
        prefs["conversation_id"] = str(body.conversation_id)
    user_request = UserRequest(
        text=body.text,
        repository_id=repository_id,
        preferences=prefs,
    )
    result = await pipeline.execute(user_request)
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=QueryResponse.from_result(result, repository_id).model_dump(mode="json"),
        )
    return QueryResponse.from_result(result, repository_id)


def _format_sse(event: StreamEvent) -> str:
    """Serialise a domain StreamEvent as a single SSE data frame."""
    data: dict[str, object] = {"type": event.type.value}
    if event.text:
        data["token"] = event.text
    if event.type is StreamEventType.END and event.response is not None:
        citations = [
            {
                "filePath": c.file_path,
                "lineStart": c.line_start or 0,
                "lineEnd": c.line_end or 0,
            }
            for c in event.response.citations
            if c.file_path
        ]
        data["sources"] = citations
    return f"data: {json.dumps(data)}\n\n"


def _format_error_sse(detail: str) -> str:
    """Serialise a pipeline error as an SSE data frame."""
    return f"data: {json.dumps({'type': 'ERROR', 'detail': detail})}\n\n"


@router.post(
    "/{repository_id}/query/stream",
    response_class=StreamingResponse,
)
async def query_repository_stream(
    repository_id: UUID,
    body: QueryRequest,
    pipeline: QueryPipelineDependency,
) -> StreamingResponse:
    """Plan, retrieve, build context, and stream a response token by token.

    Delegates query orchestration to ``RepositoryQueryPipeline.stream()``
    and serialises each ``StreamEvent`` as a Server-Sent Event.  This
    route contains no orchestration logic.
    """
    prefs = dict(body.preferences)
    if body.conversation_id is not None:
        prefs["conversation_id"] = str(body.conversation_id)
    user_request = UserRequest(
        text=body.text,
        repository_id=repository_id,
        preferences=prefs,
    )

    async def event_stream():
        try:
            async for event in pipeline.stream(user_request):
                yield _format_sse(event)
        except Exception:
            yield _format_error_sse("Query pipeline execution failed.")

    return StreamingResponse(
        content=event_stream(),
        media_type="text/event-stream",
    )
