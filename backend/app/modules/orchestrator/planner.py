"""Replaceable response planning from already constructed evidence."""

from typing import Protocol

from app.modules.context_builder.models import LLMContext
from app.modules.orchestrator.models import ResponseIntent, ResponsePlan


class ResponsePlanner(Protocol):
    """Select response behavior without coupling callers to a model or graph."""

    def plan(self, context: LLMContext) -> ResponsePlan:
        """Create a response plan from the query and prepared evidence."""


class RuleBasedResponsePlanner:
    """Transparent initial policy for deterministic response planning."""

    def plan(self, context: LLMContext) -> ResponsePlan:
        """Infer response intent from request language and evidence availability."""
        text = context.query.text.casefold()
        intent = _intent(text)
        tools = _tools(intent)
        return ResponsePlan(
            intent=intent,
            tools=tools,
            strategy="evidence_grounded",
            temperature=0.2 if intent is not ResponseIntent.GENERATE else 0.5,
            streaming=True,
            verification=True,
        )


def _intent(text: str) -> ResponseIntent:
    if any(term in text for term in ("summarize", "summary")):
        return ResponseIntent.SUMMARY
    if any(term in text for term in ("explain", "what does", "how does")):
        return ResponseIntent.EXPLAIN
    if any(term in text for term in ("generate", "write documentation", "document")):
        return ResponseIntent.GENERATE
    if any(term in text for term in ("compare", "difference")):
        return ResponseIntent.COMPARE
    if any(term in text for term in ("trace", "flow", "call path")):
        return ResponseIntent.TRACE
    if any(term in text for term in ("refactor", "improve")):
        return ResponseIntent.REFACTOR
    return ResponseIntent.ANSWER


def _tools(intent: ResponseIntent) -> tuple[str, ...]:
    if intent is ResponseIntent.TRACE:
        return ("architecture",)
    if intent is ResponseIntent.GENERATE:
        return ("documentation",)
    return ()
