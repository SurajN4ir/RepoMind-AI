"""PostgreSQL + pgvector-backed vector similarity search adapter."""

from collections.abc import Mapping, Sequence
from uuid import UUID

import structlog
from pgvector.sqlalchemy import Vector
from sqlalchemy import Float, bindparam, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.indexing.db_models import IndexEntryModel
from app.modules.retrieval.models import SearchResult
from app.modules.retrieval.repository import VectorSearchRepository

logger = structlog.get_logger(__name__)


class PgVectorSearchStore(VectorSearchRepository):
    """Database-side vector similarity search using pgvector's cosine distance operator.

    Ranking happens in PostgreSQL (``ORDER BY embedding <=> :query LIMIT :limit``)
    instead of loading every candidate row into Python. Only the vector port is
    implemented here; pair with ``DbSearchStore`` for keyword search and metadata
    filtering, which are unaffected by this change. Requires
    ``index_entries.embedding`` to be a real pgvector column (see migration
    0008_pgvector_embedding_column) — only wire this adapter in when the
    configured database is PostgreSQL.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def search(
        self,
        query_vector: tuple[float, ...],
        *,
        repository_id: UUID | None,
        filters: Mapping[str, object],
        limit: int,
    ) -> Sequence[SearchResult]:
        query_param = bindparam(
            "query_vector", list(query_vector), type_=Vector(len(query_vector))
        )
        # return_type is required: .op() without one infers the result type from the
        # left operand (Vector), so pgvector's vector-string parser would be applied
        # to the plain float distance value and fail.
        distance = IndexEntryModel.embedding.op("<=>", return_type=Float)(query_param)
        stmt = select(IndexEntryModel, distance.label("distance"))
        if repository_id is not None:
            stmt = stmt.where(IndexEntryModel.repository_id == repository_id)
        for key, value in filters.items():
            stmt = stmt.where(IndexEntryModel.entry_metadata.op("->>")(key) == str(value))
        stmt = stmt.order_by(distance.asc()).limit(limit)

        rows = await self._session.execute(stmt)
        results = [
            SearchResult(
                chunk_id=entry.document_id,
                score=1.0 - distance_value,
                text=entry.text,
                metadata=dict(entry.entry_metadata),
            )
            for entry, distance_value in rows.all()
        ]
        logger.debug("pgvector_search_completed", result_count=len(results), limit=limit)
        return results
