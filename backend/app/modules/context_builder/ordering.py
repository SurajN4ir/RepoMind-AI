"""Stable coherent ordering for already selected evidence."""

from app.modules.context_builder.models import EvidenceChunk


class EvidenceOrderer:
    """Order by source location first while preserving retrieval priority across files."""

    def order(self, chunks: tuple[EvidenceChunk, ...]) -> tuple[EvidenceChunk, ...]:
        """Sort deterministically by file priority, then source line and chunk ID."""
        file_priority: dict[str, float] = {}
        for chunk in chunks:
            path = chunk.citation.file_path or "Unknown source"
            file_priority[path] = max(file_priority.get(path, float("-inf")), chunk.priority)
        return tuple(
            sorted(
                chunks,
                key=lambda chunk: (
                    -file_priority[chunk.citation.file_path or "Unknown source"],
                    chunk.citation.file_path or "Unknown source",
                    chunk.citation.line_start if chunk.citation.line_start is not None else -1,
                    -chunk.priority,
                    chunk.chunk_id,
                ),
            )
        )
