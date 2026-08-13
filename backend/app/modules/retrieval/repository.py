"""Read-side storage ports and deterministic in-memory search adapter for tests."""

from collections.abc import Mapping, Sequence
from math import sqrt
from typing import Protocol
from uuid import UUID

from app.modules.indexing.models import IndexEntry
from app.modules.retrieval.models import SearchResult


class VectorSearchRepository(Protocol):
    """Port for ranked vector similarity lookup without retrieval orchestration."""

    async def search(
        self,
        query_vector: tuple[float, ...],
        *,
        repository_id: UUID | None,
        filters: Mapping[str, object],
        limit: int,
    ) -> Sequence[SearchResult]: ...


class KeywordSearchRepository(Protocol):
    """Port for ranked lexical lookup without ranking fusion."""

    async def search(
        self,
        query_text: str,
        *,
        repository_id: UUID | None,
        filters: Mapping[str, object],
        limit: int,
    ) -> Sequence[SearchResult]: ...


class MetadataSearchRepository(Protocol):
    """Port for filter evaluation over fused read-side results."""

    async def filter(
        self,
        results: Sequence[SearchResult],
        filters: Mapping[str, object],
    ) -> Sequence[SearchResult]: ...


class InMemorySearchStore(
    VectorSearchRepository,
    KeywordSearchRepository,
    MetadataSearchRepository,
):
    """Deterministic test adapter implementing read-side ports without persistence selection."""

    def __init__(self, entries: Sequence[IndexEntry]) -> None:
        self._entries = tuple(entries)

    async def search(
        self,
        query: tuple[float, ...] | str,
        *,
        repository_id: UUID | None,
        filters: Mapping[str, object],
        limit: int,
    ) -> Sequence[SearchResult]:
        entries = [entry for entry in self._entries if self._matches(entry, repository_id, filters)]
        if isinstance(query, tuple):
            ranked = sorted(
                (
                    self._result(entry, self._cosine(query, entry.embedding))
                    for entry in entries
                    if len(query) == len(entry.embedding)
                ),
                key=lambda result: (-result.score, result.chunk_id),
            )
            return ranked[:limit]
        query_terms = {term.lower() for term in query.split() if term}
        ranked = sorted(
            (
                self._result(entry, self._keyword_score(query_terms, entry.text))
                for entry in entries
                if self._keyword_score(query_terms, entry.text) > 0
            ),
            key=lambda result: (-result.score, result.chunk_id),
        )
        return ranked[:limit]

    async def filter(
        self,
        results: Sequence[SearchResult],
        filters: Mapping[str, object],
    ) -> Sequence[SearchResult]:
        return [
            result
            for result in results
            if all(result.metadata.get(key) == value for key, value in filters.items())
        ]

    @staticmethod
    def _matches(
        entry: IndexEntry,
        repository_id: UUID | None,
        filters: Mapping[str, object],
    ) -> bool:
        if repository_id is not None and entry.repository_id != repository_id:
            return False
        return all(entry.metadata.get(key) == value for key, value in filters.items())

    @staticmethod
    def _result(entry: IndexEntry, score: float) -> SearchResult:
        return SearchResult(entry.document_id, score, entry.text, entry.metadata)

    @staticmethod
    def _cosine(first: tuple[float, ...], second: tuple[float, ...]) -> float:
        first_magnitude = sqrt(sum(value * value for value in first))
        second_magnitude = sqrt(sum(value * value for value in second))
        if first_magnitude == 0 or second_magnitude == 0:
            return 0.0
        return sum(left * right for left, right in zip(first, second, strict=True)) / (
            first_magnitude * second_magnitude
        )

    @staticmethod
    def _keyword_score(query_terms: set[str], text: str) -> float:
        text_lower = text.lower()
        return float(sum(term in text_lower for term in query_terms))
