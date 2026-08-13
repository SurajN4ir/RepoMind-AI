"""Pydantic serialization contracts for generated orchestrator responses."""

from typing import Any

from pydantic import BaseModel, Field

from app.modules.orchestrator.models import GeneratedResponse, ResponsePlan


class ResponsePlanResponse(BaseModel):
    intent: str
    tools: list[str]
    strategy: str
    temperature: float = Field(ge=0, le=2)
    streaming: bool
    verification: bool

    @classmethod
    def from_domain(cls, plan: ResponsePlan) -> "ResponsePlanResponse":
        return cls(
            intent=plan.intent.value,
            tools=list(plan.tools),
            strategy=plan.strategy,
            temperature=plan.temperature,
            streaming=plan.streaming,
            verification=plan.verification,
        )


class GeneratedResponseResponse(BaseModel):
    text: str
    citations: list[str]
    reasoning_metadata: dict[str, Any]
    tool_count: int = Field(ge=0)
    verification_passed: bool

    @classmethod
    def from_domain(cls, response: GeneratedResponse) -> "GeneratedResponseResponse":
        statistics = response.statistics
        return cls(
            text=response.text,
            citations=[citation.chunk_id for citation in response.citations],
            reasoning_metadata=dict(response.reasoning_metadata),
            tool_count=statistics.tool_count if statistics is not None else 0,
            verification_passed=statistics.verification_passed if statistics is not None else False,
        )
