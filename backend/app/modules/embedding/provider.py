"""Provider-neutral embedding protocol and Ollama implementation."""

from collections.abc import Sequence
from typing import Protocol

import httpx
import structlog

from app.modules.embedding.exceptions import (
    EmbeddingProviderError,
    EmbeddingTimeoutError,
    InvalidEmbeddingResponseError,
)
from app.modules.embedding.models import EmbeddingVector, IndexDocument
from app.shared.clock.utc import utc_now

logger = structlog.get_logger(__name__)


class EmbeddingProvider(Protocol):
    """Provider boundary that only accepts provider-facing index documents."""

    provider_name: str
    model_name: str

    async def embed(self, documents: Sequence[IndexDocument]) -> list[EmbeddingVector]:
        """Generate one vector per document in the same order as the input."""


class OllamaEmbeddingProvider:
    """Ollama `/api/embed` provider adapter with strict response validation."""

    provider_name = "ollama"

    def __init__(
        self,
        model_name: str = "embeddinggemma",
        *,
        base_url: str = "http://localhost:11434",
        timeout_seconds: float = 30.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.model_name = model_name
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds
        self._client = client

    async def embed(self, documents: Sequence[IndexDocument]) -> list[EmbeddingVector]:
        """Embed an ordered document batch through Ollama's native batch endpoint."""
        if not documents:
            return []
        payload = {
            "model": self.model_name,
            "input": [document.text for document in documents],
            "truncate": False,
        }
        logger.debug(
            "embedding_provider_request_started",
            provider=self.provider_name,
            count=len(documents),
        )
        try:
            if self._client is not None:
                response = await self._client.post(f"{self._base_url}/api/embed", json=payload)
            else:
                async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                    response = await client.post(f"{self._base_url}/api/embed", json=payload)
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise EmbeddingTimeoutError("Ollama embedding request timed out.") from exc
        except httpx.HTTPError as exc:
            raise EmbeddingProviderError("Ollama embedding request failed.") from exc

        try:
            embeddings = response.json()["embeddings"]
        except (KeyError, TypeError, ValueError) as exc:
            raise InvalidEmbeddingResponseError(
                "Ollama response did not contain embeddings."
            ) from exc
        if not isinstance(embeddings, list) or len(embeddings) != len(documents):
            raise InvalidEmbeddingResponseError("Ollama returned an unexpected embedding count.")

        vectors: list[EmbeddingVector] = []
        dimensions: int | None = None
        for document, raw_vector in zip(documents, embeddings, strict=True):
            if (
                not isinstance(raw_vector, list)
                or not raw_vector
                or not all(isinstance(value, (int, float)) for value in raw_vector)
            ):
                raise InvalidEmbeddingResponseError("Ollama returned an invalid embedding vector.")
            vector = tuple(float(value) for value in raw_vector)
            if dimensions is None:
                dimensions = len(vector)
            elif len(vector) != dimensions:
                raise InvalidEmbeddingResponseError(
                    "Ollama returned inconsistent vector dimensions."
                )
            vectors.append(
                EmbeddingVector(
                    document_id=document.id,
                    vector=vector,
                    dimensions=len(vector),
                    provider=self.provider_name,
                    model=self.model_name,
                    created_at=utc_now(),
                )
            )
        logger.debug(
            "embedding_provider_request_completed",
            provider=self.provider_name,
            count=len(vectors),
        )
        return vectors
