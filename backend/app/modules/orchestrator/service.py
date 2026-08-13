"""Application service composing response planning, workflow, verification, and streaming."""

from collections.abc import AsyncIterator

import structlog

from app.modules.context_builder.models import LLMContext
from app.modules.orchestrator.exceptions import ResponseVerificationError
from app.modules.orchestrator.execution import WorkflowEngine
from app.modules.orchestrator.models import GeneratedResponse, ResponseStatistics, StreamEvent
from app.modules.orchestrator.planner import ResponsePlanner, RuleBasedResponsePlanner
from app.modules.orchestrator.streaming import ResponseStreamer, WordResponseStreamer
from app.modules.orchestrator.tools import ToolRegistry
from app.modules.orchestrator.verification import CitationPreservationVerifier, ResponseVerifier


class OrchestratorService:
    """Create grounded responses without exposing workflow or generator implementations."""

    def __init__(
        self,
        workflow_engine: WorkflowEngine,
        *,
        planner: ResponsePlanner | None = None,
        tool_registry: ToolRegistry | None = None,
        verifier: ResponseVerifier | None = None,
        streamer: ResponseStreamer | None = None,
    ) -> None:
        self._workflow_engine = workflow_engine
        self._planner = planner or RuleBasedResponsePlanner()
        self._tool_registry = tool_registry or ToolRegistry()
        self._verifier = verifier or CitationPreservationVerifier()
        self._streamer = streamer or WordResponseStreamer()
        self._logger = structlog.get_logger(__name__)

    async def respond(self, context: LLMContext) -> GeneratedResponse:
        """Plan, execute, verify, and return a citation-preserving response."""
        plan = self._planner.plan(context)
        tools = self._tool_registry.select(plan)
        text, outputs, elapsed_seconds = await self._workflow_engine.execute(context, plan, tools)
        provisional = GeneratedResponse(
            text=text,
            citations=context.citations,
            reasoning_metadata={
                "response_intent": plan.intent.value,
                "strategy": plan.strategy,
                "executed_tools": tuple(output.tool_name for output in outputs),
            },
        )
        verification_passed = not plan.verification or await self._verifier.verify(
            provisional, context
        )
        if not verification_passed:
            raise ResponseVerificationError("Generated response did not pass verification.")
        response = GeneratedResponse(
            text=provisional.text,
            citations=provisional.citations,
            reasoning_metadata=provisional.reasoning_metadata,
            statistics=ResponseStatistics(
                tool_count=len(tools),
                successful_tool_count=len(outputs),
                elapsed_seconds=elapsed_seconds,
                streamed=plan.streaming,
                verification_passed=verification_passed,
            ),
        )
        self._logger.info(
            "response_generated",
            intent=plan.intent.value,
            tool_count=len(tools),
            citation_count=len(response.citations),
        )
        return response

    async def stream(self, context: LLMContext) -> AsyncIterator[StreamEvent]:
        """Generate a response, then expose it through the configured stream lifecycle."""
        response = await self.respond(context)
        async for event in self._streamer.stream(response):
            yield event
