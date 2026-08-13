"""Async unit tests for repository workspace ingestion."""

import asyncio
from dataclasses import dataclass, field
from pathlib import Path
from uuid import UUID

import pytest

from app.modules.ingestion.exceptions import GitCloneError, UnsupportedIngestionStatusError
from app.modules.ingestion.filters import IngestionFilterConfig, RepositoryFileFilter
from app.modules.ingestion.git import GitClient
from app.modules.ingestion.service import IngestionService
from app.modules.ingestion.walker import RepositoryWalker
from app.modules.repository.enums import RepositoryStatus
from app.shared.identifiers.uuid import new_uuid


def test_file_filter_rejects_oversized_and_known_binary_files(tmp_path: Path) -> None:
    file_filter = RepositoryFileFilter(IngestionFilterConfig(max_file_size_bytes=10))

    assert file_filter.evaluate(tmp_path / "large.py", 11).reason == "oversized"
    assert file_filter.evaluate(tmp_path / "image.png", 1).reason == "binary"
    assert file_filter.should_ignore_directory("node_modules")


@pytest.mark.asyncio
async def test_walker_filters_build_binary_and_oversized_files(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("print('ok')", encoding="utf-8")
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "dependency.js").write_text("ignored", encoding="utf-8")
    (tmp_path / "asset.dat").write_bytes(b"\x00binary")
    (tmp_path / "large.txt").write_bytes(b"x" * 21)

    walker = RepositoryWalker(RepositoryFileFilter(IngestionFilterConfig(max_file_size_bytes=20)))
    result = await walker.walk(tmp_path)

    assert [file.path for file in result.files] == ["src/main.py"]
    assert result.stats.total_files == 1
    assert result.stats.skipped_files == 2
    assert result.stats.skipped_binary_files == 1
    assert result.stats.skipped_oversized_files == 1


@pytest.mark.asyncio
async def test_git_client_uses_depth_one_clone_without_shell_interpolation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured_command: list[str] = []

    class CompletedProcess:
        returncode = 0

        async def communicate(self) -> tuple[bytes, bytes]:
            return b"", b""

    async def fake_create_subprocess_exec(*command: str, **_: object) -> CompletedProcess:
        captured_command.extend(command)
        return CompletedProcess()

    monkeypatch.setattr(asyncio, "create_subprocess_exec", fake_create_subprocess_exec)

    await GitClient("git-test").clone_shallow(
        "https://github.com/example/repomind",
        "main",
        Path("checkout"),
    )

    assert captured_command[:5] == ["git-test", "clone", "--depth", "1", "--branch"]
    assert captured_command[-2:] == ["https://github.com/example/repomind", "checkout"]


@dataclass
class _RepositoryRecord:
    id: UUID
    url: str = "https://github.com/example/repomind"
    default_branch: str = "main"
    status: RepositoryStatus = RepositoryStatus.REGISTERED


@dataclass
class _FakeRepositoryService:
    record: _RepositoryRecord
    status_updates: list[RepositoryStatus] = field(default_factory=list)

    async def get(self, _: UUID) -> _RepositoryRecord:
        return self.record

    async def update_status(
        self,
        _: UUID,
        status: RepositoryStatus,
        **__: object,
    ) -> _RepositoryRecord:
        self.record.status = status
        self.status_updates.append(status)
        return self.record


@dataclass
class _WritingGitClient:
    workspace: Path | None = None

    async def clone_shallow(self, _: str, __: str, destination: Path) -> None:
        self.workspace = destination.parent
        destination.mkdir()
        (destination / "main.py").write_text("print('ok')", encoding="utf-8")


class _FailingGitClient:
    async def clone_shallow(self, _: str, __: str, ___: Path) -> None:
        raise GitCloneError("clone failed")


@pytest.mark.asyncio
async def test_ingestion_returns_manifest_updates_status_and_cleans_workspace() -> None:
    repository_id = new_uuid()
    repository_service = _FakeRepositoryService(_RepositoryRecord(id=repository_id))
    git_client = _WritingGitClient()
    service = IngestionService(
        repository_service,  # type: ignore[arg-type]
        git_client,  # type: ignore[arg-type]
        RepositoryWalker(RepositoryFileFilter()),
    )

    manifest = await service.ingest(repository_id)

    assert manifest.repository_id == repository_id
    assert [file.path for file in manifest.files] == ["main.py"]
    assert repository_service.status_updates == [RepositoryStatus.INDEXING, RepositoryStatus.READY]
    assert git_client.workspace is not None
    assert not git_client.workspace.exists()


@pytest.mark.asyncio
async def test_ingestion_marks_repository_failed_after_clone_error() -> None:
    repository_id = new_uuid()
    repository_service = _FakeRepositoryService(_RepositoryRecord(id=repository_id))
    service = IngestionService(
        repository_service,  # type: ignore[arg-type]
        _FailingGitClient(),  # type: ignore[arg-type]
        RepositoryWalker(RepositoryFileFilter()),
    )

    with pytest.raises(GitCloneError):
        await service.ingest(repository_id)

    assert repository_service.status_updates == [RepositoryStatus.INDEXING, RepositoryStatus.FAILED]


@pytest.mark.asyncio
async def test_ingestion_rejects_archived_repository_without_running_git() -> None:
    repository_id = new_uuid()
    repository_service = _FakeRepositoryService(
        _RepositoryRecord(id=repository_id, status=RepositoryStatus.ARCHIVED)
    )
    service = IngestionService(
        repository_service,  # type: ignore[arg-type]
        _FailingGitClient(),  # type: ignore[arg-type]
        RepositoryWalker(RepositoryFileFilter()),
    )

    with pytest.raises(UnsupportedIngestionStatusError):
        await service.ingest(repository_id)

    assert repository_service.status_updates == []
