"""Async unit tests for provider-neutral response orchestration."""

import pytest

from app.modules.context_builder.models import ContextStatistics, EvidenceSection, LLMContext
from app.modules.orchestrator.exceptions import ResponseVerificationError
from app.modules.orchestrator.execution import DefaultWorkflowEngine
from app.modules.orchestrator.models import ResponseIntent, ToolOutput
from app.modules.orchestrator.service import OrchestratorService
from app.modules.orchestrator.tools import ToolRegistry
from app.modules.orchestrator.verification import ResponseVerifier
from app.modules.retrieval.models import Citation, SearchQuery


def _context(query: str = "Explain authentication") -> LLMContext:
    citation = Citation("auth", "src/auth.py", "validate_token", 4, 9)
    return LLMContext(
        query=SearchQuery(query),
        sections=(EvidenceSection("File: src/auth.py", ()),),
        citations=(citation,),
        statistics=ContextStatistics(1, 1, 0, 1, 5, 100),
        formatted_text="File: src/auth.py\nSymbol: validate_token",
    )


class _Generator:
    async def generate(self, context: LLMContext, plan: object, tool_outputs: object) -> str:
        return "Authentication is validated by validate_token."


class _ArchitectureTool:
    name = "architecture"

    async def execute(self, context: LLMContext, plan: object) -> ToolOutput:
        return ToolOutput(self.name, {"diagram": "auth flow"})


class _FailingTool:
    name = "architecture"

    async def execute(self, context: LLMContext, plan: object) -> ToolOutput:
        raise RuntimeError("unavailable")


class _FailingVerifier(ResponseVerifier):
    async def verify(self, response: object, context: LLMContext) -> bool:
        return False


def _service(
    *, registry: ToolRegistry | None = None, verifier: ResponseVerifier | None = None
) -> OrchestratorService:
    return OrchestratorService(
        DefaultWorkflowEngine(_Generator()),
        tool_registry=registry,
        verifier=verifier,
    )


@pytest.mark.asyncio
async def test_orchestrator_plans_executes_tools_and_preserves_citations() -> None:
    response = await _service(registry=ToolRegistry((_ArchitectureTool(),))).respond(
        _context("Trace auth flow")
    )
    assert response.reasoning_metadata["response_intent"] == ResponseIntent.TRACE.value
    assert response.reasoning_metadata["executed_tools"] == ("architecture",)
    assert response.citations[0].chunk_id == "auth"
    assert response.statistics is not None and response.statistics.verification_passed


@pytest.mark.asyncio
async def test_orchestrator_recovers_when_optional_tool_fails() -> None:
    response = await _service(registry=ToolRegistry((_FailingTool(),))).respond(
        _context("Trace auth flow")
    )
    assert response.statistics is not None
    assert response.statistics.tool_count == 1
    assert response.statistics.successful_tool_count == 0


@pytest.mark.asyncio
async def test_orchestrator_exposes_streaming_lifecycle() -> None:
    events = [event async for event in _service().stream(_context())]
    assert events[0].type.value == "START"
    assert any(event.type.value == "TEXT" for event in events)
    assert events[-1].type.value == "END"
    assert events[-1].response is not None


@pytest.mark.asyncio
async def test_orchestrator_surfaces_verification_failure() -> None:
    with pytest.raises(ResponseVerificationError):
        await _service(verifier=_FailingVerifier()).respond(_context())
