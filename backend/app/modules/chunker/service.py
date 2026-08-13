"""Semantic chunking orchestration over parser-produced domain models."""

import structlog

from app.modules.chunker.builders import ChunkBuilder
from app.modules.chunker.models import Chunk, ChunkCollection
from app.modules.chunker.strategy import strategy_for_file
from app.modules.chunker.tokenizer import EstimatingTokenizer, Tokenizer
from app.modules.parser.models import ParsedRepository

logger = structlog.get_logger(__name__)


class SemanticChunkerService:
    """Orchestrate language-aware semantic strategies without opening repository files."""

    def __init__(self, tokenizer: Tokenizer | None = None) -> None:
        self._builder = ChunkBuilder(tokenizer or EstimatingTokenizer())

    def chunk(self, parsed_repository: ParsedRepository) -> ChunkCollection:
        """Build deterministically ordered semantic chunks from parser domain output only."""
        chunks: list[Chunk] = []
        for parsed_file in parsed_repository.files:
            strategy = strategy_for_file(parsed_file, parsed_repository.repository_id)
            chunks.extend(strategy.build_chunks(parsed_file, self._builder))
        ordered_chunks = tuple(
            sorted(
                chunks,
                key=lambda chunk: (
                    chunk.file_path,
                    chunk.start_line,
                    chunk.end_line,
                    chunk.chunk_type.value,
                    chunk.id,
                ),
            )
        )
        collection = ChunkCollection.create(parsed_repository.repository_id, ordered_chunks)
        logger.info(
            "semantic_chunks_created",
            repository_id=str(parsed_repository.repository_id),
            total_chunks=collection.statistics.total_chunks,
        )
        return collection
