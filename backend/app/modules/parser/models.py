"""Pure language-agnostic semantic parser domain models."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from app.modules.parser.language import SupportedLanguage
from app.shared.clock.utc import utc_now


class SymbolKind(StrEnum):
    """Language-agnostic kinds of declared symbols."""

    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"


@dataclass(frozen=True, slots=True)
class ParsedSymbol:
    """A declared class, function, or method extracted from a source file."""

    name: str
    kind: SymbolKind
    start_line: int
    end_line: int
    signature: str | None
    parent_name: str | None = None
    docstring: str | None = None


@dataclass(frozen=True, slots=True)
class ImportReference:
    """A language-native import statement retained as language-agnostic text."""

    statement: str
    start_line: int


@dataclass(frozen=True, slots=True)
class ExportReference:
    """A language-native export declaration retained as language-agnostic text."""

    statement: str
    start_line: int


@dataclass(frozen=True, slots=True)
class ParsedFile:
    """Semantic metadata and parse outcome for one manifest file."""

    path: str
    language: SupportedLanguage | None
    symbols: tuple[ParsedSymbol, ...]
    imports: tuple[ImportReference, ...]
    exports: tuple[ExportReference, ...]
    docstrings: tuple[str, ...]
    comments: tuple[str, ...]
    parse_error: str | None
    source: str | None = field(default=None, repr=False, compare=False)
    ast: Any | None = field(default=None, repr=False, compare=False)


@dataclass(frozen=True, slots=True)
class ParsedRepositoryStats:
    """Aggregate parsing outcomes for one repository manifest."""

    total_files: int
    supported_files: int
    parsed_files: int
    failed_files: int
    total_symbols: int


@dataclass(frozen=True, slots=True)
class ParsedRepository:
    """Non-persistent semantic representation of a repository manifest."""

    repository_id: UUID
    parsed_at: datetime
    files: tuple[ParsedFile, ...]
    stats: ParsedRepositoryStats

    @classmethod
    def create(cls, repository_id: UUID, files: tuple[ParsedFile, ...]) -> "ParsedRepository":
        """Build a parsed repository and aggregate its outcomes with the shared UTC clock."""
        supported_files = sum(file.language is not None for file in files)
        parsed_files = sum(file.language is not None and file.parse_error is None for file in files)
        failed_files = sum(file.parse_error is not None for file in files)
        total_symbols = sum(len(file.symbols) for file in files)
        return cls(
            repository_id=repository_id,
            parsed_at=utc_now(),
            files=files,
            stats=ParsedRepositoryStats(
                total_files=len(files),
                supported_files=supported_files,
                parsed_files=parsed_files,
                failed_files=failed_files,
                total_symbols=total_symbols,
            ),
        )
