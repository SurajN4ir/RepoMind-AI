"""Embedding bounded-context exceptions."""


class EmbeddingError(Exception):
    """Base exception for transient embedding pipeline failures."""


class EmbeddingProviderError(EmbeddingError):
    """Raised when an embedding provider cannot complete a request."""


class EmbeddingTimeoutError(EmbeddingProviderError):
    """Raised when an embedding provider does not respond before its timeout."""


class EmbeddingBatchFailedError(EmbeddingError):
    """Raised after retry attempts for a document batch are exhausted."""


class InvalidEmbeddingResponseError(EmbeddingProviderError):
    """Raised when provider output cannot be mapped safely to requested documents."""


class UnsupportedEmbeddingProviderError(EmbeddingError):
    """Raised when configured embedding provider selection is unsupported."""
