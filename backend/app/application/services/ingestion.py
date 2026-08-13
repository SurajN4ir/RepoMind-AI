"""Application boundary for repository workspace ingestion."""

from uuid import UUID

import structlog

from app.application.exceptions import (
    ConflictError,
    EntityNotFoundError,
    ExternalServiceError,
    UnhandledDomainError,
)
from app.modules.ingestion.exceptions import (
    GitCloneError,
    IngestionError,
    RepositoryWorkspaceError,
    UnsupportedIngestionStatusError,
)
from app.modules.ingestion.manifest import RepositoryManifest
from app.modules.ingestion.service import IngestionService
from app.modules.repository.exceptions import RepositoryDomainError, RepositoryNotFoundError


class IngestionApplicationService:
    """Coordinate ingestion workflows at the application boundary.

    Delegates workspace creation, file filtering, and manifest generation to
    the domain service. Translates domain exceptions into application exceptions.
    """

    def __init__(self, domain: IngestionService) -> None:
        self._domain = domain
        self._logger = structlog.get_logger(__name__)

    async def ingest(self, repository_id: UUID) -> RepositoryManifest:
        """Shallow-clone, inventory, and return a repository manifest."""
        try:
            manifest = await self._domain.ingest(repository_id)
            self._logger.info(
                "ingestion_completed",
                repository_id=str(repository_id),
                total_files=manifest.stats.total_files,
            )
            return manifest
        except (RepositoryDomainError, IngestionError) as exc:
            raise _map_ingestion_error(exc) from exc


def _map_ingestion_error(exc: RepositoryDomainError | IngestionError) -> Exception:
    """Map ingestion and repository domain errors to application exceptions."""
    if isinstance(exc, RepositoryNotFoundError):
        return EntityNotFoundError(str(exc))
    if isinstance(exc, UnsupportedIngestionStatusError):
        return ConflictError(str(exc))
    if isinstance(exc, (GitCloneError, RepositoryWorkspaceError)):
        return ExternalServiceError(str(exc))
    if isinstance(exc, IngestionError):
        return ExternalServiceError(str(exc))
    if isinstance(exc, RepositoryDomainError):
        return UnhandledDomainError(str(exc))
    return UnhandledDomainError(str(exc))
