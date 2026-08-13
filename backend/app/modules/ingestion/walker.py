"""Filesystem traversal for clean repository manifests."""

import asyncio
import os
from dataclasses import dataclass
from pathlib import Path

from app.modules.ingestion.filters import RepositoryFileFilter
from app.modules.ingestion.manifest import RepositoryFile, RepositoryStats


@dataclass(frozen=True, slots=True)
class WalkResult:
    """Accepted files and selection statistics from one workspace traversal."""

    files: tuple[RepositoryFile, ...]
    stats: RepositoryStats


class RepositoryWalker:
    """Traverse a workspace without following links or retaining file contents."""

    def __init__(self, file_filter: RepositoryFileFilter) -> None:
        self._file_filter = file_filter

    async def walk(self, workspace: Path) -> WalkResult:
        """Traverse a workspace off the event loop and return a deterministic inventory."""
        return await asyncio.to_thread(self._walk_sync, workspace)

    def _walk_sync(self, workspace: Path) -> WalkResult:
        files: list[RepositoryFile] = []
        skipped_files = 0
        skipped_binary_files = 0
        skipped_oversized_files = 0
        total_bytes = 0

        for root, directories, filenames in os.walk(workspace, topdown=True, followlinks=False):
            directories[:] = sorted(
                directory
                for directory in directories
                if not self._file_filter.should_ignore_directory(directory)
            )
            root_path = Path(root)
            for filename in sorted(filenames):
                candidate = root_path / filename
                if candidate.is_symlink() or not candidate.is_file():
                    skipped_files += 1
                    continue
                try:
                    size_bytes = candidate.stat().st_size
                    decision = self._file_filter.evaluate(candidate, size_bytes)
                    if decision.include and self._file_filter.is_binary_file(candidate):
                        decision = decision.__class__(include=False, reason="binary")
                except OSError:
                    skipped_files += 1
                    continue

                if not decision.include:
                    skipped_files += 1
                    if decision.reason == "binary":
                        skipped_binary_files += 1
                    elif decision.reason == "oversized":
                        skipped_oversized_files += 1
                    continue

                relative_path = candidate.relative_to(workspace).as_posix()
                files.append(
                    RepositoryFile(
                        path=relative_path,
                        size_bytes=size_bytes,
                        extension=candidate.suffix.lower() or None,
                    )
                )
                total_bytes += size_bytes

        files.sort(key=lambda item: item.path)
        return WalkResult(
            files=tuple(files),
            stats=RepositoryStats(
                total_files=len(files),
                total_bytes=total_bytes,
                skipped_files=skipped_files,
                skipped_binary_files=skipped_binary_files,
                skipped_oversized_files=skipped_oversized_files,
            ),
        )
