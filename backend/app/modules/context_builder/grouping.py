"""Grouping policy for coherent evidence sections."""

from collections import OrderedDict

from app.modules.context_builder.models import EvidenceChunk, EvidenceSection


class EvidenceGrouper:
    """Group evidence by file to retain nearby symbols and source context."""

    def group(self, chunks: tuple[EvidenceChunk, ...]) -> tuple[EvidenceSection, ...]:
        """Create stable file sections from ordered evidence."""
        grouped: OrderedDict[str, list[EvidenceChunk]] = OrderedDict()
        for chunk in chunks:
            path = chunk.citation.file_path or "Unknown source"
            grouped.setdefault(path, []).append(chunk)
        return tuple(
            EvidenceSection(title=f"File: {path}", chunks=tuple(section_chunks))
            for path, section_chunks in grouped.items()
        )
