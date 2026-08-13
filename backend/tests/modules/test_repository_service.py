"""Repository bounded-context unit tests using isolated async SQLite storage."""

from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.config.settings import Settings
from app.modules.repository.enums import RepositoryProvider, RepositoryStatus
from app.modules.repository.exceptions import (
    DuplicateRepositoryError,
    InvalidRepositoryMetadataError,
    InvalidRepositoryStatusTransitionError,
    InvalidRepositoryUrlError,
    RepositoryNotFoundError,
)
from app.modules.repository.repository import RepositoryRepository
from app.modules.repository.schemas import CreateRepositoryRequest, UpdateRepositoryRequest
from app.modules.repository.service import RepositoryService
from app.shared.database.base import Base
from app.shared.database.pagination import PaginationParams
from app.shared.database.session import build_async_engine


@pytest.fixture
async def engine(tmp_path: Path) -> AsyncGenerator[AsyncEngine]:
    """Create a fresh database containing only shared and Repository metadata."""
    database_path = tmp_path / "repository.db"
    async_engine = build_async_engine(Settings(database_url=f"sqlite+aiosqlite:///{database_path}"))
    async with async_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield async_engine
    await async_engine.dispose()


@pytest.fixture
def session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)


def _service(session: AsyncSession) -> RepositoryService:
    return RepositoryService(session, RepositoryRepository(session))


def _create_request(**overrides: object) -> CreateRepositoryRequest:
    values: dict[str, object] = {
        "name": "RepoMind",
        "url": "https://github.com/example/repomind",
        "provider": RepositoryProvider.GITHUB,
        "default_branch": "main",
    }
    values.update(overrides)
    return CreateRepositoryRequest.model_validate(values)


@pytest.mark.asyncio
async def test_registers_repository_with_registered_status(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        repository = await _service(session).register(_create_request())

    assert repository.status is RepositoryStatus.REGISTERED
    assert repository.id is not None
    assert repository.created_at is not None


@pytest.mark.asyncio
async def test_prevents_duplicate_repository_urls(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        service = _service(session)
        await service.register(_create_request())

        with pytest.raises(DuplicateRepositoryError):
            await service.register(_create_request(name="Duplicate"))


@pytest.mark.asyncio
async def test_updates_metadata_status_and_deletes_repository(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        service = _service(session)
        created = await service.register(_create_request())
        indexing = await service.update(
            created.id,
            UpdateRepositoryRequest(
                description="Repository metadata",
                status=RepositoryStatus.INDEXING,
            ),
        )
        ready = await service.update_status(created.id, RepositoryStatus.READY)

        assert indexing.description == "Repository metadata"
        assert ready.status is RepositoryStatus.READY

        page = await service.list(PaginationParams(page=1, page_size=25))
        assert page.total == 1
        assert await service.get(created.id) == ready

        # End the read-only session transaction before the delete unit of work.
        await session.commit()
        await service.delete(created.id)

        with pytest.raises(RepositoryNotFoundError):
            await service.get(created.id)


@pytest.mark.asyncio
async def test_rejects_invalid_status_transition(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        service = _service(session)
        created = await service.register(_create_request())

        with pytest.raises(InvalidRepositoryStatusTransitionError):
            await service.update_status(created.id, RepositoryStatus.READY)


@pytest.mark.asyncio
async def test_validates_repository_metadata_and_url(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        service = _service(session)

        with pytest.raises(InvalidRepositoryMetadataError):
            await service.register(_create_request(name="   "))
        with pytest.raises(InvalidRepositoryUrlError):
            await service.register(_create_request(url="git@github.com:example/repomind.git"))
