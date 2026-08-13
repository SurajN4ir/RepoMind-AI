"""Application use cases for registered repository metadata."""

from collections.abc import Mapping
from datetime import datetime
from pathlib import PureWindowsPath
from urllib.parse import urlparse
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.repository.enums import RepositoryProvider, RepositoryStatus
from app.modules.repository.exceptions import (
    DuplicateRepositoryError,
    InvalidRepositoryMetadataError,
    InvalidRepositoryStatusTransitionError,
    InvalidRepositoryUrlError,
    RepositoryNotFoundError,
    RepositoryPersistenceError,
    UnsupportedRepositoryProviderError,
)
from app.modules.repository.models import Repository
from app.modules.repository.repository import RepositoryRepository
from app.modules.repository.schemas import CreateRepositoryRequest, UpdateRepositoryRequest
from app.shared.database.exceptions import IntegrityConstraintError, PersistenceError
from app.shared.database.pagination import Page, PaginationParams
from app.shared.database.transactions import transaction

_ALLOWED_STATUS_TRANSITIONS: Mapping[RepositoryStatus, frozenset[RepositoryStatus]] = {
    RepositoryStatus.NEW: frozenset({RepositoryStatus.REGISTERED, RepositoryStatus.ARCHIVED}),
    RepositoryStatus.REGISTERED: frozenset({RepositoryStatus.INDEXING, RepositoryStatus.ARCHIVED}),
    RepositoryStatus.INDEXING: frozenset(
        {RepositoryStatus.READY, RepositoryStatus.FAILED, RepositoryStatus.ARCHIVED}
    ),
    RepositoryStatus.READY: frozenset({RepositoryStatus.INDEXING, RepositoryStatus.ARCHIVED}),
    RepositoryStatus.FAILED: frozenset({RepositoryStatus.INDEXING, RepositoryStatus.ARCHIVED}),
    RepositoryStatus.ARCHIVED: frozenset(),
}


class RepositoryService:
    """Coordinate repository metadata use cases without performing ingestion work."""

    def __init__(self, session: AsyncSession, repository: RepositoryRepository) -> None:
        self._session = session
        self._repository = repository

    async def register(self, request: CreateRepositoryRequest) -> Repository:
        """Register a unique repository and mark it as registered."""
        self._validate_provider(request.provider)
        url = self._validate_url(request.url, request.provider)
        name = self._validate_required_text(request.name, "name")
        default_branch = self._validate_required_text(request.default_branch, "default_branch")
        try:
            async with transaction(self._session):
                if await self._repository.exists_by_url(url):
                    raise DuplicateRepositoryError(
                        "A repository with this URL is already registered."
                    )
                return await self._repository.add(
                    Repository(
                        name=name,
                        url=url,
                        provider=request.provider,
                        default_branch=default_branch,
                        description=self._normalize_optional_text(request.description),
                        language_summary=request.language_summary,
                        status=RepositoryStatus.REGISTERED,
                    )
                )
        except IntegrityConstraintError as exc:
            raise DuplicateRepositoryError(
                "A repository with this URL is already registered."
            ) from exc
        except PersistenceError as exc:
            raise RepositoryPersistenceError("Could not register repository.") from exc

    async def get(self, repository_id: UUID) -> Repository:
        """Fetch one registered repository or raise a feature-local not-found error."""
        try:
            async with transaction(self._session):
                repository = await self._repository.get(repository_id)
        except PersistenceError as exc:
            raise RepositoryPersistenceError("Could not fetch repository.") from exc
        if repository is None:
            raise RepositoryNotFoundError("Repository was not found.")
        return repository

    async def list(self, pagination: PaginationParams) -> Page[Repository]:
        """List registered repositories using shared pagination semantics."""
        try:
            async with transaction(self._session):
                return await self._repository.list(pagination)
        except PersistenceError as exc:
            raise RepositoryPersistenceError("Could not list repositories.") from exc

    async def update(self, repository_id: UUID, request: UpdateRepositoryRequest) -> Repository:
        """Update allowed metadata and lifecycle fields for a registered repository."""
        changes = request.model_dump(exclude_unset=True)
        try:
            async with transaction(self._session):
                repository = await self._get_or_raise(repository_id)
                provider = changes.get("provider", repository.provider)
                self._validate_provider(provider)
                url = self._validate_url(changes.get("url", repository.url), provider)
                if url != repository.url:
                    existing = await self._repository.get_by_url(url)
                    if existing is not None and existing.id != repository.id:
                        raise DuplicateRepositoryError(
                            "A repository with this URL is already registered."
                        )
                    repository.url = url

                if "status" in changes:
                    self._validate_status_transition(repository.status, changes["status"])
                    repository.status = changes["status"]

                for field in ("name", "default_branch"):
                    if field in changes:
                        setattr(
                            repository, field, self._validate_required_text(changes[field], field)
                        )
                if "description" in changes:
                    repository.description = self._normalize_optional_text(changes["description"])
                for field in ("language_summary", "last_indexed_at", "provider"):
                    if field in changes:
                        setattr(repository, field, changes[field])
                return await self._repository.update(repository)
        except IntegrityConstraintError as exc:
            raise DuplicateRepositoryError(
                "A repository with this URL is already registered."
            ) from exc
        except PersistenceError as exc:
            raise RepositoryPersistenceError("Could not update repository.") from exc

    async def update_status(
        self,
        repository_id: UUID,
        status: RepositoryStatus,
        *,
        last_indexed_at: datetime | None = None,
        total_files: int | None = None,
    ) -> Repository:
        """Update lifecycle status for use by this or future bounded contexts."""
        changes: dict[str, object] = {"status": status}
        if last_indexed_at is not None:
            changes["last_indexed_at"] = last_indexed_at
        if total_files is not None:
            changes["total_files"] = total_files
        return await self.update(repository_id, UpdateRepositoryRequest.model_validate(changes))

    async def delete(self, repository_id: UUID) -> None:
        """Delete a registered repository record without performing external cleanup."""
        try:
            async with transaction(self._session):
                repository = await self._get_or_raise(repository_id)
                await self._repository.delete(repository)
        except PersistenceError as exc:
            raise RepositoryPersistenceError("Could not delete repository.") from exc

    async def _get_or_raise(self, repository_id: UUID) -> Repository:
        repository = await self._repository.get(repository_id)
        if repository is None:
            raise RepositoryNotFoundError("Repository was not found.")
        return repository

    @staticmethod
    def _validate_provider(provider: RepositoryProvider) -> None:
        if not isinstance(provider, RepositoryProvider):
            raise UnsupportedRepositoryProviderError("Unsupported repository provider.")

    @staticmethod
    def _validate_url(url: str, provider: RepositoryProvider) -> str:
        if not isinstance(url, str):
            raise InvalidRepositoryUrlError("Repository URL must be a string.")
        normalized = url.strip()
        parsed = urlparse(normalized)
        if provider is RepositoryProvider.LOCAL:
            if (
                parsed.scheme == "file"
                or normalized.startswith(("/", "\\"))
                or PureWindowsPath(normalized).is_absolute()
            ):
                return normalized
            raise InvalidRepositoryUrlError(
                "Local repositories require a file URL or absolute path."
            )
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise InvalidRepositoryUrlError("Remote repositories require an HTTP(S) URL.")
        return normalized.rstrip("/")

    @staticmethod
    def _validate_status_transition(current: RepositoryStatus, requested: RepositoryStatus) -> None:
        if not isinstance(requested, RepositoryStatus):
            raise InvalidRepositoryMetadataError("status must be a valid repository status.")
        if requested is current:
            return
        if requested not in _ALLOWED_STATUS_TRANSITIONS[current]:
            raise InvalidRepositoryStatusTransitionError(
                f"Cannot transition repository from {current.value} to {requested.value}."
            )

    @staticmethod
    def _normalize_optional_text(value: str | None) -> str | None:
        return value.strip() if value is not None else None

    @staticmethod
    def _validate_required_text(value: str | None, field_name: str) -> str:
        if not isinstance(value, str):
            raise InvalidRepositoryMetadataError(f"{field_name} must be a string.")
        normalized = value.strip()
        if not normalized:
            raise InvalidRepositoryMetadataError(f"{field_name} must not be blank.")
        return normalized
