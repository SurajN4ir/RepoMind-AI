"""Retrieval bounded-context exceptions."""


class RetrievalError(Exception):
    """Base exception for read-side retrieval failures."""


class EmptySearchQueryError(RetrievalError):
    """Raised when retrieval is asked to process blank query text."""


class RetrievalStorageError(RetrievalError):
    """Raised when a read-side storage adapter cannot complete a search."""


class QueryEmbeddingError(RetrievalError):
    """Raised when an embedding provider cannot embed the retrieval query."""
