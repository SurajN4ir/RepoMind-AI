"""Pure domain models for AI orchestration boundaries."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum

from app.modules.retrieval.models import Citation


class ResponseIntent(StrEnum):
    """Kinds of response an orchestration policy may request."""

    ANSWER = "ANSWER"
    SUMMARY = "SUMMARY"
    EXPLAIN = "EXPLAIN"
    GENERATE = "GENERATE"
    COMPARE = "COMPARE"
    TRACE = "TRACE"
    REFACTOR = "REFACTOR"


@dataclass(frozen=True, slots=True)
class ResponsePlan:
    """A response-execution decision independent from any workflow engine."""

    intent: ResponseIntent
    tools: tuple[str, ...]
    strategy: str
    temperature: float
    streaming: bool
    verification: bool

    def __post_init__(self) -> None:
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("Response temperature must be between 0 and 2.")


@dataclass(frozen=True, slots=True)
class ToolOutput:
    """Opaque, named result returned by an orchestration tool."""

    tool_name: str
    data: Mapping[str, object]


@dataclass(frozen=True, slots=True)
class ResponseStatistics:
    """Observability data for one completed orchestration request."""

    tool_count: int
    successful_tool_count: int
    elapsed_seconds: float
    streamed: bool
    verification_passed: bool


@dataclass(frozen=True, slots=True)
class GeneratedResponse:
    """User-visible generated content with citations and safe execution metadata."""

    text: str
    citations: tuple[Citation, ...]
    reasoning_metadata: Mapping[str, object] = field(default_factory=dict)
    statistics: ResponseStatistics | None = None


class StreamEventType(StrEnum):
    """Lifecycle events emitted by a response stream."""

    START = "START"
    TEXT = "TEXT"
    END = "END"


@dataclass(frozen=True, slots=True)
class StreamEvent:
    """One transport-neutral event in a generated-response stream."""

    type: StreamEventType
    text: str = ""
    response: GeneratedResponse | None = None
