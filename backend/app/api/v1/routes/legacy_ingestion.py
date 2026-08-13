"""HTTP transport for legacy repository manifest ingestion (moved from domain module)."""

from uuid import UUID

from fastapi import APIRouter

from app.api.v1.dependencies import IngestionAppServiceDependency
from app.application.exceptions import ApplicationError
from app.application.http_exceptions import to_http_exception
from app.modules.ingestion.schemas import RepositoryManifestResponse

router = APIRouter(prefix="/repositories", tags=["ingestion"])


@router.post("/{repository_id}/ingest", response_model=RepositoryManifestResponse)
async def ingest_repository(
    repository_id: UUID,
    service: IngestionAppServiceDependency,
) -> RepositoryManifestResponse:
    """Generate an ephemeral manifest from a clean, shallow-cloned workspace."""
    try:
        manifest = await service.ingest(repository_id)
    except ApplicationError as exc:
        raise to_http_exception(exc, fallback_message="Ingestion failed.") from exc
    return RepositoryManifestResponse.from_manifest(manifest)
