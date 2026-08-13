"""Semantic parsing orchestration over manifests and ephemeral source workspaces."""

import asyncio
from pathlib import Path

import structlog

from app.modules.ingestion.manifest import RepositoryManifest
from app.modules.parser.exceptions import SourceRootError
from app.modules.parser.language import LanguageDetector, SupportedLanguage
from app.modules.parser.models import ParsedFile, ParsedRepository
from app.modules.parser.tree_sitter import TreeSitterParser
from app.modules.parser.visitors import SemanticVisitor

logger = structlog.get_logger(__name__)


class SemanticParserService:
    """Transform a manifest and its ephemeral source root into semantic domain models."""

    def __init__(
        self,
        language_detector: LanguageDetector | None = None,
        tree_sitter: TreeSitterParser | None = None,
        visitor: SemanticVisitor | None = None,
    ) -> None:
        self._language_detector = language_detector or LanguageDetector()
        self._tree_sitter = tree_sitter or TreeSitterParser()
        self._visitor = visitor or SemanticVisitor()

    async def parse(self, manifest: RepositoryManifest, source_root: Path) -> ParsedRepository:
        """Parse every supported manifest file, retaining per-file failures instead of stopping."""
        root = source_root.resolve()
        files = tuple(
            [await self._parse_file(manifest_file.path, root) for manifest_file in manifest.files]
        )
        parsed_repository = ParsedRepository.create(manifest.repository_id, files)
        logger.info(
            "repository_semantic_parse_completed",
            repository_id=str(manifest.repository_id),
            parsed_files=parsed_repository.stats.parsed_files,
            failed_files=parsed_repository.stats.failed_files,
        )
        return parsed_repository

    async def _parse_file(self, manifest_path: str, source_root: Path) -> ParsedFile:
        language = self._language_detector.detect(manifest_path)
        if language is None:
            return ParsedFile(
                path=manifest_path,
                language=None,
                symbols=(),
                imports=(),
                exports=(),
                docstrings=(),
                comments=(),
                parse_error=None,
            )
        try:
            source_path = self._resolve_source_path(source_root, manifest_path)
            return await asyncio.to_thread(
                self._parse_file_sync,
                manifest_path,
                source_path,
                language,
            )
        except Exception as exc:
            logger.warning("repository_file_parse_failed", path=manifest_path, exc_info=True)
            return ParsedFile(
                path=manifest_path,
                language=language,
                symbols=(),
                imports=(),
                exports=(),
                docstrings=(),
                comments=(),
                parse_error=str(exc) or exc.__class__.__name__,
            )

    def _parse_file_sync(
        self,
        manifest_path: str,
        source_path: Path,
        language: SupportedLanguage,
    ) -> ParsedFile:
        source = source_path.read_bytes()
        tree = self._tree_sitter.parse(source, language, manifest_path)
        extraction = self._visitor.extract(tree, source, language)
        parse_error = "Tree-sitter detected syntax errors." if tree.root_node.has_error else None
        return ParsedFile(
            path=manifest_path,
            language=language,
            symbols=extraction.symbols,
            imports=extraction.imports,
            exports=extraction.exports,
            docstrings=extraction.docstrings,
            comments=extraction.comments,
            parse_error=parse_error,
            source=source.decode("utf-8", errors="replace"),
            ast=tree,
        )

    @staticmethod
    def _resolve_source_path(source_root: Path, manifest_path: str) -> Path:
        candidate = (source_root / manifest_path).resolve()
        if candidate != source_root and source_root not in candidate.parents:
            raise SourceRootError("Manifest path resolves outside the supplied source root.")
        return candidate
