"""Unit tests for shared persistence mechanics using an isolated SQLite database."""

from collections.abc import AsyncGenerator
from pathlib import Path
from uuid import UUID

import pytest
from alembic.config import Config
from sqlalchemy import String, select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.database.base import Base
from app.shared.database.exceptions import IntegrityConstraintError
from app.shared.database.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from app.shared.database.pagination import PaginationParams
from app.shared.database.repository import BaseRepository
from app.shared.database.session import build_async_engine
from app.shared.database.transactions import transaction


class PersistenceTestRecord(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Test-only model proving shared mapping and repository behavior."""

    __tablename__ = "persistence_test_records"

    name: Mapped[str] = mapped_column(String(100), unique=True)


@pytest.fixture
async def engine(tmp_path: Path) -> AsyncGenerator[AsyncEngine]:
    from app.config.settings import Settings

    database_path = tmp_path / "persistence.db"
    async_engine = build_async_engine(Settings(database_url=f"sqlite+aiosqlite:///{database_path}"))
    async with async_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield async_engine
    await async_engine.dispose()


@pytest.fixture
def session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)


@pytest.mark.asyncio
async def test_repository_persists_and_paginates_records(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        repository = BaseRepository(session, PersistenceTestRecord)
        async with transaction(session):
            first = await repository.add(PersistenceTestRecord(name="first"))
            await repository.add(PersistenceTestRecord(name="second"))

        assert isinstance(first.id, UUID)
        assert first.created_at is not None
        assert first.updated_at is not None

    async with session_factory() as session:
        repository = BaseRepository(session, PersistenceTestRecord)
        result = await repository.list(PaginationParams(page=1, page_size=1))

        assert result.total == 2
        assert len(result.items) == 1
        assert result.total_pages == 2
        await session.commit()  # End the read-only autobegin transaction before a new unit of work.
        fetched = await repository.get_or_raise(first.id)
        await session.commit()
        fetched.name = "renamed"
        async with transaction(session):
            await repository.update(fetched)

    async with session_factory() as session:
        repository = BaseRepository(session, PersistenceTestRecord)
        renamed = await repository.get_or_raise(first.id)
        await session.commit()
        async with transaction(session):
            await repository.delete(renamed)
        assert await repository.get(first.id) is None


@pytest.mark.asyncio
async def test_transaction_translates_integrity_errors(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        repository = BaseRepository(session, PersistenceTestRecord)
        async with transaction(session):
            await repository.add(PersistenceTestRecord(name="duplicate"))

        with pytest.raises(IntegrityConstraintError):
            async with transaction(session):
                await repository.add(PersistenceTestRecord(name="duplicate"))


def test_alembic_is_configured_for_async_shared_metadata() -> None:
    config = Config("alembic.ini")
    environment_path = Path("backend/alembic/env.py")

    assert config.get_main_option("script_location") == "backend/alembic"
    assert "app.shared.database.base import Base" in environment_path.read_text(encoding="utf-8")
    assert "async_engine_from_config" in environment_path.read_text(encoding="utf-8")


@pytest.mark.asyncio
async def test_transaction_rolls_back_when_application_code_fails(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        repository = BaseRepository(session, PersistenceTestRecord)
        with pytest.raises(RuntimeError):
            async with transaction(session):
                await repository.add(PersistenceTestRecord(name="rollback"))
                raise RuntimeError("intentional")

    async with session_factory() as session:
        names = (await session.scalars(select(PersistenceTestRecord.name))).all()
        assert names == []
