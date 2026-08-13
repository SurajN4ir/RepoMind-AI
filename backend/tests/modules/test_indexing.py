"""Async tests for idempotent write-side indexing through storage abstractions."""

from datetime import UTC, datetime

import pytest

from app.modules.embedding.models import (
    EmbeddingCollection,
    EmbeddingStatistics,
    EmbeddingVector,
    IndexDocument,
)
from app.modules.indexing.exceptions import IndexingStorageError
from app.modules.indexing.repository import InMemoryIndexStore
from app.modules.indexing.service import IndexingService
from app.shared.identifiers.uuid import new_uuid


def _embeddings(*documents: IndexDocument) -> EmbeddingCollection:
    repository_id = new_uuid()
    vectors = tuple(
        EmbeddingVector(
            document_id=document.id,
            vector=(0.6, 0.8),
            dimensions=2,
            provider="test-provider",
            model="test-model",
            created_at=datetime.now(UTC),
        )
        for document in documents
    )
    return EmbeddingCollection(
        repository_id=repository_id,
        provider="test-provider",
        model="test-model",
        vectors=vectors,
        statistics=EmbeddingStatistics(len(documents), 0, 1 if documents else 0, 0.0, 0.0),
        documents=documents,
    )


def _document(identifier: str, text: str = "source", **metadata: object) -> IndexDocument:
    return IndexDocument(
        id=identifier,
        text=text,
        metadata={"file_path": "src/file.py", "language": "python", **metadata},
    )


def _service(store: InMemoryIndexStore) -> IndexingService:
    return IndexingService(store, store, store, store)


@pytest.mark.asyncio
async def test_fresh_indexing_writes_all_projections_and_metadata() -> None:
    store = InMemoryIndexStore()
    collection = _embeddings(_document("one"), _document("two", symbol_kind="function"))

    result = await _service(store).index(collection)

    assert result.statistics.inserted == 2
    assert result.statistics.updated == 0
    assert len(store.vector_entries) == 2
    assert len(store.keyword_entries) == 2
    assert len(store.metadata_entries) == 2
    stored_metadata = store.metadata_entries[(collection.repository_id, "two")].metadata
    assert stored_metadata["symbol_kind"] == "function"


@pytest.mark.asyncio
async def test_reindexing_unchanged_collection_is_idempotent() -> None:
    store = InMemoryIndexStore()
    collection = _embeddings(_document("one"), _document("two"))
    service = _service(store)

    await service.index(collection)
    result = await service.index(collection)

    assert result.statistics.inserted == 0
    assert result.statistics.updated == 0
    assert result.statistics.unchanged == 2
    assert len(store.vector_entries) == 2


@pytest.mark.asyncio
async def test_indexing_updates_changed_document_and_deletes_missing_document() -> None:
    store = InMemoryIndexStore()
    initial = _embeddings(_document("one", "old"), _document("two", "remove"))
    service = _service(store)
    await service.index(initial)

    changed = EmbeddingCollection(
        repository_id=initial.repository_id,
        provider=initial.provider,
        model=initial.model,
        vectors=(
            EmbeddingVector(
                "one",
                (1.0, 0.0),
                2,
                "test-provider",
                "test-model",
                datetime.now(UTC),
            ),
        ),
        statistics=EmbeddingStatistics(1, 0, 1, 0.0, 0.0),
        documents=(_document("one", "new"),),
    )

    result = await service.index(changed)

    assert result.statistics.updated == 1
    assert result.statistics.deleted == 1
    assert (initial.repository_id, "two") not in store.vector_entries
    assert store.keyword_entries[(initial.repository_id, "one")].text == "new"


class _FailingKeywordRepository:
    async def upsert(self, entries: object) -> None:
        raise RuntimeError("storage unavailable")

    async def delete(self, repository_id: object, document_ids: object) -> None:
        return None


@pytest.mark.asyncio
async def test_failed_projection_write_rolls_back_all_index_projections() -> None:
    store = InMemoryIndexStore()
    collection = _embeddings(_document("one"))
    failing_keywords = _FailingKeywordRepository()
    service = IndexingService(store, failing_keywords, store, store)  # type: ignore[arg-type]

    with pytest.raises(IndexingStorageError):
        await service.index(collection)

    assert store.vector_entries == {}
    assert store.keyword_entries == {}
    assert store.metadata_entries == {}


@pytest.mark.asyncio
async def test_batch_indexing_handles_multiple_entries_in_one_sync() -> None:
    store = InMemoryIndexStore()
    collection = _embeddings(*(_document(f"document-{index}") for index in range(10)))

    result = await _service(store).index(collection)

    assert result.statistics.inserted == 10
    assert len(result.vector_entries) == 10
