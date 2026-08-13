"""Application service for LLM-neutral evidence context construction."""

from collections.abc import Sequence

import structlog

from app.modules.context_builder.budget import BudgetAllocator, TokenCounter, WhitespaceTokenCounter
from app.modules.context_builder.formatter import ContextFormatter, SourceEvidenceFormatter
from app.modules.context_builder.grouping import EvidenceGrouper
from app.modules.context_builder.models import ContextStatistics, EvidenceChunk, LLMContext
from app.modules.context_builder.ordering import EvidenceOrderer
from app.modules.context_builder.pruning import EvidencePruner
from app.modules.retrieval.models import RetrievedContext


class ContextBuilderService:
    """Compose retrieved evidence using independently replaceable policies."""

    def __init__(
        self,
        *,
        token_counter: TokenCounter | None = None,
        budget_allocator: BudgetAllocator | None = None,
        pruner: EvidencePruner | None = None,
        orderer: EvidenceOrderer | None = None,
        grouper: EvidenceGrouper | None = None,
        formatter: ContextFormatter | None = None,
    ) -> None:
        self._token_counter = token_counter or WhitespaceTokenCounter()
        self._budget_allocator = budget_allocator or BudgetAllocator()
        self._pruner = pruner or EvidencePruner()
        self._orderer = orderer or EvidenceOrderer()
        self._grouper = grouper or EvidenceGrouper()
        self._formatter = formatter or SourceEvidenceFormatter()
        self._logger = structlog.get_logger(__name__)

    async def build(
        self,
        context: RetrievedContext,
        *,
        retrieval_results: Sequence[RetrievedContext] | None = None,
        conversation_history: str = "",
        repository_structure: str = "",
        convention_examples: str = "",
    ) -> LLMContext:
        """Convert retrieval output(s) to a bounded, formatted evidence context.

        When ``retrieval_results`` is provided, chunks from all results are
        merged before pruning and budgeting. The primary ``context`` serves as
        the source of the query and citations; additional results contribute
        supporting evidence at lower priority.
        """
        all_results = [context]
        if retrieval_results:
            seen_query_ids = {id(context.query)}
            for result in retrieval_results:
                if id(result.query) not in seen_query_ids:
                    all_results.append(result)
                    seen_query_ids.add(id(result.query))

        candidates = self._merge_candidates(all_results)
        pruned = self._pruner.prune(candidates)
        ordered = self._orderer.order(pruned)
        retained = self._budget_allocator.allocate(ordered)
        sections = self._grouper.group(retained)
        output_citations = tuple(chunk.citation for chunk in retained)
        total_input = sum(len(r.results) for r in all_results)
        total_retained = len(retained)
        total_pruned = total_input - total_retained
        statistics = ContextStatistics(
            input_chunk_count=total_input,
            retained_chunk_count=total_retained,
            pruned_chunk_count=total_pruned,
            section_count=len(sections),
            token_count=sum(chunk.token_count for chunk in retained),
            token_budget=self._budget_allocator.token_budget,
        )
        built = LLMContext(
            query=context.query,
            sections=sections,
            citations=output_citations,
            statistics=statistics,
            formatted_text=self._formatter.format(sections),
            conversation_history=conversation_history,
            repository_structure=repository_structure,
            convention_examples=convention_examples,
        )
        self._logger.info(
            "llm_context_built",
            input_chunk_count=statistics.input_chunk_count,
            retained_chunk_count=statistics.retained_chunk_count,
            token_count=statistics.token_count,
        )
        return built

    def _merge_candidates(
        self,
        contexts: Sequence[RetrievedContext],
    ) -> tuple[EvidenceChunk, ...]:
        seen_ids: set[str] = set()
        merged: list[EvidenceChunk] = []
        for position, ctx in enumerate(contexts):
            priority_scale = 1.0 / (1.0 + position)
            citations = {c.chunk_id: c for c in ctx.citations}
            for result in ctx.results:
                if result.chunk_id in seen_ids:
                    continue
                citation = citations.get(result.chunk_id)
                if citation is None:
                    continue
                seen_ids.add(result.chunk_id)
                merged.append(
                    EvidenceChunk(
                        chunk_id=result.chunk_id,
                        text=result.text,
                        metadata=result.metadata,
                        citation=citation,
                        token_count=self._token_counter.count(result.text),
                        priority=result.score * priority_scale,
                    )
                )
        return tuple(merged)
