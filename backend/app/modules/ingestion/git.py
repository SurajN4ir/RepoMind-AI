"""Isolated asynchronous Git operations for repository workspace ingestion."""

import asyncio
from pathlib import Path

import structlog

from app.modules.ingestion.exceptions import GitCloneError

logger = structlog.get_logger(__name__)


class GitClient:
    """Run narrowly scoped Git commands without shell interpolation."""

    def __init__(self, executable: str = "git") -> None:
        self._executable = executable

    async def clone_shallow(self, url: str, default_branch: str, destination: Path) -> None:
        """Create a depth-one clone of ``default_branch`` at a caller-owned destination."""
        command = [
            self._executable,
            "clone",
            "--depth",
            "1",
            "--branch",
            default_branch,
            url,
            str(destination),
        ]
        logger.info("repository_clone_started", destination=str(destination))
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except OSError as exc:
            logger.error("repository_clone_process_failed", exc_info=True)
            raise GitCloneError("Git could not be started for repository cloning.") from exc

        _, stderr = await process.communicate()
        if process.returncode != 0:
            logger.warning("repository_clone_failed", return_code=process.returncode)
            detail = stderr.decode("utf-8", errors="replace").strip()
            raise GitCloneError(f"Shallow clone failed: {detail or 'unknown Git error'}")
        logger.info("repository_clone_completed")
