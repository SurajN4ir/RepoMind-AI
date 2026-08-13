"""Extensible tool registry for orchestration-only capabilities."""

from collections.abc import Iterable
from typing import Protocol

from app.modules.context_builder.models import LLMContext
from app.modules.orchestrator.models import ResponsePlan, ToolOutput


class OrchestrationTool(Protocol):
    """A named optional capability selected by a `ResponsePlan`."""

    @property
    def name(self) -> str:
        """Return the stable name used in response plans."""

    async def execute(self, context: LLMContext, plan: ResponsePlan) -> ToolOutput:
        """Execute this capability against prepared evidence only."""


class ToolRegistry:
    """Resolve plan tool names to registered tool implementations."""

    def __init__(self, tools: Iterable[OrchestrationTool] = ()) -> None:
        self._tools = {tool.name: tool for tool in tools}

    def select(self, plan: ResponsePlan) -> tuple[OrchestrationTool, ...]:
        """Return registered tools requested by the plan, preserving plan order."""
        return tuple(self._tools[name] for name in plan.tools if name in self._tools)
