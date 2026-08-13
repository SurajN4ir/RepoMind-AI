"""Language-aware semantic chunking strategies."""

import re
from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.chunker.builders import ChunkBuilder, chunk_type_for_symbol
from app.modules.chunker.models import Chunk, ChunkType
from app.modules.parser.language import SupportedLanguage
from app.modules.parser.models import ParsedFile


class ChunkStrategy(ABC):
    """Create semantic chunks from one parser-produced file representation."""

    @abstractmethod
    def build_chunks(self, parsed_file: ParsedFile, builder: ChunkBuilder) -> list[Chunk]:
        """Build chunks for a single parsed file."""


class SymbolChunkStrategy(ChunkStrategy):
    """Chunk parser-declared symbols and file imports for a programming language."""

    def build_chunks(self, parsed_file: ParsedFile, builder: ChunkBuilder) -> list[Chunk]:
        if parsed_file.source is None:
            return []
        chunks: list[Chunk] = []
        if parsed_file.imports:
            import_lines = [reference.statement for reference in parsed_file.imports]
            chunks.append(
                builder.build(
                    repository_id=self._repository_id,
                    file_path=parsed_file.path,
                    language=parsed_file.language,
                    content="\n".join(import_lines),
                    start_line=min(reference.start_line for reference in parsed_file.imports),
                    end_line=max(reference.start_line for reference in parsed_file.imports),
                    chunk_type=ChunkType.IMPORTS,
                    imports=parsed_file.imports,
                    exports=parsed_file.exports,
                )
            )
        lines = parsed_file.source.splitlines()
        for symbol in parsed_file.symbols:
            content = _line_range(lines, symbol.start_line, symbol.end_line)
            if not content.strip():
                continue
            chunks.append(
                builder.build(
                    repository_id=self._repository_id,
                    file_path=parsed_file.path,
                    language=parsed_file.language,
                    content=content,
                    start_line=symbol.start_line,
                    end_line=symbol.end_line,
                    chunk_type=chunk_type_for_symbol(symbol.kind),
                    symbol=symbol,
                    imports=parsed_file.imports,
                    exports=parsed_file.exports,
                )
            )
        if not chunks and parsed_file.source.strip():
            chunks.append(
                builder.build(
                    repository_id=self._repository_id,
                    file_path=parsed_file.path,
                    language=parsed_file.language,
                    content=parsed_file.source.strip(),
                    start_line=1,
                    end_line=len(parsed_file.source.splitlines()),
                    chunk_type=ChunkType.MODULE,
                    imports=parsed_file.imports,
                    exports=parsed_file.exports,
                )
            )
        return chunks

    def __init__(self, repository_id: UUID) -> None:
        self._repository_id = repository_id


class PythonChunkStrategy(SymbolChunkStrategy):
    """Python symbols are already extracted by the semantic parser."""


class JavaScriptChunkStrategy(SymbolChunkStrategy):
    """JavaScript symbols are already extracted by the semantic parser."""


class TypeScriptChunkStrategy(SymbolChunkStrategy):
    """TypeScript symbols are already extracted by the semantic parser."""


class MarkdownChunkStrategy(ChunkStrategy):
    """Create one README-section chunk for each Markdown heading section."""

    _HEADING = re.compile(r"^(#{1,6})\s+.+", re.MULTILINE)

    def __init__(self, repository_id: UUID) -> None:
        self._repository_id = repository_id

    def build_chunks(self, parsed_file: ParsedFile, builder: ChunkBuilder) -> list[Chunk]:
        if not parsed_file.source:
            return []
        lines = parsed_file.source.splitlines()
        headings = [index for index, line in enumerate(lines) if self._HEADING.match(line)]
        if not headings:
            return self._single_section(parsed_file, builder, lines)
        chunks: list[Chunk] = []
        for position, start_index in enumerate(headings):
            end_index = headings[position + 1] if position + 1 < len(headings) else len(lines)
            content = "\n".join(lines[start_index:end_index]).strip()
            if content:
                chunks.append(
                    builder.build(
                        repository_id=self._repository_id,
                        file_path=parsed_file.path,
                        language=None,
                        content=content,
                        start_line=start_index + 1,
                        end_line=end_index,
                        chunk_type=ChunkType.README_SECTION,
                    )
                )
        return chunks

    def _single_section(
        self,
        parsed_file: ParsedFile,
        builder: ChunkBuilder,
        lines: list[str],
    ) -> list[Chunk]:
        content = "\n".join(lines).strip()
        if not content:
            return []
        return [
            builder.build(
                repository_id=self._repository_id,
                file_path=parsed_file.path,
                language=None,
                content=content,
                start_line=1,
                end_line=len(lines),
                chunk_type=ChunkType.README_SECTION,
            )
        ]


class ConfigurationChunkStrategy(ChunkStrategy):
    """Split common configuration formats at top-level logical section boundaries."""

    _SECTION = re.compile(r"^(?:\[[^\]]+\]|[^\s][^:]*:)")

    def __init__(self, repository_id: UUID) -> None:
        self._repository_id = repository_id

    def build_chunks(self, parsed_file: ParsedFile, builder: ChunkBuilder) -> list[Chunk]:
        if not parsed_file.source:
            return []
        lines = parsed_file.source.splitlines()
        starts = [index for index, line in enumerate(lines) if self._SECTION.match(line)]
        if not starts:
            starts = [0]
        chunks: list[Chunk] = []
        for position, start_index in enumerate(starts):
            end_index = starts[position + 1] if position + 1 < len(starts) else len(lines)
            content = "\n".join(lines[start_index:end_index]).strip()
            if content:
                chunks.append(
                    builder.build(
                        repository_id=self._repository_id,
                        file_path=parsed_file.path,
                        language=None,
                        content=content,
                        start_line=start_index + 1,
                        end_line=end_index,
                        chunk_type=ChunkType.CONFIG,
                    )
                )
        return chunks


class GenericTextChunkStrategy(ChunkStrategy):
    """Keep unsupported text as one semantic file-level chunk rather than token windows."""

    def __init__(self, repository_id: UUID) -> None:
        self._repository_id = repository_id

    def build_chunks(self, parsed_file: ParsedFile, builder: ChunkBuilder) -> list[Chunk]:
        content = (parsed_file.source or "").strip()
        if not content:
            return []
        return [
            builder.build(
                repository_id=self._repository_id,
                file_path=parsed_file.path,
                language=parsed_file.language,
                content=content,
                start_line=1,
                end_line=len(content.splitlines()),
                chunk_type=ChunkType.UNKNOWN,
                imports=parsed_file.imports,
                exports=parsed_file.exports,
            )
        ]


def strategy_for_file(parsed_file: ParsedFile, repository_id: UUID) -> ChunkStrategy:
    """Select a strategy from parser language and path without reopening source files."""
    if parsed_file.language is SupportedLanguage.PYTHON:
        return PythonChunkStrategy(repository_id)
    if parsed_file.language is SupportedLanguage.JAVASCRIPT:
        return JavaScriptChunkStrategy(repository_id)
    if parsed_file.language is SupportedLanguage.TYPESCRIPT:
        return TypeScriptChunkStrategy(repository_id)
    suffix = parsed_file.path.rsplit(".", 1)[-1].lower() if "." in parsed_file.path else ""
    if suffix in {"md", "mdx"}:
        return MarkdownChunkStrategy(repository_id)
    if suffix in {"yaml", "yml", "toml", "ini", "cfg", "json"}:
        return ConfigurationChunkStrategy(repository_id)
    return GenericTextChunkStrategy(repository_id)


def _line_range(lines: list[str], start_line: int, end_line: int) -> str:
    """Return a one-indexed inclusive source range from parser declaration coordinates."""
    return "\n".join(lines[start_line - 1 : end_line])
