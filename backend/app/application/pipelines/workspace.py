import asyncio
import shutil
import tempfile
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

import structlog

from app.application.exceptions import WorkspaceError

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def pipeline_workspace() -> AsyncGenerator[Path]:
    """Create and remove a unique temporary workspace for pipeline execution."""
    try:
        workspace = Path(await asyncio.to_thread(tempfile.mkdtemp, prefix="repomind-pipeline-"))
    except OSError as exc:
        raise WorkspaceError("Could not create pipeline workspace.") from exc
    logger.debug("pipeline_workspace_created", workspace=str(workspace))
    try:
        yield workspace
    finally:
        try:
            await asyncio.to_thread(shutil.rmtree, workspace)
            logger.debug("pipeline_workspace_cleaned", workspace=str(workspace))
        except OSError:
            logger.warning(
                "pipeline_workspace_cleanup_failed",
                workspace=str(workspace),
                exc_info=True,
            )
