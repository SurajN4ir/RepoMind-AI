"""Keyword-index projection helpers; concrete backends satisfy KeywordIndexRepository."""

from app.modules.indexing.models import IndexEntry, KeywordIndexEntry


def keyword_entries(entries: tuple[IndexEntry, ...]) -> tuple[KeywordIndexEntry, ...]:
    """Derive keyword text records from canonical index entries."""
    return tuple(
        KeywordIndexEntry(entry.document_id, entry.repository_id, entry.text) for entry in entries
    )
