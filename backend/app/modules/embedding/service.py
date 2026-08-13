"""Provider-agnostic orchestration from semantic chunks to normalized embeddings."""

import asyncio
from time import perf_counter

import structlog

from app.modules.chunker.models import ChunkCollection
from app.modules.embedding.batcher import DocumentBatcher
from app.modules.embedding.exceptions import (
    EmbeddingBatchFailedError,
    EmbeddingProviderError,
    InvalidEmbeddingResponseError,
)
from app.modules.embedding.models import (
    EmbeddingCollection,
    EmbeddingStatistics,
    EmbeddingVector,
    IndexDocument,
)
from app.modules.embedding.normalizer import VectorNormalizer
from app.modules.embedding.provider import EmbeddingProvider
from app.modules.embedding.transformers import ChunkDocumentTransformer

logger = structlog.get_logger(__name__)


class EmbeddingService:
    """Embed chunk collections without coupling the pipeline to a provider vendor."""

    def __init__(
        self,
        provider: EmbeddingProvider,
        *,
        transformer: ChunkDocumentTransformer | None = None,
        batcher: DocumentBatcher | None = None,
        normalizer: VectorNormalizer | None = None,
        max_retries: int = 2,
        retry_delay_seconds: float = 0.25,
    ) -> None:
        if max_retries < 0 or retry_delay_seconds < 0:
            raise ValueError("Retry settings cannot be negative.")
        self._provider = provider
        self._transformer = transformer or ChunkDocumentTransformer()
        self._batcher = batcher or DocumentBatcher()
        self._normalizer = normalizer or VectorNormalizer()
        self._max_retries = max_retries
        self._retry_delay_seconds = retry_delay_seconds

    async def embed(self, chunks: ChunkCollection) -> EmbeddingCollection:
        """Transform, batch, embed, normalize, and return transient vector output."""
        started_at = perf_counter()
        documents = self._transformer.transform_collection(chunks.chunks)
        batches = self._batcher.batch(documents)
        vectors: list[EmbeddingVector] = []
        total_batch_latency = 0.0
        for index, batch in enumerate(batches):
            batch_started_at = perf_counter()
            generated = await self._embed_with_retry(batch.documents, index)
            self._validate_document_order(batch.documents, generated)
            vectors.extend(self._normalizer.normalize(vector) for vector in generated)
            total_batch_latency += perf_counter() - batch_started_at
        elapsed = perf_counter() - started_at
        collection = EmbeddingCollection(
            repository_id=chunks.repository_id,
            provider=self._provider.provider_name,
            model=self._provider.model_name,
            vectors=tuple(vectors),
            statistics=EmbeddingStatistics(
                document_count=len(documents),
                total_tokens=sum(batch.token_count for batch in batches),
                batch_count=len(batches),
                elapsed_time_seconds=elapsed,
                average_latency_seconds=total_batch_latency / len(batches) if batches else 0.0,
            ),
            documents=documents,
        )
        logger.info(
            "embedding_collection_created",
            repository_id=str(chunks.repository_id),
            provider=collection.provider,
            document_count=collection.statistics.document_count,
        )
        return collection

    async def _embed_with_retry(
        self,
        documents: tuple[IndexDocument, ...],
        batch_index: int,
    ) -> list[EmbeddingVector]:
        for attempt in range(self._max_retries + 1):
            try:
                return await self._provider.embed(documents)
            except EmbeddingProviderError as exc:
                if attempt == self._max_retries:
                    raise EmbeddingBatchFailedError(
                        f"Embedding batch {batch_index} failed after {attempt + 1} attempts."
                    ) from exc
                delay = self._retry_delay_seconds * (2**attempt)
                logger.warning(
                    "embedding_batch_retrying",
                    batch_index=batch_index,
                    attempt=attempt + 1,
                    delay_seconds=delay,
                )
                if delay:
                    await asyncio.sleep(delay)
        raise AssertionError("Retry loop must return or raise.")

    @staticmethod
    def _validate_document_order(
        documents: tuple[IndexDocument, ...],
        vectors: list[EmbeddingVector],
    ) -> None:
        if len(documents) != len(vectors) or any(
            document.id != vector.document_id
            for document, vector in zip(documents, vectors, strict=True)
        ):
            raise InvalidEmbeddingResponseError("Provider vectors did not preserve document order.")
