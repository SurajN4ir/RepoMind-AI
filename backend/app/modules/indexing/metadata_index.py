"""Metadata-index projection helpers; concrete backends satisfy MetadataIndexRepository."""

from app.modules.indexing.models import IndexEntry, MetadataIndexEntry


def metadata_entries(entries: tuple[IndexEntry, ...]) -> tuple[MetadataIndexEntry, ...]:
    """Derive metadata records from canonical index entries."""
    return tuple(
        MetadataIndexEntry(entry.document_id, entry.repository_id, entry.metadata)
        for entry in entries
    )
