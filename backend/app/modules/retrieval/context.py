"""Build agent-ready retrieval context without invoking any agent or language model."""

from app.modules.retrieval.models import (
    Citation,
    RetrievalStatistics,
    RetrievedContext,
    SearchQuery,
    SearchResult,
)


class ContextBuilder:
    """Assemble ordered results and compact source citations for downstream consumers."""

    def build(
        self,
        query: SearchQuery,
        results: tuple[SearchResult, ...],
        statistics: RetrievalStatistics,
    ) -> RetrievedContext:
        """Create a retrieval context from already ranked and paginated results."""
        citations = tuple(self._citation(result) for result in results)
        return RetrievedContext(
            query=query,
            results=results,
            citations=citations,
            statistics=statistics,
        )

    @staticmethod
    def _citation(result: SearchResult) -> Citation:
        line_range = result.metadata.get("line_range")
        return Citation(
            chunk_id=result.chunk_id,
            file_path=_string_or_none(result.metadata.get("file_path")),
            qualified_symbol_name=_string_or_none(result.metadata.get("qualified_symbol_name")),
            line_start=_line_value(line_range, "start"),
            line_end=_line_value(line_range, "end"),
        )


def _string_or_none(value: object) -> str | None:
    return value if isinstance(value, str) else None


def _line_value(line_range: object, key: str) -> int | None:
    if isinstance(line_range, dict) and isinstance(line_range.get(key), int):
        return line_range[key]
    return None
