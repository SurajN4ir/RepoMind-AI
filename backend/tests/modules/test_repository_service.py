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

OWNER_A = "user_a"
OWNER_B = "user_b"


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
        repository = await _service(session).register(_create_request(), OWNER_A)

    assert repository.status is RepositoryStatus.REGISTERED
    assert repository.id is not None
    assert repository.created_at is not None


@pytest.mark.asyncio
async def test_register_persists_caller_as_owner(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        repository = await _service(session).register(_create_request(), OWNER_A)

    assert repository.owner_id == OWNER_A


@pytest.mark.asyncio
async def test_prevents_duplicate_repository_urls(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        service = _service(session)
        await service.register(_create_request(), OWNER_A)

        with pytest.raises(DuplicateRepositoryError):
            await service.register(_create_request(name="Duplicate"), OWNER_A)


@pytest.mark.asyncio
async def test_updates_metadata_status_and_deletes_repository(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        service = _service(session)
        created = await service.register(_create_request(), OWNER_A)
        indexing = await service.update(
            created.id,
            UpdateRepositoryRequest(
                description="Repository metadata",
                status=RepositoryStatus.INDEXING,
            ),
            OWNER_A,
        )
        ready = await service.update_status(created.id, RepositoryStatus.READY)

        assert indexing.description == "Repository metadata"
        assert ready.status is RepositoryStatus.READY

        page = await service.list(PaginationParams(page=1, page_size=25), OWNER_A)
        assert page.total == 1
        assert await service.get(created.id, OWNER_A) == ready

        # End the read-only session transaction before the delete unit of work.
        await session.commit()
        await service.delete(created.id, OWNER_A)

        with pytest.raises(RepositoryNotFoundError):
            await service.get(created.id, OWNER_A)


@pytest.mark.asyncio
async def test_rejects_invalid_status_transition(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        service = _service(session)
        created = await service.register(_create_request(), OWNER_A)

        with pytest.raises(InvalidRepositoryStatusTransitionError):
            await service.update_status(created.id, RepositoryStatus.READY)


@pytest.mark.asyncio
async def test_validates_repository_metadata_and_url(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        service = _service(session)

        with pytest.raises(InvalidRepositoryMetadataError):
            await service.register(_create_request(name="   "), OWNER_A)
        with pytest.raises(InvalidRepositoryUrlError):
            await service.register(
                _create_request(url="git@github.com:example/repomind.git"), OWNER_A
            )


class TestRepositoryOwnership:
    """Cross-user isolation: an owner's repositories are invisible to everyone else."""

    @pytest.mark.asyncio
    async def test_list_only_returns_callers_own_repositories(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        async with session_factory() as session:
            service = _service(session)
            await service.register(_create_request(name="A's repo"), OWNER_A)
            await service.register(
                _create_request(name="B's repo", url="https://github.com/example/other"),
                OWNER_B,
            )

            page_a = await service.list(PaginationParams(page=1, page_size=25), OWNER_A)
            page_b = await service.list(PaginationParams(page=1, page_size=25), OWNER_B)

        assert [repo.name for repo in page_a.items] == ["A's repo"]
        assert [repo.name for repo in page_b.items] == ["B's repo"]

    @pytest.mark.asyncio
    async def test_owner_can_get_their_own_repository(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        async with session_factory() as session:
            service = _service(session)
            created = await service.register(_create_request(), OWNER_A)

            fetched = await service.get(created.id, OWNER_A)

        assert fetched.id == created.id

    @pytest.mark.asyncio
    async def test_other_user_cannot_get_repository(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        async with session_factory() as session:
            service = _service(session)
            created = await service.register(_create_request(), OWNER_A)

            with pytest.raises(RepositoryNotFoundError):
                await service.get(created.id, OWNER_B)

    @pytest.mark.asyncio
    async def test_other_user_cannot_update_repository(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        async with session_factory() as session:
            service = _service(session)
            created = await service.register(_create_request(), OWNER_A)

            with pytest.raises(RepositoryNotFoundError):
                await service.update(
                    created.id,
                    UpdateRepositoryRequest(description="hijacked"),
                    OWNER_B,
                )

    @pytest.mark.asyncio
    async def test_other_user_cannot_delete_repository(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        async with session_factory() as session:
            service = _service(session)
            created = await service.register(_create_request(), OWNER_A)
            created_id = created.id
            await session.commit()

            with pytest.raises(RepositoryNotFoundError):
                await service.delete(created_id, OWNER_B)

        # Still there, still fetchable by its real owner.
        async with session_factory() as session:
            assert await _service(session).get(created_id, OWNER_A) is not None

    @pytest.mark.asyncio
    async def test_nonexistent_and_not_owned_raise_the_same_error(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """Callers must not be able to tell "doesn't exist" apart from "not yours"."""
        from uuid import uuid4

        async with session_factory() as session:
            service = _service(session)
            created = await service.register(_create_request(), OWNER_A)

            not_owned_error = None
            not_found_error = None
            try:
                await service.get(created.id, OWNER_B)
            except RepositoryNotFoundError as exc:
                not_owned_error = str(exc)
            try:
                await service.get(uuid4(), OWNER_A)
            except RepositoryNotFoundError as exc:
                not_found_error = str(exc)

        assert not_owned_error is not None
        assert not_owned_error == not_found_error

    @pytest.mark.asyncio
    async def test_legacy_row_with_null_owner_is_inaccessible_not_misattributed(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """Migration 0009 leaves pre-existing rows with owner_id=NULL rather
        than inventing an owner. Confirm that actually behaves safely: such a
        row is invisible to every real caller, not owned by whoever asks."""
        from app.modules.repository.models import Repository

        async with session_factory() as session:
            legacy = Repository(
                owner_id=None,
                name="legacy-repo",
                url="https://github.com/example/legacy",
                provider=RepositoryProvider.GITHUB,
                default_branch="main",
                status=RepositoryStatus.REGISTERED,
            )
            session.add(legacy)
            await session.commit()
            legacy_id = legacy.id

        async with session_factory() as session:
            service = _service(session)
            with pytest.raises(RepositoryNotFoundError):
                await service.get(legacy_id, OWNER_A)
            with pytest.raises(RepositoryNotFoundError):
                await service.get(legacy_id, OWNER_B)

            page = await service.list(PaginationParams(page=1, page_size=25), OWNER_A)
        assert legacy_id not in {repo.id for repo in page.items}
