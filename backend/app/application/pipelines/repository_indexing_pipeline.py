from __future__ import annotations

import re
import traceback
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from uuid import UUID

import structlog

from app.application.exceptions import PipelineError, ValidationError, WorkspaceError
from app.application.pipelines.models import PipelineContext, RepositoryIndexingResult
from app.application.pipelines.workspace import pipeline_workspace
from app.application.services.repository import RepositoryApplicationService
from app.modules.chunker.models import ChunkCollection
from app.modules.chunker.service import SemanticChunkerService
from app.modules.embedding.models import EmbeddingCollection
from app.modules.embedding.service import EmbeddingService
from app.modules.indexing.models import RepositoryIndex
from app.modules.indexing.repository import (
    ActivityRepository,
    DependencyRepository,
    FileContentRepository,
)
from app.modules.indexing.service import IndexingService
from app.modules.ingestion.filters import IngestionFilterConfig, RepositoryFileFilter
from app.modules.ingestion.git import GitClient
from app.modules.ingestion.manifest import RepositoryManifest
from app.modules.ingestion.walker import RepositoryWalker, WalkResult
from app.modules.parser.models import ParsedFile, ParsedRepository
from app.modules.parser.service import SemanticParserService
from app.modules.repository.models import Repository, RepositoryStatus

logger = structlog.get_logger(__name__)


class RepositoryIndexingPipeline:
    """Coordinate the full write-side repository indexing workflow.

    Composes domain services into a single fault-tolerant pipeline that
    owns temporary workspace lifecycles, status transitions, and error
    recovery — superseding the orchestration that previously lived inside
    ``IngestionService``.
    """

    def __init__(
        self,
        repository_service: RepositoryApplicationService,
        git_client: GitClient | None = None,
        walker: RepositoryWalker | None = None,
        parser: SemanticParserService | None = None,
        chunker: SemanticChunkerService | None = None,
        embedding_service: EmbeddingService | None = None,
        indexing_service: IndexingService | None = None,
        filter_config: IngestionFilterConfig | None = None,
        file_content_store: FileContentRepository | None = None,
        dependency_store: DependencyRepository | None = None,
        activity_store: ActivityRepository | None = None,
    ) -> None:
        self._repository_service = repository_service
        self._git_client = git_client or GitClient()
        self._walker = walker or RepositoryWalker(
            RepositoryFileFilter(filter_config or IngestionFilterConfig())
        )
        self._parser = parser or SemanticParserService()
        self._chunker = chunker or SemanticChunkerService()
        self._embedding_service = embedding_service
        self._indexing_service = indexing_service
        self._file_content_store = file_content_store
        self._dependency_store = dependency_store
        self._activity_store = activity_store

    async def execute(
        self,
        repository_id: UUID,
        *,
        clone_url: str | None = None,
        branch: str | None = None,
    ) -> RepositoryIndexingResult:
        context = PipelineContext(repository_id=repository_id, started_at=datetime.now(UTC))
        indexing_set = False
        try:
            repository = await self._load_repository(context, repository_id)
            await self._validate_and_mark_indexing(context, repository)
            indexing_set = True

            async with pipeline_workspace() as workspace:
                clone_path = await self._clone(context, repository, workspace, clone_url, branch)
                walk_result = await self._walk(context, clone_path)
                manifest = self._create_manifest(context, walk_result)
                parsed = await self._parse(context, manifest, clone_path)
                await self._store_file_contents(context, parsed)
                await self._resolve_and_store_dependencies(context, parsed)
                context.chunks = self._chunk(context, parsed)

            if context.chunks and self._embedding_service is not None:
                context.embedding_collection = await self._embed(context)

            if context.embedding_collection and self._indexing_service is not None:
                context.repository_index = await self._index(context)

            await self._finalize(context, manifest.generated_at)
            return self._build_result(context, success=True)

        except Exception:
            logger.exception("pipeline_execution_failed", repository_id=str(repository_id))
            error_msg = traceback.format_exc()
            context.errors.append(error_msg)
            if indexing_set:
                await self._safe_set_failed(repository_id)
            return self._build_result(context, success=False)

    async def _load_repository(self, context: PipelineContext, repository_id: UUID) -> Repository:
        repository = await self._repository_service.get(repository_id)
        context.repository = repository
        return repository

    async def _validate_and_mark_indexing(
        self, context: PipelineContext, repository: Repository
    ) -> None:
        allowed = {RepositoryStatus.REGISTERED, RepositoryStatus.READY, RepositoryStatus.FAILED}
        if repository.status not in allowed:
            raise ValidationError(
                f"Repository {repository.id} has status {repository.status.value}; "
                f"expected one of {[s.value for s in allowed]}"
            )
        await self._repository_service.update_status(
            context.repository_id, RepositoryStatus.INDEXING
        )
        if self._activity_store is not None:
            await self._activity_store.record_activity(
                context.repository_id,
                "index_started",
                f"Indexing started for {repository.name}",
            )

    async def _clone(
        self,
        context: PipelineContext,
        repository: Repository,
        workspace: Path,
        clone_url: str | None,
        branch: str | None,
    ) -> Path:
        url = clone_url or repository.url
        target = workspace / repository.name
        try:
            await self._git_client.clone_shallow(url, branch, target)
        except Exception as exc:
            raise WorkspaceError(f"Failed to clone repository: {exc}") from exc
        return target

    async def _walk(self, context: PipelineContext, source_path: Path) -> WalkResult:
        try:
            return await self._walker.walk(source_path)
        except Exception as exc:
            raise WorkspaceError(f"Failed to walk repository: {exc}") from exc

    def _create_manifest(
        self, context: PipelineContext, walk_result: WalkResult
    ) -> RepositoryManifest:
        manifest = RepositoryManifest.create(
            context.repository_id, walk_result.files, walk_result.stats
        )
        context.manifest = manifest
        return manifest

    async def _parse(
        self, context: PipelineContext, manifest: RepositoryManifest, source_root: Path
    ) -> ParsedRepository:
        parsed = await self._parser.parse(manifest, source_root)
        context.parsed_repository = parsed
        return parsed

    def _chunk(self, context: PipelineContext, parsed: ParsedRepository) -> ChunkCollection:
        chunks = self._chunker.chunk(parsed)
        context.chunks = chunks
        return chunks

    async def _store_file_contents(
        self, context: PipelineContext, parsed: ParsedRepository
    ) -> None:
        if self._file_content_store is None:
            return

        parsed_files = {pf.path: pf for pf in parsed.files if pf.source is not None}

        current = {
            path: sha256(pf.source.encode("utf-8")).hexdigest() for path, pf in parsed_files.items()
        }

        existing = await self._file_content_store.get_file_path_hashes(context.repository_id)

        stale = [path for path in existing if path not in current]
        if stale:
            await self._file_content_store.delete_file_contents(context.repository_id, stale)

        stored = 0
        for file_path, content_hash in current.items():
            if existing.get(file_path) == content_hash:
                continue
            pf = parsed_files[file_path]
            await self._file_content_store.store_file_content(
                repository_id=context.repository_id,
                file_path=file_path,
                content=pf.source,
                content_hash=content_hash,
            )
            stored += 1

        logger.info(
            "pipeline_file_contents_stored",
            repository_id=str(context.repository_id),
            stored=stored,
            deleted=len(stale),
        )

    async def _resolve_and_store_dependencies(
        self, context: PipelineContext, parsed: ParsedRepository
    ) -> None:
        if self._dependency_store is None:
            return

        edges = _resolve_file_dependencies(parsed.files)
        if edges:
            await self._dependency_store.store_dependencies(context.repository_id, list(edges))

    async def _embed(self, context: PipelineContext) -> EmbeddingCollection:
        if self._embedding_service is None:
            raise PipelineError("Embedding service is not configured.")
        if context.chunks is None:
            raise PipelineError("Cannot embed without chunks.")
        try:
            collection = await self._embedding_service.embed(context.chunks)
            logger.info(
                "pipeline_embedding_completed",
                repository_id=str(context.repository_id),
                vector_count=len(collection.vectors),
            )
            return collection
        except Exception as exc:
            raise PipelineError(f"Embedding step failed: {exc}") from exc

    async def _index(self, context: PipelineContext) -> RepositoryIndex:
        if self._indexing_service is None:
            raise PipelineError("Indexing service is not configured.")
        if context.embedding_collection is None:
            raise PipelineError("Cannot index without an embedding collection.")
        try:
            result = await self._indexing_service.index(context.embedding_collection)
            logger.info(
                "pipeline_indexing_completed",
                repository_id=str(context.repository_id),
                inserted=result.statistics.inserted,
                updated=result.statistics.updated,
                deleted=result.statistics.deleted,
            )
            return result
        except Exception as exc:
            raise PipelineError(f"Indexing step failed: {exc}") from exc

    async def _finalize(self, context: PipelineContext, last_indexed_at: datetime) -> None:
        total_files = context.manifest.stats.total_files if context.manifest is not None else None
        await self._repository_service.update_status(
            context.repository_id,
            RepositoryStatus.READY,
            last_indexed_at=last_indexed_at,
            total_files=total_files,
        )
        if self._activity_store is not None:
            parsed_files = context.parsed_repository.files if context.parsed_repository else []
            stored = len([pf for pf in parsed_files if pf.source is not None])
            repo_name = context.repository.name if context.repository else "repository"
            await self._activity_store.record_activity(
                context.repository_id,
                "index_completed",
                f"Indexed {stored} files from {repo_name}",
            )

    async def _safe_set_failed(self, repository_id: UUID) -> None:
        try:
            await self._repository_service.update_status(repository_id, RepositoryStatus.FAILED)
        except Exception:
            logger.exception(
                "failed_to_set_repository_failed",
                repository_id=str(repository_id),
            )
        if self._activity_store is not None:
            try:
                await self._activity_store.record_activity(
                    repository_id,
                    "index_failed",
                    "Indexing failed — check logs for details",
                )
            except Exception:
                logger.exception("failed_to_record_activity", repository_id=str(repository_id))

    def _build_result(self, context: PipelineContext, *, success: bool) -> RepositoryIndexingResult:
        now = datetime.now(UTC)
        elapsed = (now - (context.started_at or now)).total_seconds()
        return RepositoryIndexingResult(
            repository_id=context.repository_id,
            success=success,
            manifest=context.manifest,
            parsed_repository=context.parsed_repository,
            chunks=context.chunks,
            embedding_collection=context.embedding_collection,
            repository_index=context.repository_index,
            elapsed_seconds=elapsed,
            errors=tuple(context.errors),
        )


# ---- Import resolution helpers ----


_AMBIGUOUS: object = object()
"""Sentinel used to mark lookup keys that map to more than one file."""


def _try_register(known: dict[str, str | object], key: str, path: str) -> None:
    """Register *path* under *key* if the mapping is unambiguous.

    If *key* is already registered to a different path the key is marked
    ``_AMBIGUOUS`` so that lookups produce no result.  Prefer no edge
    over a wrong edge.
    """
    existing = known.get(key)
    if existing is _AMBIGUOUS:
        return
    if existing is None:
        known[key] = path
    elif existing != path:
        known[key] = _AMBIGUOUS


def _resolve_file_dependencies(
    parsed_files: tuple[ParsedFile, ...],
) -> set[tuple[str, str]]:
    """Resolve import references to known file paths within the parsed repository.

    Returns a set of (source_path, target_path) dependency edges.
    """
    known: dict[str, str | object] = {}
    for pf in parsed_files:
        p = pf.path
        known[p] = p
        stem = p.rsplit(".", 1)[0] if "." in p else p
        known[stem] = p
        _try_register(known, stem.replace("/", "."), p)
        leaf = stem.rsplit("/", 1)[-1] if "/" in stem else stem
        _try_register(known, leaf, p)
        parts = stem.split("/")
        for i in range(1, len(parts)):
            _try_register(known, "/".join(parts[i:]), p)

    edges: set[tuple[str, str]] = set()
    for pf in parsed_files:
        for imp in pf.imports:
            source = pf.path
            statement = imp.statement

            # ---- Python absolute ----
            module = _extract_module_name(statement)
            if module:
                target = known.get(module)
                if target is not None and target is not _AMBIGUOUS and target != source:
                    edges.add((source, target))
                    continue

            # ---- Python relative ----
            relative = _resolve_relative_import(source, statement)
            if relative:
                target = known.get(relative)
                if target is not None and target is not _AMBIGUOUS and target != source:
                    edges.add((source, target))
                    continue
                # ``from . import X`` — module_part was empty and the
                # resolved ``__init__`` either didn't exist or *is* the
                # importing file.  Try the imported names as submodule
                # files of the same package.
                sub_target = _resolve_submodule_import(source, statement, known)
                if sub_target is not None and sub_target != source:
                    edges.add((source, sub_target))
                    continue

            # ---- JS / TS ----
            js_target = _resolve_js_import(source, statement, known)
            if js_target is not None and js_target != source:
                edges.add((source, js_target))

    return edges


# ---- Python import helpers ----


def _extract_module_name(statement: str) -> str | None:
    """Extract the absolute module name from a Python import statement."""
    m = re.match(
        r"from\s+([a-zA-Z_][\w.]*(?:\.[a-zA-Z_][\w.]*)*)\s+import",
        statement,
    )
    if m:
        return m.group(1)
    m = re.match(r"import\s+([a-zA-Z_][\w.]*)", statement)
    if m:
        parts = m.group(1).split(".")
        return parts[0]
    return None


def _resolve_relative_import(importing_file: str, statement: str) -> str | None:
    """Resolve a relative Python import to a candidate file path.

    Handles ``from .``, ``from ..``, etc.  The caller is responsible for
    following up on ``from . import X`` cases (see
    :func:`_resolve_submodule_import`).
    """
    m = re.match(r"from\s+(\.+)([\w.]*)\s+import", statement)
    if not m:
        return None
    dots = len(m.group(1))
    module_part = m.group(2).replace(".", "/")
    parts = importing_file.split("/")
    if len(parts) <= dots:
        return None
    base = "/".join(parts[:-dots])
    if module_part:
        return f"{base}/{module_part}"
    return f"{base}/__init__"


def _resolve_submodule_import(
    importing_file: str,
    statement: str,
    known: dict[str, str | object],
) -> str | None:
    """Resolve ``from . import X`` when *X* is a sibling submodule file.

    Called after ``_resolve_relative_import`` returned a path that did
    not match any known file.  Iterates the comma-separated names after
    ``import`` and checks whether each exists as a module or file in the
    same directory.
    """
    m = re.match(r"from\s+(\.+)\s+import\s+(.+)", statement)
    if not m:
        return None
    dots = len(m.group(1))
    parts = importing_file.split("/")
    if len(parts) <= dots:
        return None
    base = "/".join(parts[:-dots])
    names = re.split(r"\s*,\s*", m.group(2))
    for raw_name in names:
        name = re.sub(r"\s+as\s+\w+", "", raw_name).strip()
        if not name:
            continue
        for candidate in (f"{base}/{name}", f"{base}/{name}/__init__"):
            target = known.get(candidate)
            if target is not None and target is not _AMBIGUOUS:
                return target
    return None


# ---- JS / TS import helpers ----


_JS_EXTENSIONS = (".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs")
"""Common JS/TS file extensions tried during module resolution."""


def _resolve_js_import(
    source: str,
    statement: str,
    known: dict[str, str | object],
) -> str | None:
    """Resolve a JS/TS import statement to a known file path.

    Handles::

        import X from "..."
        import { X } from "..."
        import * as X from "..."
        import "..."          (side-effect import)
        export { X } from "..."
        export * from "..."

    Non-relative (npm) imports are silently skipped.  Relative imports
    are resolved against the importing file's directory with extension
    probing (``.js``, ``.ts``, ``.jsx``, ``.tsx``, ``.mjs``, ``.cjs``)
    and ``/index`` fallback.
    """
    m = re.search(r"""(?:from|import)\s*['"]([^'"]+)['"]""", statement)
    if not m:
        return None
    specifier = m.group(1)

    if not specifier.startswith("."):
        return None  # npm package or bare specifier — skip

    dirname = source.rsplit("/", 1)[0] if "/" in source else ""
    parts = dirname.split("/") if dirname else []

    for segment in specifier.split("/"):
        if segment in ("", "."):
            continue
        if segment == "..":
            if parts:
                parts.pop()
        else:
            parts.append(segment)

    base = "/".join(parts)

    # Direct match first, then extension probing, then /index fallback
    for candidates in (
        (base,),
        tuple(base + ext for ext in _JS_EXTENSIONS),
        tuple(f"{base}/index{ext}" for ext in ("",) + _JS_EXTENSIONS),
    ):
        for candidate in candidates:
            target = known.get(candidate)
            if target is not None and target is not _AMBIGUOUS:
                return target

    return None
