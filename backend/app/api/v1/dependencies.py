"""FastAPI dependency providers that wire application services for route handlers."""

from collections.abc import Sequence
from functools import lru_cache
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.exceptions import ApplicationError
from app.application.http_exceptions import to_http_exception
from app.application.pipelines.repository_indexing_pipeline import (
    RepositoryIndexingPipeline,
)
from app.application.pipelines.repository_query_pipeline import (
    RepositoryQueryPipeline,
)
from app.application.services.repository import RepositoryApplicationService
from app.config.settings import get_settings
from app.modules.auth.exceptions import AuthenticationError
from app.modules.auth.models import AuthenticatedUser
from app.modules.auth.verifier import ClerkTokenVerifier, extract_bearer_token
from app.modules.chunker.service import SemanticChunkerService
from app.modules.context_builder.service import ContextBuilderService
from app.modules.conversation.store import ConversationStore
from app.modules.embedding.provider import OllamaEmbeddingProvider
from app.modules.embedding.service import EmbeddingService
from app.modules.indexing.db_repository import DbIndexStore
from app.modules.indexing.repository import (
    ActivityRepository,
    DependencyRepository,
    FileContentRepository,
)
from app.modules.indexing.service import IndexingService
from app.modules.ingestion.filters import IngestionFilterConfig, RepositoryFileFilter
from app.modules.ingestion.git import GitClient
from app.modules.ingestion.walker import RepositoryWalker
from app.modules.orchestrator.execution import DefaultWorkflowEngine
from app.modules.orchestrator.ollama_provider import OllamaResponseGenerator
from app.modules.orchestrator.service import OrchestratorService
from app.modules.parser.service import SemanticParserService
from app.modules.query_engine.models import RepositoryReference
from app.modules.query_engine.service import QueryEngineService
from app.modules.repository.models import Repository
from app.modules.repository.repository import RepositoryRepository
from app.modules.repository.service import RepositoryService
from app.modules.retrieval.db_repository import DbSearchStore
from app.modules.retrieval.pgvector_repository import PgVectorSearchStore
from app.modules.retrieval.repository import VectorSearchRepository
from app.modules.retrieval.service import RetrievalService
from app.shared.database.session import get_db_session, get_secondary_db_session


@lru_cache
def get_token_verifier() -> ClerkTokenVerifier:
    """Return a process-wide cached Clerk token verifier."""
    settings = get_settings()
    if not settings.clerk_jwks_url:
        raise RuntimeError("CLERK_JWKS_URL is not configured.")
    return ClerkTokenVerifier(jwks_url=settings.clerk_jwks_url, issuer=settings.clerk_issuer)


async def get_current_user(
    verifier: Annotated[ClerkTokenVerifier, Depends(get_token_verifier)],
    authorization: Annotated[str | None, Header()] = None,
) -> AuthenticatedUser:
    """Verify the caller's bearer token and return their identity, or raise 401.

    Takes the verifier via Depends() (not a bare call) so tests can override
    get_token_verifier and exercise this function's real header-parsing and
    error-mapping logic without needing a reachable Clerk instance.
    """
    try:
        token = extract_bearer_token(authorization)
        return verifier.verify(token)
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


CurrentUserDependency = Annotated[AuthenticatedUser, Depends(get_current_user)]


async def get_repository_app_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> RepositoryApplicationService:
    """Construct a request-scoped repository application service."""
    domain = RepositoryService(session, RepositoryRepository(session))
    return RepositoryApplicationService(domain)


RepositoryAppServiceDependency = Annotated[
    RepositoryApplicationService, Depends(get_repository_app_service)
]


async def get_authorized_repository(
    repository_id: UUID,
    current_user: CurrentUserDependency,
    service: RepositoryAppServiceDependency,
) -> Repository:
    """Fetch a path-addressed repository, enforcing that the caller owns it.

    Use this (even without binding its return value) on every route that
    takes a repository_id path parameter, so indexing/query/search/file
    access all require the same ownership check as the CRUD routes.

    Converts ApplicationError to HTTPException itself: dependencies run
    outside route-body try/except blocks, and the app's only registered
    exception handler is a generic catch-all that would otherwise turn a
    routine "not found" into a 500.
    """
    try:
        return await service.get(repository_id, current_user.user_id)
    except ApplicationError as exc:
        raise to_http_exception(exc) from exc


AuthorizedRepositoryDependency = Annotated[Repository, Depends(get_authorized_repository)]


async def get_indexing_pipeline(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> RepositoryIndexingPipeline:
    """Construct a request-scoped indexing pipeline with all domain services.

    The canonical repository indexing/ingestion path: clone, walk, parse,
    chunk, embed via Ollama, and index into PostgreSQL/pgvector (or SQLite
    for local dev) through ``DbIndexStore``. ``POST .../ingest`` (legacy)
    also depends on this pipeline rather than its own implementation -- see
    docs/adr/0015-legacy-ingestion-endpoint-delegates-to-indexing-pipeline.md.
    """
    settings = get_settings()
    repository_domain = RepositoryService(session, RepositoryRepository(session))
    repository_service = RepositoryApplicationService(repository_domain)
    file_filter = RepositoryFileFilter(
        IngestionFilterConfig(max_file_size_bytes=settings.ingestion_max_file_size_bytes)
    )
    walker = RepositoryWalker(file_filter)
    index_store = DbIndexStore(session)
    return RepositoryIndexingPipeline(
        repository_service=repository_service,
        git_client=GitClient(settings.git_executable),
        walker=walker,
        parser=SemanticParserService(),
        chunker=SemanticChunkerService(),
        embedding_service=EmbeddingService(
            OllamaEmbeddingProvider(
                model_name=settings.embedding_model,
                base_url=settings.embedding_base_url,
            )
        ),
        indexing_service=IndexingService(index_store, index_store, index_store, index_store),
        file_content_store=index_store,
        dependency_store=index_store,
        activity_store=index_store,
    )


IndexingPipelineDependency = Annotated[RepositoryIndexingPipeline, Depends(get_indexing_pipeline)]


class _RepositoryResolverAdapter:
    """Adapts RepositoryApplicationService to the query engine's RepositoryResolver protocol.

    Scoped to one owner so that resolving a repository by name during query
    planning can never surface another user's repository names or ids.
    """

    def __init__(self, service: RepositoryApplicationService, owner_id: str) -> None:
        self._service = service
        self._owner_id = owner_id

    async def list_repositories(self) -> Sequence[RepositoryReference]:
        from app.shared.database.pagination import PaginationParams

        page = await self._service.list(PaginationParams(page=1, page_size=100), self._owner_id)
        return [RepositoryReference(id=repo.id, name=repo.name) for repo in page.items]


async def get_query_pipeline(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    keyword_session: Annotated[AsyncSession, Depends(get_secondary_db_session)],
    current_user: CurrentUserDependency,
) -> RepositoryQueryPipeline:
    """Construct a request-scoped query pipeline with all domain services.

    Embeds via Ollama (falling back to a local Ollama instance at
    http://localhost:11434).

    RetrievalService runs the vector and keyword read ports concurrently via
    asyncio.gather, and SQLAlchemy's AsyncSession is not safe for concurrent
    use by two coroutines. The keyword/metadata store therefore gets its own
    session (``keyword_session``); the vector store uses the primary
    ``session``, matching every other service built here.
    """
    settings = get_settings()
    repository_domain = RepositoryService(session, RepositoryRepository(session))
    repository_service = RepositoryApplicationService(repository_domain)

    resolver = _RepositoryResolverAdapter(repository_service, current_user.user_id)
    query_engine = QueryEngineService(resolver)

    keyword_store = DbSearchStore(keyword_session)
    vector_store: VectorSearchRepository = (
        PgVectorSearchStore(session)
        if settings.database_url.startswith("postgresql")
        else DbSearchStore(session)
    )
    retrieval = RetrievalService(
        OllamaEmbeddingProvider(
            model_name=settings.embedding_model,
            base_url=settings.embedding_base_url,
        ),
        vector_store,
        keyword_store,
        keyword_store,
    )

    index_store = DbIndexStore(session)
    context_builder = ContextBuilderService()
    workflow_engine = DefaultWorkflowEngine(
        OllamaResponseGenerator(
            model_name=settings.generation_model,
            base_url=settings.generation_base_url,
        )
    )
    orchestrator = OrchestratorService(workflow_engine)
    conversation_store = ConversationStore(session)

    return RepositoryQueryPipeline(
        query_engine=query_engine,
        retrieval_service=retrieval,
        context_builder=context_builder,
        orchestrator=orchestrator,
        dependency_store=index_store,
        file_content_store=index_store,
        conversation_store=conversation_store,
    )


QueryPipelineDependency = Annotated[RepositoryQueryPipeline, Depends(get_query_pipeline)]


async def get_file_content_store(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> FileContentRepository:
    """Construct a request-scoped file content store."""
    return DbIndexStore(session)


FileContentStoreDependency = Annotated[FileContentRepository, Depends(get_file_content_store)]


async def get_dependency_store(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> DependencyRepository:
    """Construct a request-scoped dependency store."""
    return DbIndexStore(session)


DependencyStoreDependency = Annotated[DependencyRepository, Depends(get_dependency_store)]


async def get_activity_store(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ActivityRepository:
    """Construct a request-scoped activity event store."""
    return DbIndexStore(session)


ActivityStoreDependency = Annotated[ActivityRepository, Depends(get_activity_store)]
