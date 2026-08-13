"""Pure domain models for LLM-neutral evidence context."""

from collections.abc import Mapping
from dataclasses import dataclass

from app.modules.retrieval.models import Citation, SearchQuery


@dataclass(frozen=True, slots=True)
class EvidenceChunk:
    """One retained retrieval result enriched for evidence consumption."""

    chunk_id: str
    text: str
    metadata: Mapping[str, object]
    citation: Citation
    token_count: int
    priority: float


@dataclass(frozen=True, slots=True)
class EvidenceSection:
    """A coherent collection of evidence, usually from one source file."""

    title: str
    chunks: tuple[EvidenceChunk, ...]
    summary: str | None = None


@dataclass(frozen=True, slots=True)
class ContextStatistics:
    """Auditable measurements for a bounded evidence assembly operation."""

    input_chunk_count: int
    retained_chunk_count: int
    pruned_chunk_count: int
    section_count: int
    token_count: int
    token_budget: int


@dataclass(frozen=True, slots=True)
class LLMContext:
    """Structured, bounded evidence that any future reasoning system may consume."""

    query: SearchQuery
    sections: tuple[EvidenceSection, ...]
    citations: tuple[Citation, ...]
    statistics: ContextStatistics
    formatted_text: str
    conversation_history: str = ""
    repository_structure: str = ""
    convention_examples: str = ""
