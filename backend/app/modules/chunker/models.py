"""Pure semantic chunking domain models with no persistence concerns."""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from app.modules.parser.language import SupportedLanguage
from app.modules.parser.models import SymbolKind
from app.shared.clock.utc import utc_now


class ChunkType(StrEnum):
    """The semantic boundary represented by a chunk."""

    FUNCTION = "function"
    CLASS = "class"
    METHOD = "method"
    MODULE = "module"
    IMPORTS = "imports"
    README_SECTION = "readme_section"
    CONFIG = "config"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class Chunk:
    """A transient, semantically bounded unit of repository source text."""

    id: str
    repository_id: UUID
    file_path: str
    language: SupportedLanguage | None
    symbol_name: str | None
    qualified_symbol_name: str | None
    symbol_kind: SymbolKind | None
    content: str
    start_line: int
    end_line: int
    token_count: int
    chunk_type: ChunkType
    metadata: Mapping[str, object]


@dataclass(frozen=True, slots=True)
class ChunkStatistics:
    """Aggregate metrics describing a collection of semantic chunks."""

    total_chunks: int
    average_tokens: float
    largest_chunk: int
    smallest_chunk: int
    languages: Mapping[str, int]


@dataclass(frozen=True, slots=True)
class ChunkCollection:
    """Versioned transient output of semantic chunking for one repository."""

    repository_id: UUID
    version: int
    created_at: datetime
    chunks: tuple[Chunk, ...]
    statistics: ChunkStatistics

    @classmethod
    def create(cls, repository_id: UUID, chunks: tuple[Chunk, ...]) -> "ChunkCollection":
        """Construct a collection and aggregate its deterministic chunk metadata."""
        token_counts = [chunk.token_count for chunk in chunks]
        languages: dict[str, int] = {}
        for chunk in chunks:
            key = chunk.language.value if chunk.language else "unknown"
            languages[key] = languages.get(key, 0) + 1
        return cls(
            repository_id=repository_id,
            version=1,
            created_at=utc_now(),
            chunks=chunks,
            statistics=ChunkStatistics(
                total_chunks=len(chunks),
                average_tokens=sum(token_counts) / len(token_counts) if token_counts else 0.0,
                largest_chunk=max(token_counts, default=0),
                smallest_chunk=min(token_counts, default=0),
                languages=languages,
            ),
        )
