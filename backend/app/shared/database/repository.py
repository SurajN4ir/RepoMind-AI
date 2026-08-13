"""Generic async repository implementation for feature-owned models."""

from collections.abc import Sequence
from typing import Any, TypeVar
from uuid import UUID

import structlog
from sqlalchemy import Select, func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.database.base import Base
from app.shared.database.exceptions import (
    EntityNotFoundError,
    IntegrityConstraintError,
    PersistenceError,
)
from app.shared.database.pagination import Page, PaginationParams

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository[ModelT: Base]:
    """Common async CRUD mechanics for a single feature-owned SQLAlchemy model.

    Feature repositories should compose or subclass this class for storage concerns only;
    application decisions belong in their module's application layer.
    """

    def __init__(self, session: AsyncSession, model_type: type[ModelT]) -> None:
        self._session = session
        self._model_type = model_type
        self._logger = structlog.get_logger(__name__).bind(model=model_type.__name__)

    async def add(self, entity: ModelT) -> ModelT:
        """Attach an entity and flush it so generated database values are available."""
        try:
            self._session.add(entity)
            await self._session.flush()
            self._logger.debug("database_entity_added")
            return entity
        except IntegrityError as exc:
            self._logger.warning("database_integrity_error", exc_info=True)
            raise IntegrityConstraintError("A database integrity constraint was violated.") from exc
        except SQLAlchemyError as exc:
            self._logger.error("database_operation_failed", operation="add", exc_info=True)
            raise PersistenceError("Could not persist entity.") from exc

    async def get(self, entity_id: UUID) -> ModelT | None:
        """Return an entity by primary key, or ``None`` when absent."""
        try:
            entity = await self._session.get(self._model_type, entity_id)
            self._logger.debug("database_entity_fetched", found=entity is not None)
            return entity
        except SQLAlchemyError as exc:
            self._logger.error("database_operation_failed", operation="get", exc_info=True)
            raise PersistenceError("Could not fetch entity.") from exc

    async def get_or_raise(self, entity_id: UUID) -> ModelT:
        """Return an entity by primary key or raise a persistence-neutral exception."""
        entity = await self.get(entity_id)
        if entity is None:
            raise EntityNotFoundError(f"{self._model_type.__name__} was not found.")
        return entity

    async def update(self, entity: ModelT) -> ModelT:
        """Flush changes made to an attached entity and return the same instance."""
        try:
            await self._session.flush()
            self._logger.debug("database_entity_updated")
            return entity
        except IntegrityError as exc:
            self._logger.warning("database_integrity_error", exc_info=True)
            raise IntegrityConstraintError("A database integrity constraint was violated.") from exc
        except SQLAlchemyError as exc:
            self._logger.error("database_operation_failed", operation="update", exc_info=True)
            raise PersistenceError("Could not update entity.") from exc

    async def list(self, pagination: PaginationParams) -> Page[ModelT]:
        """Return a stable, primary-key ordered page of model instances."""
        try:
            identifier: Any = self._model_type.id
            statement: Select[tuple[ModelT]] = (
                select(self._model_type)
                .order_by(identifier)
                .offset(pagination.offset)
                .limit(pagination.page_size)
            )
            items: Sequence[ModelT] = (await self._session.scalars(statement)).all()
            total = await self._session.scalar(select(func.count()).select_from(self._model_type))
            self._logger.debug("database_entities_listed", count=len(items), total=total or 0)
            return Page(
                items=items,
                total=total or 0,
                page=pagination.page,
                page_size=pagination.page_size,
            )
        except SQLAlchemyError as exc:
            self._logger.error("database_operation_failed", operation="list", exc_info=True)
            raise PersistenceError("Could not list entities.") from exc

    async def delete(self, entity: ModelT) -> None:
        """Mark an entity for deletion and flush the operation."""
        try:
            await self._session.delete(entity)
            await self._session.flush()
            self._logger.debug("database_entity_deleted")
        except SQLAlchemyError as exc:
            self._logger.error("database_operation_failed", operation="delete", exc_info=True)
            raise PersistenceError("Could not delete entity.") from exc
