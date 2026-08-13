from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from app.modules.chunker.models import ChunkCollection
from app.modules.context_builder.models import LLMContext
from app.modules.conversation.models import MessageRecord
from app.modules.embedding.models import EmbeddingCollection
from app.modules.indexing.models import RepositoryIndex
from app.modules.ingestion.manifest import RepositoryManifest
from app.modules.orchestrator.models import GeneratedResponse
from app.modules.parser.models import ParsedRepository
from app.modules.query_engine.models import QueryPlan, UserRequest
from app.modules.repository.models import Repository
from app.modules.retrieval.models import RetrievedContext


@dataclass
class PipelineContext:
    """Write-audit context passed through pipeline steps.

    Each step reads previous outputs from *self* and writes its own output
    back, so the final result object can be assembled from accumulated state.
    """

    repository_id: UUID
    repository: Repository | None = None

    workspace: str | None = None
    manifest: RepositoryManifest | None = None
    parsed_repository: ParsedRepository | None = None
    chunks: ChunkCollection | None = None
    embedding_collection: EmbeddingCollection | None = None
    repository_index: RepositoryIndex | None = None

    started_at: datetime | None = None
    finished_at: datetime | None = None

    errors: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RepositoryIndexingResult:
    """Outcome of a single repository indexing pipeline invocation."""

    repository_id: UUID
    success: bool
    manifest: RepositoryManifest | None
    parsed_repository: ParsedRepository | None
    chunks: ChunkCollection | None
    embedding_collection: EmbeddingCollection | None
    repository_index: RepositoryIndex | None
    elapsed_seconds: float
    errors: tuple[str, ...]


@dataclass
class QueryPipelineContext:
    """Read-audit context passed through query pipeline steps.

    Each step reads previous outputs from *self* and writes its own output
    back, so the final result object can be assembled from accumulated state.
    """

    request: UserRequest
    plan: QueryPlan | None = None
    retrieved_context: RetrievedContext | None = None
    retrieval_results: list[RetrievedContext] = field(default_factory=list)
    llm_context: LLMContext | None = None
    response: GeneratedResponse | None = None
    conversation_id: UUID | None = None
    conversation_messages: list[MessageRecord] = field(default_factory=list)
    started_at: datetime | None = None
    finished_at: datetime | None = None
    errors: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class QueryResult:
    """Outcome of a single query pipeline invocation."""

    request: UserRequest
    success: bool
    response: GeneratedResponse | None
    plan: QueryPlan | None
    retrieved_context: RetrievedContext | None
    llm_context: LLMContext | None
    elapsed_seconds: float
    errors: tuple[str, ...]
