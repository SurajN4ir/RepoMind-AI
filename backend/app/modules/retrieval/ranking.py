"""Read-side ranking boundary built on configurable Reciprocal Rank Fusion."""

from collections.abc import Sequence

from app.modules.retrieval.models import SearchResult
from app.modules.retrieval.rrf import ReciprocalRankFusion


class HybridRanker:
    """Rank vector and keyword hits without embedding storage or query execution concerns."""

    def __init__(self, fusion: ReciprocalRankFusion | None = None) -> None:
        self._fusion = fusion or ReciprocalRankFusion()

    def rank(
        self,
        vector_results: Sequence[SearchResult],
        keyword_results: Sequence[SearchResult],
    ) -> tuple[SearchResult, ...]:
        """Fuse vector and keyword rankings into one deduplicated ordered result list."""
        return self._fusion.fuse(vector_results, keyword_results)
