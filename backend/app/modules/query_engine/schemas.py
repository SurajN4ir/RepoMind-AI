"""Pydantic serialization contracts for Query Engine callers."""

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.query_engine.models import QueryPlan, UserRequest


class UserRequestSchema(BaseModel):
    """Transport representation of a request awaiting query planning."""

    text: str = Field(min_length=1)
    repository_id: UUID | None = None
    conversation_id: UUID | None = None
    preferences: dict[str, Any] = Field(default_factory=dict)

    def to_domain(self) -> UserRequest:
        """Convert the transport contract to its pure domain equivalent."""
        return UserRequest(self.text, self.repository_id, self.conversation_id, self.preferences)


class RetrievalStepResponse(BaseModel):
    """Serializable retrieval operation within a query plan."""

    source: str
    query: str
    limit: int
    filters: dict[str, Any]


class QueryPlanResponse(BaseModel):
    """Serializable plan; deliberately contains no retrieved context."""

    intent: str
    text: str
    repository_id: UUID | None
    filters: dict[str, Any]
    limit: int
    offset: int
    confidence: float
    warnings: list[str]
    retrieval_steps: list[RetrievalStepResponse] = Field(default_factory=list)

    @classmethod
    def from_domain(cls, plan: QueryPlan) -> "QueryPlanResponse":
        """Serialize a plan without calling Retrieval or an LLM."""
        return cls(
            intent=plan.intent.value,
            text=plan.search_query.text,
            repository_id=plan.search_query.repository_id,
            filters=dict(plan.search_query.filters),
            limit=plan.search_query.limit,
            offset=plan.search_query.offset,
            confidence=plan.confidence,
            warnings=list(plan.warnings),
            retrieval_steps=[
                RetrievalStepResponse(
                    source=step.source,
                    query=step.query,
                    limit=step.limit,
                    filters=dict(step.filters),
                )
                for step in plan.retrieval_steps
            ],
        )
