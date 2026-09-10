"""Application-layer HTTP endpoint that delegates indexing to the pipeline.

This route lives at the application layer (not in a domain module) because
the ``RepositoryIndexingPipeline`` it invokes is an application construct
that composes multiple domain services.
"""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.api.v1.dependencies import AuthorizedRepositoryDependency, IndexingPipelineDependency
from app.api.v1.routes.schemas import IndexingResponse

router = APIRouter(prefix="/repositories", tags=["indexing"])


@router.post(
    "/{repository_id}/index",
    response_model=IndexingResponse,
)
async def index_repository(
    repository_id: UUID,
    pipeline: IndexingPipelineDependency,
    _authorized: AuthorizedRepositoryDependency,
) -> IndexingResponse:
    """Clone, walk, parse, chunk, embed, and index a registered repository.

    The entire workflow is delegated to ``RepositoryIndexingPipeline``.
    This route contains no orchestration logic.
    """
    result = await pipeline.execute(repository_id)
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=IndexingResponse.from_result(result).model_dump(mode="json"),
        )
    return IndexingResponse.from_result(result)
