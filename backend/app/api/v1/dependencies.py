"""FastAPI dependency providers that wire application services for route handlers."""

from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.pipelines.repository_indexing_pipeline import (
    RepositoryIndexingPipeline,
)
from app.application.pipelines.repository_query_pipeline import (
    RepositoryQueryPipeline,
)
from app.application.services.ingestion import IngestionApplicationService
from app.application.services.repository import RepositoryApplicationService
from app.config.settings import get_settings
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
from app.modules.ingestion.service import IngestionService
from app.modules.ingestion.walker import RepositoryWalker
from app.modules.orchestrator.execution import DefaultWorkflowEngine
from app.modules.orchestrator.ollama_provider import OllamaResponseGenerator
from app.modules.orchestrator.service import OrchestratorService
from app.modules.parser.service import SemanticParserService
from app.modules.query_engine.models import RepositoryReference
from app.modules.query_engine.service import QueryEngineService
from app.modules.repository.repository import RepositoryRepository
from app.modules.repository.service import RepositoryService
from app.modules.retrieval.db_repository import DbSearchStore
from app.modules.retrieval.service import RetrievalService
from app.shared.database.session import get_db_session


async def get_repository_app_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> RepositoryApplicationService:
    """Construct a request-scoped repository application service."""
    domain = RepositoryService(session, RepositoryRepository(session))
    return RepositoryApplicationService(domain)


RepositoryAppServiceDependency = Annotated[
    RepositoryApplicationService, Depends(get_repository_app_service)
]


async def get_ingestion_app_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> IngestionApplicationService:
    """Construct a request-scoped ingestion application service."""
    settings = get_settings()
    repository_domain = RepositoryService(session, RepositoryRepository(session))
    file_filter = RepositoryFileFilter(
        IngestionFilterConfig(max_file_size_bytes=settings.ingestion_max_file_size_bytes)
    )
    domain = IngestionService(
        repository_domain,
        GitClient(settings.git_executable),
        RepositoryWalker(file_filter),
    )
    return IngestionApplicationService(domain)


IngestionAppServiceDependency = Annotated[
    IngestionApplicationService, Depends(get_ingestion_app_service)
]


async def get_indexing_pipeline(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> RepositoryIndexingPipeline:
    """Construct a request-scoped indexing pipeline with all domain services.

    Embeds via Ollama (falling back to a local Ollama instance at
    http://localhost:11434). Indexes into an in-memory store — production
    SQLAlchemy adapters should replace ``InMemoryIndexStore`` once the
    index tables and migrations are created.
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
    """Adapts RepositoryApplicationService to the query engine's RepositoryResolver protocol."""

    def __init__(self, service: RepositoryApplicationService) -> None:
        self._service = service

    async def list_repositories(self) -> Sequence[RepositoryReference]:
        from app.shared.database.pagination import PaginationParams

        page = await self._service.list(PaginationParams(page=1, page_size=100))
        return [RepositoryReference(id=repo.id, name=repo.name) for repo in page.items]


async def get_query_pipeline(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> RepositoryQueryPipeline:
    """Construct a request-scoped query pipeline with all domain services.

    Embeds via Ollama (falling back to a local Ollama instance at
    http://localhost:11434). Uses an empty in-memory search store —
    production SQLAlchemy adapters should replace ``InMemorySearchStore``
    once the read-side projections are ready.
    """
    repository_domain = RepositoryService(session, RepositoryRepository(session))
    repository_service = RepositoryApplicationService(repository_domain)

    resolver = _RepositoryResolverAdapter(repository_service)
    query_engine = QueryEngineService(resolver)

    store = DbSearchStore(session)
    retrieval = RetrievalService(
        OllamaEmbeddingProvider(
            model_name=settings.embedding_model,
            base_url=settings.embedding_base_url,
        ),
        store,
        store,
        store,
    )

    index_store = DbIndexStore(session)
    context_builder = ContextBuilderService()
    workflow_engine = DefaultWorkflowEngine(OllamaResponseGenerator())
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
