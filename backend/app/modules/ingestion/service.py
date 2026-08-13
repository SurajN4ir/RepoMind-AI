"""Repository workspace ingestion orchestration and lifecycle coordination."""

import asyncio
import shutil
import tempfile
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import UUID

import structlog

from app.modules.ingestion.exceptions import (
    IngestionError,
    RepositoryWorkspaceError,
    UnsupportedIngestionStatusError,
)
from app.modules.ingestion.git import GitClient
from app.modules.ingestion.manifest import RepositoryManifest
from app.modules.ingestion.walker import RepositoryWalker
from app.modules.repository.enums import RepositoryStatus
from app.modules.repository.service import RepositoryService

logger = structlog.get_logger(__name__)


class IngestionService:
    """Create an ephemeral workspace and return a clean repository manifest."""

    def __init__(
        self,
        repository_service: RepositoryService,
        git_client: GitClient,
        walker: RepositoryWalker,
    ) -> None:
        self._repository_service = repository_service
        self._git_client = git_client
        self._walker = walker

    async def ingest(self, repository_id: UUID) -> RepositoryManifest:
        """Shallow-clone, inventory, and clean up one repository workspace."""
        repository = await self._repository_service.get(repository_id)
        self._validate_start_status(repository.status)
        status_changed = False
        try:
            await self._repository_service.update_status(repository_id, RepositoryStatus.INDEXING)
            status_changed = True
            async with temporary_workspace() as workspace:
                checkout_path = workspace / "repository"
                await self._git_client.clone_shallow(
                    repository.url,
                    repository.default_branch,
                    checkout_path,
                )
                walk_result = await self._walker.walk(checkout_path)
                manifest = RepositoryManifest.create(
                    repository_id=repository_id,
                    files=walk_result.files,
                    stats=walk_result.stats,
                )
            await self._repository_service.update_status(
                repository_id,
                RepositoryStatus.READY,
                last_indexed_at=manifest.generated_at,
            )
            logger.info(
                "repository_manifest_created",
                repository_id=str(repository_id),
                total_files=manifest.stats.total_files,
            )
            return manifest
        except Exception as exc:
            if status_changed:
                await self._mark_failed(repository_id)
            if isinstance(exc, IngestionError):
                raise
            logger.error(
                "repository_ingestion_failed",
                repository_id=str(repository_id),
                exc_info=True,
            )
            raise IngestionError("Repository manifest ingestion failed.") from exc

    @staticmethod
    def _validate_start_status(status: RepositoryStatus) -> None:
        allowed_statuses = {
            RepositoryStatus.REGISTERED,
            RepositoryStatus.READY,
            RepositoryStatus.FAILED,
        }
        if status not in allowed_statuses:
            raise UnsupportedIngestionStatusError(
                f"Repository status {status.value} cannot begin ingestion."
            )

    async def _mark_failed(self, repository_id: UUID) -> None:
        try:
            await self._repository_service.update_status(repository_id, RepositoryStatus.FAILED)
        except Exception:
            logger.error(
                "repository_failure_status_update_failed",
                repository_id=str(repository_id),
                exc_info=True,
            )


@asynccontextmanager
async def temporary_workspace() -> AsyncGenerator[Path]:
    """Create and remove a unique temporary workspace even when ingestion fails."""
    try:
        workspace = Path(await asyncio.to_thread(tempfile.mkdtemp, prefix="repomind-ingestion-"))
    except OSError as exc:
        raise RepositoryWorkspaceError("Could not create repository workspace.") from exc
    logger.debug("repository_workspace_created", workspace=str(workspace))
    try:
        yield workspace
    finally:
        try:
            await asyncio.to_thread(shutil.rmtree, workspace)
            logger.debug("repository_workspace_cleaned", workspace=str(workspace))
        except OSError:
            logger.warning(
                "repository_workspace_cleanup_failed",
                workspace=str(workspace),
                exc_info=True,
            )
