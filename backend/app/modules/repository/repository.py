"""Repository-specific persistence queries."""

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.repository.models import Repository
from app.shared.database.exceptions import PersistenceError
from app.shared.database.repository import BaseRepository


class RepositoryRepository(BaseRepository[Repository]):
    """Persistence adapter for registered repositories and their domain queries."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Repository)

    async def get_by_url(self, url: str) -> Repository | None:
        """Return the repository registered at an exact canonical URL, if present."""
        try:
            statement = select(Repository).where(Repository.url == url)
            repository = await self._session.scalar(statement)
            self._logger.debug("repository_fetched_by_url", found=repository is not None)
            return repository
        except SQLAlchemyError as exc:
            self._logger.error("database_operation_failed", operation="get_by_url", exc_info=True)
            raise PersistenceError("Could not fetch repository by URL.") from exc

    async def exists_by_url(self, url: str) -> bool:
        """Return whether an exact canonical URL is already registered."""
        return await self.get_by_url(url) is not None
