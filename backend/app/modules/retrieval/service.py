"""Provider-agnostic hybrid retrieval orchestration."""

import asyncio
from time import perf_counter

import structlog

from app.modules.embedding.exceptions import EmbeddingProviderError
from app.modules.embedding.provider import EmbeddingProvider
from app.modules.retrieval.context import ContextBuilder
from app.modules.retrieval.exceptions import QueryEmbeddingError, RetrievalStorageError
from app.modules.retrieval.models import RetrievalStatistics, RetrievedContext, SearchQuery
from app.modules.retrieval.query import query_document
from app.modules.retrieval.ranking import HybridRanker
from app.modules.retrieval.repository import (
    KeywordSearchRepository,
    MetadataSearchRepository,
    VectorSearchRepository,
)

logger = structlog.get_logger(__name__)


class RetrievalService:
    """Embed queries, retrieve hybrid candidates, rank, filter, and assemble context."""

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_repository: VectorSearchRepository,
        keyword_repository: KeywordSearchRepository,
        metadata_repository: MetadataSearchRepository,
        *,
        ranker: HybridRanker | None = None,
        context_builder: ContextBuilder | None = None,
    ) -> None:
        self._embedding_provider = embedding_provider
        self._vector_repository = vector_repository
        self._keyword_repository = keyword_repository
        self._metadata_repository = metadata_repository
        self._ranker = ranker or HybridRanker()
        self._context_builder = context_builder or ContextBuilder()

    async def retrieve(self, query: SearchQuery) -> RetrievedContext:
        """Run provider-neutral hybrid retrieval and return ordered, cited context."""
        started_at = perf_counter()
        try:
            embedded_query = await self._embedding_provider.embed([query_document(query)])
        except EmbeddingProviderError as exc:
            raise QueryEmbeddingError("Could not embed retrieval query.") from exc
        if len(embedded_query) != 1:
            raise QueryEmbeddingError("Embedding provider returned an invalid query vector.")

        search_limit = query.limit + query.offset
        try:
            vector_results, keyword_results = await asyncio.gather(
                self._vector_repository.search(
                    embedded_query[0].vector,
                    repository_id=query.repository_id,
                    filters=query.filters,
                    limit=search_limit,
                ),
                self._keyword_repository.search(
                    query.text,
                    repository_id=query.repository_id,
                    filters=query.filters,
                    limit=search_limit,
                ),
            )
        except Exception as exc:
            raise RetrievalStorageError("Read-side index search failed.") from exc

        rrf_started_at = perf_counter()
        fused = self._ranker.rank(vector_results, keyword_results)
        rrf_elapsed = perf_counter() - rrf_started_at
        try:
            filtered = await self._metadata_repository.filter(fused, query.filters)
        except Exception as exc:
            raise RetrievalStorageError("Metadata filtering failed.") from exc
        paginated = tuple(filtered[query.offset : query.offset + query.limit])
        statistics = RetrievalStatistics(
            vector_hits=len(vector_results),
            keyword_hits=len(keyword_results),
            rrf_time_seconds=rrf_elapsed,
            retrieval_time_seconds=perf_counter() - started_at,
            rerank_time_seconds=0.0,
        )
        context = self._context_builder.build(query, paginated, statistics)
        logger.info(
            "retrieval_context_created",
            result_count=len(context.results),
            vector_hits=statistics.vector_hits,
            keyword_hits=statistics.keyword_hits,
        )
        return context
