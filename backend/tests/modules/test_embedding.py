"""Async unit tests for the provider-agnostic embedding pipeline."""

import json
from datetime import UTC, datetime
from uuid import UUID

import httpx
import pytest

from app.modules.chunker.models import Chunk, ChunkCollection, ChunkStatistics, ChunkType
from app.modules.embedding.batcher import DocumentBatcher
from app.modules.embedding.exceptions import EmbeddingBatchFailedError, EmbeddingProviderError
from app.modules.embedding.models import EmbeddingVector, IndexDocument
from app.modules.embedding.provider import OllamaEmbeddingProvider
from app.modules.embedding.service import EmbeddingService
from app.modules.embedding.transformers import ChunkDocumentTransformer
from app.modules.parser.language import SupportedLanguage
from app.modules.parser.models import SymbolKind
from app.shared.identifiers.uuid import new_uuid


def _chunk(identifier: str = "chunk-1", repository_id: UUID | None = None) -> Chunk:
    repository_id = repository_id or new_uuid()
    return Chunk(
        id=identifier,
        repository_id=repository_id,
        file_path="src/auth.py",
        language=SupportedLanguage.PYTHON,
        symbol_name="login",
        qualified_symbol_name="AuthService.login",
        symbol_kind=SymbolKind.METHOD,
        content="def login(user):\n    return user",
        start_line=10,
        end_line=11,
        token_count=8,
        chunk_type=ChunkType.METHOD,
        metadata={"imports": ["import os"], "parent_symbol": "AuthService"},
    )


def _collection(*chunks: Chunk) -> ChunkCollection:
    if not chunks:
        return ChunkCollection(
            repository_id=new_uuid(),
            version=1,
            created_at=datetime.now(UTC),
            chunks=(),
            statistics=ChunkStatistics(0, 0.0, 0, 0, {}),
        )
    return ChunkCollection.create(chunks[0].repository_id, chunks)


def test_chunk_transformer_preserves_rich_metadata() -> None:
    document = ChunkDocumentTransformer().transform(_chunk())

    assert document.id == "chunk-1"
    assert "Symbol: AuthService.login" in document.text
    assert "Language: python" in document.text
    assert document.metadata["file_path"] == "src/auth.py"
    assert document.metadata["qualified_symbol_name"] == "AuthService.login"
    assert document.metadata["chunk_type"] == "method"


def test_batcher_preserves_order_and_token_budget() -> None:
    documents = tuple(IndexDocument(str(index), "one two", {}) for index in range(3))
    batches = DocumentBatcher(max_batch_size=2, max_token_budget=3).batch(documents)

    batch_ids = [[document.id for document in batch.documents] for batch in batches]
    assert batch_ids == [["0"], ["1"], ["2"]]
    assert [batch.token_count for batch in batches] == [2, 2, 2]


class _FakeProvider:
    provider_name = "fake"
    model_name = "fake-model"

    def __init__(self, failures: int = 0) -> None:
        self.failures = failures
        self.calls = 0

    async def embed(self, documents: tuple[IndexDocument, ...]) -> list[EmbeddingVector]:
        self.calls += 1
        if self.calls <= self.failures:
            raise EmbeddingProviderError("temporary failure")
        return [
            EmbeddingVector(
                document_id=document.id,
                vector=(3.0, 4.0),
                dimensions=2,
                provider=self.provider_name,
                model=self.model_name,
                created_at=datetime.now(UTC),
            )
            for document in documents
        ]


@pytest.mark.asyncio
async def test_embedding_service_generates_normalized_vectors() -> None:
    provider = _FakeProvider()
    first_chunk = _chunk("first")
    second_chunk = _chunk("second", first_chunk.repository_id)
    collection = _collection(first_chunk, second_chunk)

    embeddings = await EmbeddingService(provider).embed(collection)  # type: ignore[arg-type]

    assert embeddings.provider == "fake"
    assert embeddings.statistics.document_count == 2
    assert embeddings.statistics.batch_count == 1
    assert embeddings.vectors[0].vector == pytest.approx((0.6, 0.8))
    assert provider.calls == 1


@pytest.mark.asyncio
async def test_embedding_service_handles_empty_collections_without_provider_calls() -> None:
    provider = _FakeProvider()

    embeddings = await EmbeddingService(provider).embed(_collection())  # type: ignore[arg-type]

    assert embeddings.vectors == ()
    assert embeddings.statistics.batch_count == 0
    assert provider.calls == 0


@pytest.mark.asyncio
async def test_embedding_service_retries_batch_failures() -> None:
    provider = _FakeProvider(failures=1)

    embeddings = await EmbeddingService(
        provider,  # type: ignore[arg-type]
        max_retries=1,
        retry_delay_seconds=0,
    ).embed(_collection(_chunk()))

    assert len(embeddings.vectors) == 1
    assert provider.calls == 2


@pytest.mark.asyncio
async def test_embedding_service_raises_when_retries_are_exhausted() -> None:
    provider = _FakeProvider(failures=3)

    with pytest.raises(EmbeddingBatchFailedError):
        await EmbeddingService(
            provider,  # type: ignore[arg-type]
            max_retries=1,
            retry_delay_seconds=0,
        ).embed(_collection(_chunk()))


@pytest.mark.asyncio
async def test_ollama_provider_maps_batch_response_and_payload() -> None:
    captured_payload: dict[str, object] = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        captured_payload.update(json.loads((await request.aread()).decode("utf-8")))
        return httpx.Response(200, json={"embeddings": [[1.0, 0.0], [0.0, 1.0]]})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        provider = OllamaEmbeddingProvider(model_name="test-model", client=client)
        vectors = await provider.embed(
            [IndexDocument("one", "first", {}), IndexDocument("two", "second", {})]
        )

    assert captured_payload == {
        "model": "test-model",
        "input": ["first", "second"],
        "truncate": False,
    }
    assert [vector.document_id for vector in vectors] == ["one", "two"]
    assert all(vector.provider == "ollama" for vector in vectors)
