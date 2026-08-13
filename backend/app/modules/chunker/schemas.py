"""Serialization contracts for transient semantic chunking output."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.chunker.models import ChunkCollection


class ChunkResponse(BaseModel):
    id: str
    repository_id: UUID
    file_path: str
    language: str | None
    symbol_name: str | None
    qualified_symbol_name: str | None
    symbol_kind: str | None
    content: str
    start_line: int = Field(ge=1)
    end_line: int = Field(ge=1)
    token_count: int = Field(ge=0)
    chunk_type: str
    metadata: dict[str, Any]


class ChunkStatisticsResponse(BaseModel):
    total_chunks: int = Field(ge=0)
    average_tokens: float = Field(ge=0)
    largest_chunk: int = Field(ge=0)
    smallest_chunk: int = Field(ge=0)
    languages: dict[str, int]


class ChunkCollectionResponse(BaseModel):
    repository_id: UUID
    version: int
    created_at: datetime
    chunks: list[ChunkResponse]
    statistics: ChunkStatisticsResponse

    @classmethod
    def from_domain(cls, collection: ChunkCollection) -> "ChunkCollectionResponse":
        """Serialize chunks while preserving metadata and deterministic identifiers."""
        return cls(
            repository_id=collection.repository_id,
            version=collection.version,
            created_at=collection.created_at,
            chunks=[
                ChunkResponse(
                    id=chunk.id,
                    repository_id=chunk.repository_id,
                    file_path=chunk.file_path,
                    language=chunk.language.value if chunk.language else None,
                    symbol_name=chunk.symbol_name,
                    qualified_symbol_name=chunk.qualified_symbol_name,
                    symbol_kind=chunk.symbol_kind.value if chunk.symbol_kind else None,
                    content=chunk.content,
                    start_line=chunk.start_line,
                    end_line=chunk.end_line,
                    token_count=chunk.token_count,
                    chunk_type=chunk.chunk_type.value,
                    metadata=dict(chunk.metadata),
                )
                for chunk in collection.chunks
            ],
            statistics=ChunkStatisticsResponse(
                total_chunks=collection.statistics.total_chunks,
                average_tokens=collection.statistics.average_tokens,
                largest_chunk=collection.statistics.largest_chunk,
                smallest_chunk=collection.statistics.smallest_chunk,
                languages=dict(collection.statistics.languages),
            ),
        )
