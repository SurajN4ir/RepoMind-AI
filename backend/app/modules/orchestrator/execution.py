"""Workflow-engine abstraction and a dependency-free default implementation."""

from time import perf_counter
from typing import Protocol

from app.modules.context_builder.models import LLMContext
from app.modules.orchestrator.exceptions import ResponseGenerationError, ToolExecutionError
from app.modules.orchestrator.models import ResponsePlan, ToolOutput
from app.modules.orchestrator.tools import OrchestrationTool


class ResponseGenerator(Protocol):
    """Provider boundary for an LLM or other response-generation implementation."""

    async def generate(
        self, context: LLMContext, plan: ResponsePlan, tool_outputs: tuple[ToolOutput, ...]
    ) -> str:
        """Generate visible response text from bounded evidence and tool outputs."""


class WorkflowEngine(Protocol):
    """Execute an orchestration workflow without exposing a graph framework."""

    async def execute(
        self,
        context: LLMContext,
        plan: ResponsePlan,
        tools: tuple[OrchestrationTool, ...],
    ) -> tuple[str, tuple[ToolOutput, ...], float]:
        """Run tools then generate text, returning elapsed workflow time."""


class DefaultWorkflowEngine:
    """Sequential workflow suitable until a graph engine adapter is configured."""

    def __init__(
        self, generator: ResponseGenerator, *, continue_on_tool_error: bool = True
    ) -> None:
        self._generator = generator
        self._continue_on_tool_error = continue_on_tool_error

    async def execute(
        self,
        context: LLMContext,
        plan: ResponsePlan,
        tools: tuple[OrchestrationTool, ...],
    ) -> tuple[str, tuple[ToolOutput, ...], float]:
        """Execute selected tools in order and delegate final text to the generator."""
        started_at = perf_counter()
        outputs: list[ToolOutput] = []
        for tool in tools:
            try:
                outputs.append(await tool.execute(context, plan))
            except Exception as exc:
                if self._continue_on_tool_error:
                    continue
                raise ToolExecutionError(f"Tool '{tool.name}' failed.") from exc
        try:
            text = await self._generator.generate(context, plan, tuple(outputs))
        except Exception as exc:
            raise ResponseGenerationError("Response generation failed.") from exc
        if not text.strip():
            raise ResponseGenerationError("Response generator returned empty text.")
        return text, tuple(outputs), perf_counter() - started_at
