"""Query normalization and provider-facing query-document construction."""

from hashlib import sha256

from app.modules.embedding.models import IndexDocument
from app.modules.retrieval.models import SearchQuery


def query_document(query: SearchQuery) -> IndexDocument:
    """Create a provider-neutral document for embedding a user search query."""
    normalized = query.text.strip()
    identifier = sha256(normalized.encode("utf-8")).hexdigest()
    return IndexDocument(
        id=f"query:{identifier}",
        text=normalized,
        metadata={"kind": "retrieval_query"},
    )
