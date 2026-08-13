"""Formatting policies for presenting structured evidence to later consumers."""

from typing import Protocol

from app.modules.context_builder.models import EvidenceSection


class ContextFormatter(Protocol):
    """Render evidence sections without knowing any prompt template or LLM."""

    def format(self, sections: tuple[EvidenceSection, ...]) -> str:
        """Return a stable textual representation of structured evidence."""


class SourceEvidenceFormatter:
    """Render source-oriented evidence with citation markers per chunk."""

    def format(self, sections: tuple[EvidenceSection, ...]) -> str:
        """Produce deterministic, human-readable evidence text with [citation:N] markers."""
        blocks: list[str] = []
        citation_index = 0
        for section in sections:
            chunks: list[str] = [section.title]
            for chunk in section.chunks:
                citation = chunk.citation
                location = _location(citation.line_start, citation.line_end)
                symbol = citation.qualified_symbol_name or "Unknown symbol"
                citation_index += 1
                chunks.append(
                    f"[citation:{citation_index}] Symbol: {symbol}\n"
                    f"Lines: {location}\n"
                    f"Code:\n{chunk.text}"
                )
            blocks.append("\n\n".join(chunks))
        return "\n\n---\n\n".join(blocks)


def _location(start: int | None, end: int | None) -> str:
    if start is None:
        return "Unknown"
    return str(start) if end in {None, start} else f"{start}-{end}"
