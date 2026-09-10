"""HTTP transport for legacy repository manifest ingestion.

Deprecated: this endpoint predates ``RepositoryIndexingPipeline``. It used to
run its own, independent clone+walk+manifest orchestration (formerly
``IngestionService``), duplicating what the pipeline does internally. It is
kept only for API-contract compatibility with existing callers and is now a
thin adapter over the same canonical pipeline ``POST .../index`` uses -- see
docs/adr/0015-legacy-ingestion-endpoint-delegates-to-indexing-pipeline.md.

Calling this endpoint now runs the *full* pipeline (parse, chunk, embed,
index), not just a manifest walk -- there is no partial invocation of the
pipeline available. The response still reports only the manifest, to match
this endpoint's original contract; if the manifest was produced (workspace
walk succeeded) but a later pipeline step failed, this still returns 200,
since the thing this endpoint promises -- a manifest -- was in fact
produced. New integrations should call ``POST .../index`` directly and read
its richer ``IndexingResponse``.
"""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.api.v1.dependencies import AuthorizedRepositoryDependency, IndexingPipelineDependency
from app.modules.ingestion.schemas import RepositoryManifestResponse

router = APIRouter(prefix="/repositories", tags=["ingestion"])


@router.post(
    "/{repository_id}/ingest",
    response_model=RepositoryManifestResponse,
    deprecated=True,
)
async def ingest_repository(
    repository_id: UUID,
    pipeline: IndexingPipelineDependency,
    _authorized: AuthorizedRepositoryDependency,
) -> RepositoryManifestResponse:
    """Run the canonical indexing pipeline; respond with its manifest only."""
    result = await pipeline.execute(repository_id)
    if result.manifest is None:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"repository_id": str(repository_id), "errors": list(result.errors)},
        )
    return RepositoryManifestResponse.from_manifest(result.manifest)
