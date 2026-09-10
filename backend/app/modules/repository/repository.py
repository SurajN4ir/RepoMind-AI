"""Repository-specific persistence queries."""

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.repository.models import Repository
from app.shared.database.exceptions import PersistenceError
from app.shared.database.pagination import Page, PaginationParams
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

    async def list_by_owner(self, owner_id: str, pagination: PaginationParams) -> Page[Repository]:
        """Return a stable, paginated page of repositories owned by one caller."""
        try:
            statement = (
                select(Repository)
                .where(Repository.owner_id == owner_id)
                .order_by(Repository.id)
                .offset(pagination.offset)
                .limit(pagination.page_size)
            )
            items = (await self._session.scalars(statement)).all()
            total = await self._session.scalar(
                select(func.count())
                .select_from(Repository)
                .where(Repository.owner_id == owner_id)
            )
            self._logger.debug("repositories_listed_by_owner", count=len(items), total=total or 0)
            return Page(
                items=items,
                total=total or 0,
                page=pagination.page,
                page_size=pagination.page_size,
            )
        except SQLAlchemyError as exc:
            self._logger.error(
                "database_operation_failed", operation="list_by_owner", exc_info=True
            )
            raise PersistenceError("Could not list repositories.") from exc
