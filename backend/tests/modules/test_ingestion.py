"""Unit tests for ingestion primitives (file filtering, walking, git cloning).

These building blocks are used directly by RepositoryIndexingPipeline (the
canonical indexing path -- see repository_indexing_pipeline.py). There is no
longer a separate IngestionService orchestrating them independently: it was
removed in Phase 4 as a duplicate implementation of what the pipeline already
does (see docs/adr/0015-legacy-ingestion-endpoint-delegates-to-indexing-pipeline.md).
"""

import subprocess
from pathlib import Path

import pytest

from app.modules.ingestion.filters import IngestionFilterConfig, RepositoryFileFilter
from app.modules.ingestion.git import GitClient
from app.modules.ingestion.walker import RepositoryWalker


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

    def fake_run(command: list[str], **_: object) -> subprocess.CompletedProcess:
        captured_command.extend(command)
        return subprocess.CompletedProcess(command, returncode=0, stdout=b"", stderr=b"")

    monkeypatch.setattr(subprocess, "run", fake_run)

    await GitClient("git-test").clone_shallow(
        "https://github.com/example/repomind",
        "main",
        Path("checkout"),
    )

    assert captured_command[:5] == ["git-test", "clone", "--depth", "1", "--branch"]
    assert captured_command[-2:] == ["https://github.com/example/repomind", "checkout"]
