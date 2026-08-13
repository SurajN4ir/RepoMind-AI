"""Deterministic content hashing and incremental index change planning."""

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from hashlib import sha256

from app.modules.indexing.models import IndexEntry


@dataclass(frozen=True, slots=True)
class IndexChangeSet:
    """Deterministic writes required to synchronize one repository index."""

    inserts: tuple[IndexEntry, ...]
    updates: tuple[IndexEntry, ...]
    unchanged: tuple[IndexEntry, ...]
    deletes: tuple[str, ...]


def content_hash(*, text: str, metadata: Mapping[str, object], model: str) -> str:
    """Hash semantically indexed content and model identity for incremental correctness."""
    serialized_metadata = json.dumps(metadata, sort_keys=True, separators=(",", ":"), default=str)
    payload = "\x1f".join((text, serialized_metadata, model))
    return sha256(payload.encode("utf-8")).hexdigest()


def plan_changes(
    current_entries: Sequence[IndexEntry],
    existing_hashes: Mapping[str, str],
) -> IndexChangeSet:
    """Classify current documents as inserts, updates, unchanged entries, or deletions."""
    current_ids = {entry.document_id for entry in current_entries}
    inserts: list[IndexEntry] = []
    updates: list[IndexEntry] = []
    unchanged: list[IndexEntry] = []
    for entry in current_entries:
        existing_hash = existing_hashes.get(entry.document_id)
        if existing_hash is None:
            inserts.append(entry)
        elif existing_hash == entry.content_hash:
            unchanged.append(entry)
        else:
            updates.append(entry)
    deletes = tuple(sorted(set(existing_hashes) - current_ids))
    return IndexChangeSet(tuple(inserts), tuple(updates), tuple(unchanged), deletes)
