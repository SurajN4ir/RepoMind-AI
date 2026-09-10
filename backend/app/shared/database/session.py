"""Async SQLAlchemy engine, session factory, and FastAPI dependency providers."""

from collections.abc import AsyncGenerator
from functools import lru_cache

import structlog
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config.settings import Settings, get_settings

logger = structlog.get_logger(__name__)


def build_async_engine(settings: Settings) -> AsyncEngine:
    """Create an async engine without opening a database connection."""
    logger.info("database_engine_configured", dialect=settings.database_url.split(":", 1)[0])
    connect_args: dict[str, object] = {}
    options: dict[str, bool | int | dict[str, object]] = {
        "echo": settings.database_echo,
        "pool_pre_ping": True,
    }
    if settings.database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    else:
        options.update(
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
        )
    options["connect_args"] = connect_args
    return create_async_engine(settings.database_url, **options)


@lru_cache
def get_engine() -> AsyncEngine:
    """Return the process-wide async engine, constructed on first use."""
    return build_async_engine(get_settings())


@lru_cache
def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return a session factory with predictable unit-of-work defaults."""
    return async_sessionmaker(get_engine(), autoflush=False, expire_on_commit=False)


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    """Yield a request-scoped session; commit on success, roll back on failure.

    Modules use ``app.shared.database.transactions.transaction()`` for
    explicit unit-of-work boundaries within a request, but those calls begin
    a *nested* transaction (SAVEPOINT) whenever the session already has one
    open -- which happens the moment any earlier write auto-begins one. Only
    an outermost commit actually persists to disk; without one here, writes
    made after the first `transaction()` call in a request (e.g. anything
    after a repository status update) build up in that auto-begun
    transaction and silently roll back when the session closes.
    """
    async with get_session_factory()() as session:
        logger.debug("database_session_opened")
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            logger.debug("database_session_closed")


async def get_secondary_db_session() -> AsyncGenerator[AsyncSession]:
    """Yield a second, independent request-scoped session.

    SQLAlchemy's AsyncSession is not safe for concurrent use by two
    coroutines. RetrievalService runs its vector and keyword read ports
    concurrently via asyncio.gather, so those two ports must not share one
    session when both are DB-backed. Use this for one of them; the primary
    session from ``get_db_session`` covers everything else.
    """
    async with get_session_factory()() as session:
        logger.debug("secondary_database_session_opened")
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            logger.debug("secondary_database_session_closed")


async def dispose_engine() -> None:
    """Dispose of pooled connections during controlled application shutdown."""
    if get_engine.cache_info().currsize:
        await get_engine().dispose()
        get_session_factory.cache_clear()
        get_engine.cache_clear()
        logger.info("database_engine_disposed")
