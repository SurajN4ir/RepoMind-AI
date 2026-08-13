"""Explicit transaction boundaries for async application use cases."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.database.exceptions import IntegrityConstraintError, TransactionError

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def transaction(session: AsyncSession) -> AsyncGenerator[AsyncSession]:
    """Execute a unit of work atomically and translate database errors.

    Callers own the session lifecycle. Nested use maps to a SAVEPOINT through
    SQLAlchemy's nested transaction support.
    """
    transaction_context = session.begin_nested() if session.in_transaction() else session.begin()
    try:
        logger.debug("database_transaction_started", nested=session.in_transaction())
        async with transaction_context:
            yield session
        logger.debug("database_transaction_committed")
    except IntegrityError as exc:
        logger.warning("database_transaction_integrity_error", exc_info=True)
        raise IntegrityConstraintError("A database integrity constraint was violated.") from exc
    except SQLAlchemyError as exc:
        logger.error("database_transaction_failed", exc_info=True)
        raise TransactionError("The database transaction failed.") from exc
