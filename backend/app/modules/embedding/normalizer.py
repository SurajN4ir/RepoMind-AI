"""Vector normalization isolated from provider transport concerns."""

from math import sqrt

from app.modules.embedding.exceptions import InvalidEmbeddingResponseError
from app.modules.embedding.models import EmbeddingVector


class VectorNormalizer:
    """Normalize embedding vectors to unit length for cosine-similarity consistency."""

    def normalize(self, embedding: EmbeddingVector) -> EmbeddingVector:
        """Return a unit-length copy of an embedding vector."""
        magnitude = sqrt(sum(value * value for value in embedding.vector))
        if magnitude == 0:
            raise InvalidEmbeddingResponseError("Embedding provider returned a zero vector.")
        normalized = tuple(value / magnitude for value in embedding.vector)
        return EmbeddingVector(
            document_id=embedding.document_id,
            vector=normalized,
            dimensions=len(normalized),
            provider=embedding.provider,
            model=embedding.model,
            created_at=embedding.created_at,
        )
