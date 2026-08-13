"""Vector-index projection helpers; concrete backends satisfy VectorIndexRepository."""

from app.modules.indexing.models import IndexEntry


def vector_entries(entries: tuple[IndexEntry, ...]) -> tuple[IndexEntry, ...]:
    """Return the vector projection without coupling to a vector-store implementation."""
    return entries
