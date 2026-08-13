"""Idempotent write-side synchronization of vector, keyword, and metadata projections."""

from time import perf_counter

import structlog

from app.modules.embedding.models import EmbeddingCollection
from app.modules.indexing.exceptions import IndexingStorageError, InvalidIndexInputError
from app.modules.indexing.incremental import content_hash, plan_changes
from app.modules.indexing.keyword_index import keyword_entries
from app.modules.indexing.metadata_index import metadata_entries
from app.modules.indexing.models import IndexEntry, IndexStatistics, RepositoryIndex
from app.modules.indexing.repository import (
    IndexingTransactionManager,
    KeywordIndexRepository,
    MetadataIndexRepository,
    VectorIndexRepository,
)
from app.modules.indexing.vector_index import vector_entries

logger = structlog.get_logger(__name__)


class IndexingService:
    """Synchronize index projections through storage ports without implementing search."""

    def __init__(
        self,
        vector_repository: VectorIndexRepository,
        keyword_repository: KeywordIndexRepository,
        metadata_repository: MetadataIndexRepository,
        transaction_manager: IndexingTransactionManager,
    ) -> None:
        self._vector_repository = vector_repository
        self._keyword_repository = keyword_repository
        self._metadata_repository = metadata_repository
        self._transaction_manager = transaction_manager

    async def index(self, embeddings: EmbeddingCollection) -> RepositoryIndex:
        """Synchronize an embedding collection idempotently across all index projections."""
        started_at = perf_counter()
        entries = self._build_entries(embeddings)
        try:
            existing_hashes = await self._vector_repository.get_hashes(embeddings.repository_id)
            changes = plan_changes(entries, existing_hashes)
            changed_entries = changes.inserts + changes.updates
            async with self._transaction_manager.transaction():
                if changed_entries:
                    await self._vector_repository.upsert(vector_entries(changed_entries))
                    await self._keyword_repository.upsert(keyword_entries(changed_entries))
                    await self._metadata_repository.upsert(metadata_entries(changed_entries))
                if changes.deletes:
                    await self._vector_repository.delete(embeddings.repository_id, changes.deletes)
                    await self._keyword_repository.delete(embeddings.repository_id, changes.deletes)
                    await self._metadata_repository.delete(
                        embeddings.repository_id,
                        changes.deletes,
                    )
        except InvalidIndexInputError:
            raise
        except Exception as exc:
            raise IndexingStorageError("Index storage synchronization failed.") from exc

        statistics = IndexStatistics(
            inserted=len(changes.inserts),
            updated=len(changes.updates),
            deleted=len(changes.deletes),
            unchanged=len(changes.unchanged),
            elapsed_time_seconds=perf_counter() - started_at,
        )
        result = RepositoryIndex(
            repository_id=embeddings.repository_id,
            vector_entries=entries,
            keyword_entries=keyword_entries(entries),
            metadata_entries=metadata_entries(entries),
            statistics=statistics,
        )
        logger.info(
            "repository_index_synchronized",
            repository_id=str(embeddings.repository_id),
            inserted=statistics.inserted,
            updated=statistics.updated,
            deleted=statistics.deleted,
            unchanged=statistics.unchanged,
        )
        return result

    @staticmethod
    def _build_entries(embeddings: EmbeddingCollection) -> tuple[IndexEntry, ...]:
        documents = {document.id: document for document in embeddings.documents}
        if len(documents) != len(embeddings.vectors):
            raise InvalidIndexInputError(
                "Embedding documents and vectors must have matching counts."
            )
        entries: list[IndexEntry] = []
        for vector in embeddings.vectors:
            document = documents.get(vector.document_id)
            if document is None:
                raise InvalidIndexInputError("Embedding vector has no matching index document.")
            entries.append(
                IndexEntry(
                    document_id=document.id,
                    repository_id=embeddings.repository_id,
                    embedding=vector.vector,
                    text=document.text,
                    metadata=document.metadata,
                    content_hash=content_hash(
                        text=document.text,
                        metadata=document.metadata,
                        model=vector.model,
                    ),
                    provider=vector.provider,
                    model=vector.model,
                )
            )
        return tuple(entries)
