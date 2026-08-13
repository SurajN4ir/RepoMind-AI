"""Configurable Reciprocal Rank Fusion for hybrid retrieval result lists."""

from collections.abc import Sequence

from app.modules.retrieval.models import SearchResult


class ReciprocalRankFusion:
    """Fuse ranked result lists while preserving document metadata and deduplicating IDs."""

    def __init__(self, fusion_constant: int = 60) -> None:
        if fusion_constant < 1:
            raise ValueError("RRF fusion constant must be positive.")
        self._fusion_constant = fusion_constant

    def fuse(self, *ranked_lists: Sequence[SearchResult]) -> tuple[SearchResult, ...]:
        """Merge ranked lists using ``sum(1 / (k + rank))`` with one result per chunk ID."""
        scores: dict[str, float] = {}
        representative: dict[str, SearchResult] = {}
        for ranked_results in ranked_lists:
            for rank, result in enumerate(ranked_results, start=1):
                scores[result.chunk_id] = scores.get(result.chunk_id, 0.0) + 1 / (
                    self._fusion_constant + rank
                )
                representative.setdefault(result.chunk_id, result)
        return tuple(
            SearchResult(
                chunk_id=chunk_id,
                score=score,
                text=representative[chunk_id].text,
                metadata=representative[chunk_id].metadata,
            )
            for chunk_id, score in sorted(scores.items(), key=lambda item: (-item[1], item[0]))
        )
