"""Indexing bounded-context exceptions."""


class IndexingError(Exception):
    """Base exception for write-side indexing failures."""


class InvalidIndexInputError(IndexingError):
    """Raised when embedding vectors and documents cannot be indexed safely."""


class IndexingStorageError(IndexingError):
    """Raised when an index storage adapter cannot complete an operation."""


class IndexingTransactionError(IndexingError):
    """Raised when an index write transaction cannot be completed."""
