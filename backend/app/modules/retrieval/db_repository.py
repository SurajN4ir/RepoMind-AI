"""Database-backed search store adapter implementing read-side ports."""

from collections.abc import Mapping, Sequence
from math import sqrt
from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.indexing.db_models import IndexEntryModel
from app.modules.retrieval.models import SearchResult
from app.modules.retrieval.repository import (
    KeywordSearchRepository,
    MetadataSearchRepository,
    VectorSearchRepository,
)

logger = structlog.get_logger(__name__)


class DbSearchStore(VectorSearchRepository, KeywordSearchRepository, MetadataSearchRepository):
    """Persistent search store backed by SQLAlchemy async sessions.

    Vector similarity is computed in Python (cosine similarity) so that no
    pgvector extension is required at the database level.  Replace with a
    pgvector-based implementation for large-scale production deployments.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _vector_search(
        self,
        query_vector: tuple[float, ...],
        *,
        repository_id: UUID | None,
        filters: Mapping[str, object],
        limit: int,
    ) -> Sequence[SearchResult]:
        rows = await self._fetch_models(repository_id)
        candidates = (
            row
            for row in rows
            if self._matches_repo(row, repository_id)
            and self._matches_filters(row.entry_metadata, filters)
            and len(query_vector) == len(row.embedding)
        )
        ranked = sorted(
            (
                SearchResult(
                    chunk_id=row.document_id,
                    score=self._cosine(query_vector, tuple(row.embedding)),
                    text=row.text,
                    metadata=dict(row.entry_metadata),
                )
                for row in candidates
            ),
            key=lambda r: (-r.score, r.chunk_id),
        )
        return ranked[:limit]

    async def _keyword_lookup(
        self,
        query_text: str,
        *,
        repository_id: UUID | None,
        filters: Mapping[str, object],
        limit: int,
    ) -> Sequence[SearchResult]:
        rows = await self._fetch_models(repository_id)
        query_terms = {t.lower() for t in query_text.split() if t}
        candidates = (
            row
            for row in rows
            if self._matches_repo(row, repository_id)
            and self._matches_filters(row.entry_metadata, filters)
        )
        scored = (
            SearchResult(
                chunk_id=row.document_id,
                score=self._keyword_score(query_terms, row.text),
                text=row.text,
                metadata=dict(row.entry_metadata),
            )
            for row in candidates
        )
        ranked = sorted(
            (r for r in scored if r.score > 0),
            key=lambda r: (-r.score, r.chunk_id),
        )
        return ranked[:limit]

    async def search(
        self,
        query: tuple[float, ...] | str,
        *,
        repository_id: UUID | None,
        filters: Mapping[str, object],
        limit: int,
    ) -> Sequence[SearchResult]:
        if isinstance(query, tuple):
            return await self._vector_search(
                query, repository_id=repository_id, filters=filters, limit=limit
            )
        return await self._keyword_lookup(
            query, repository_id=repository_id, filters=filters, limit=limit
        )

    async def filter(
        self,
        results: Sequence[SearchResult],
        filters: Mapping[str, object],
    ) -> Sequence[SearchResult]:
        if not filters:
            return results
        return [
            r
            for r in results
            if all(r.metadata.get(key) == value for key, value in filters.items())
        ]

    async def _fetch_models(self, repository_id: UUID | None) -> Sequence[IndexEntryModel]:
        if repository_id is None:
            rows = await self._session.execute(select(IndexEntryModel))
        else:
            rows = await self._session.execute(
                select(IndexEntryModel).where(IndexEntryModel.repository_id == repository_id)
            )
        return rows.scalars().all()

    @staticmethod
    def _matches_repo(row: IndexEntryModel, repository_id: UUID | None) -> bool:
        if repository_id is None:
            return True
        return row.repository_id == repository_id

    @staticmethod
    def _matches_filters(metadata: dict, filters: Mapping[str, object]) -> bool:
        return all(metadata.get(key) == value for key, value in filters.items())

    @staticmethod
    def _cosine(first: tuple[float, ...], second: tuple[float, ...]) -> float:
        first_mag = sqrt(sum(v * v for v in first))
        second_mag = sqrt(sum(v * v for v in second))
        if first_mag == 0 or second_mag == 0:
            return 0.0
        return sum(a * b for a, b in zip(first, second, strict=True)) / (first_mag * second_mag)

    @staticmethod
    def _keyword_score(query_terms: set[str], text: str) -> float:
        text_lower = text.lower()
        return float(sum(term in text_lower for term in query_terms))
