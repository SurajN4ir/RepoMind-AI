"""Pure domain models for request understanding and retrieval planning."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from uuid import UUID

from app.modules.retrieval.models import SearchQuery


class QueryIntent(StrEnum):
    """User intent categories that influence a retrieval plan."""

    SEARCH_CODE = "SEARCH_CODE"
    SEARCH_SYMBOL = "SEARCH_SYMBOL"
    SEARCH_FILE = "SEARCH_FILE"
    SEARCH_DOCUMENTATION = "SEARCH_DOCUMENTATION"
    SEARCH_CONFIGURATION = "SEARCH_CONFIGURATION"
    SEARCH_ARCHITECTURE = "SEARCH_ARCHITECTURE"
    EXPLAIN = "EXPLAIN"
    TRACE = "TRACE"
    GENERATE = "GENERATE"
    REFACTOR = "REFACTOR"


@dataclass(frozen=True, slots=True)
class UserRequest:
    """An unplanned request supplied by a caller or future conversation layer."""

    text: str
    repository_id: UUID | None = None
    conversation_id: UUID | None = None
    preferences: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class RepositoryReference:
    """Minimal repository identity needed to decide a search scope."""

    id: UUID
    name: str


@dataclass(frozen=True, slots=True)
class RetrievalStep:
    """One retrieval operation in a multi-step query plan.

    ``source`` describes the kind of information needed (e.g. ``"code_search"``
    for relevant code chunks, ``"related_files"`` for dependency-linked files,
    ``"exact_file"`` for full file content). The orchestrator translates each
    source to the appropriate storage backend.
    """

    source: str
    query: str
    limit: int = 10
    filters: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class QueryPlan:
    """A validated, executable retrieval plan with no retrieval result attached."""

    intent: QueryIntent
    search_query: SearchQuery
    confidence: float
    warnings: tuple[str, ...] = ()
    retrieval_steps: tuple[RetrievalStep, ...] = ()

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Query plan confidence must be between 0 and 1.")
