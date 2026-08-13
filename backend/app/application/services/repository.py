"""Application boundary for repository lifecycle use cases."""

from datetime import datetime
from uuid import UUID

import structlog

from app.application.exceptions import (
    ConflictError,
    EntityNotFoundError,
    ExternalServiceError,
    UnhandledDomainError,
    ValidationError,
)
from app.modules.repository.enums import RepositoryStatus
from app.modules.repository.exceptions import (
    DuplicateRepositoryError,
    InvalidRepositoryMetadataError,
    InvalidRepositoryStatusTransitionError,
    InvalidRepositoryUrlError,
    RepositoryDomainError,
    RepositoryNotFoundError,
    RepositoryPersistenceError,
    UnsupportedRepositoryProviderError,
)
from app.modules.repository.models import Repository
from app.modules.repository.schemas import CreateRepositoryRequest, UpdateRepositoryRequest
from app.modules.repository.service import RepositoryService
from app.shared.database.pagination import Page, PaginationParams


class RepositoryApplicationService:
    """Coordinate repository lifecycle use cases at the application boundary.

    Delegates all business decisions to the domain service. Translates domain
    exceptions into stable application-layer exceptions for the transport layer.
    """

    def __init__(self, domain: RepositoryService) -> None:
        self._domain = domain
        self._logger = structlog.get_logger(__name__)

    async def register(self, request: CreateRepositoryRequest) -> Repository:
        """Register a repository."""
        try:
            repository = await self._domain.register(request)
            self._logger.info("repository_registered", repository_id=str(repository.id))
            return repository
        except RepositoryDomainError as exc:
            raise _map_repository_error(exc) from exc

    async def get(self, repository_id: UUID) -> Repository:
        """Fetch one repository by identifier."""
        try:
            return await self._domain.get(repository_id)
        except RepositoryDomainError as exc:
            raise _map_repository_error(exc) from exc

    async def list(self, pagination: PaginationParams) -> Page[Repository]:
        """List repositories with pagination."""
        try:
            return await self._domain.list(pagination)
        except RepositoryDomainError as exc:
            raise _map_repository_error(exc) from exc

    async def update(self, repository_id: UUID, request: UpdateRepositoryRequest) -> Repository:
        """Update mutable repository metadata or lifecycle status."""
        try:
            repository = await self._domain.update(repository_id, request)
            self._logger.info("repository_updated", repository_id=str(repository.id))
            return repository
        except RepositoryDomainError as exc:
            raise _map_repository_error(exc) from exc

    async def delete(self, repository_id: UUID) -> None:
        """Delete a repository record."""
        try:
            await self._domain.delete(repository_id)
            self._logger.info("repository_deleted", repository_id=str(repository_id))
        except RepositoryDomainError as exc:
            raise _map_repository_error(exc) from exc

    async def update_status(
        self,
        repository_id: UUID,
        status: RepositoryStatus,
        *,
        last_indexed_at: datetime | None = None,
        total_files: int | None = None,
    ) -> Repository:
        """Update lifecycle status (public for cross-module callers)."""
        try:
            repository = await self._domain.update_status(
                repository_id,
                status,
                last_indexed_at=last_indexed_at,
                total_files=total_files,
            )
            self._logger.info(
                "repository_status_updated",
                repository_id=str(repository_id),
                status=status.value,
            )
            return repository
        except RepositoryDomainError as exc:
            raise _map_repository_error(exc) from exc


def _map_repository_error(exc: RepositoryDomainError) -> Exception:
    """Map domain exceptions to application-layer exceptions."""
    if isinstance(exc, RepositoryNotFoundError):
        return EntityNotFoundError(str(exc))
    if isinstance(exc, (DuplicateRepositoryError, InvalidRepositoryStatusTransitionError)):
        return ConflictError(str(exc))
    validation_set = (
        InvalidRepositoryMetadataError,
        InvalidRepositoryUrlError,
        UnsupportedRepositoryProviderError,
    )
    if isinstance(exc, validation_set):
        return ValidationError(str(exc))
    if isinstance(exc, RepositoryPersistenceError):
        return ExternalServiceError(str(exc))
    return UnhandledDomainError(str(exc))
