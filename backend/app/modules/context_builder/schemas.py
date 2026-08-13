"""Pydantic serialization contracts for constructed evidence context."""

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.context_builder.models import LLMContext


class EvidenceChunkResponse(BaseModel):
    chunk_id: str
    text: str
    metadata: dict[str, Any]
    token_count: int = Field(ge=0)
    priority: float


class EvidenceSectionResponse(BaseModel):
    title: str
    chunks: list[EvidenceChunkResponse]
    summary: str | None


class ContextStatisticsResponse(BaseModel):
    input_chunk_count: int = Field(ge=0)
    retained_chunk_count: int = Field(ge=0)
    pruned_chunk_count: int = Field(ge=0)
    section_count: int = Field(ge=0)
    token_count: int = Field(ge=0)
    token_budget: int = Field(gt=0)


class LLMContextResponse(BaseModel):
    query_text: str
    repository_id: UUID | None
    sections: list[EvidenceSectionResponse]
    formatted_text: str
    statistics: ContextStatisticsResponse

    @classmethod
    def from_domain(cls, context: LLMContext) -> "LLMContextResponse":
        """Serialize structured evidence without triggering response generation."""
        return cls(
            query_text=context.query.text,
            repository_id=context.query.repository_id,
            sections=[
                EvidenceSectionResponse(
                    title=section.title,
                    summary=section.summary,
                    chunks=[
                        EvidenceChunkResponse(
                            chunk_id=chunk.chunk_id,
                            text=chunk.text,
                            metadata=dict(chunk.metadata),
                            token_count=chunk.token_count,
                            priority=chunk.priority,
                        )
                        for chunk in section.chunks
                    ],
                )
                for section in context.sections
            ],
            formatted_text=context.formatted_text,
            statistics=ContextStatisticsResponse(
                input_chunk_count=context.statistics.input_chunk_count,
                retained_chunk_count=context.statistics.retained_chunk_count,
                pruned_chunk_count=context.statistics.pruned_chunk_count,
                section_count=context.statistics.section_count,
                token_count=context.statistics.token_count,
                token_budget=context.statistics.token_budget,
            ),
        )
