"""Isolated asynchronous Git operations for repository workspace ingestion."""

import asyncio
import subprocess
from pathlib import Path

import structlog

from app.modules.ingestion.exceptions import GitCloneError

logger = structlog.get_logger(__name__)


class GitClient:
    """Run narrowly scoped Git commands without shell interpolation."""

    def __init__(self, executable: str = "git") -> None:
        self._executable = executable

    async def clone_shallow(self, url: str, default_branch: str, destination: Path) -> None:
        """Create a depth-one clone of ``default_branch`` at a caller-owned destination.

        Runs via a worker thread rather than asyncio.create_subprocess_exec: on
        Windows, native asyncio subprocess support requires ProactorEventLoop,
        which conflicts with psycopg's async PostgreSQL driver (SelectorEventLoop
        only). A thread-pool subprocess call has no such event-loop requirement
        and behaves identically on Linux/Docker.
        """
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
            result = await asyncio.to_thread(
                subprocess.run,
                command,
                capture_output=True,
            )
        except OSError as exc:
            logger.error("repository_clone_process_failed", exc_info=True)
            raise GitCloneError("Git could not be started for repository cloning.") from exc

        if result.returncode != 0:
            logger.warning("repository_clone_failed", return_code=result.returncode)
            detail = result.stderr.decode("utf-8", errors="replace").strip()
            raise GitCloneError(f"Shallow clone failed: {detail or 'unknown Git error'}")
        logger.info("repository_clone_completed")
