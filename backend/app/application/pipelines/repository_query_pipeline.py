"""Application pipeline composing domain modules into a read-side query workflow."""

from __future__ import annotations

import json
import traceback
from collections.abc import AsyncIterator, Sequence
from datetime import UTC, datetime
from uuid import UUID

import structlog

from app.application.exceptions import PipelineError
from app.application.pipelines.models import QueryPipelineContext, QueryResult
from app.modules.context_builder.budget import WhitespaceTokenCounter
from app.modules.context_builder.models import LLMContext
from app.modules.context_builder.service import ContextBuilderService
from app.modules.conversation.format import format_conversation_history
from app.modules.conversation.store import ConversationStore
from app.modules.indexing.models import FileDependencyRecord
from app.modules.indexing.repository import DependencyRepository, FileContentRepository
from app.modules.insight.repository_context_formatter import RepositoryContextFormatter
from app.modules.orchestrator.models import (
    GeneratedResponse,
    StreamEvent,
    StreamEventType,
)
from app.modules.orchestrator.service import OrchestratorService
from app.modules.query_engine.models import QueryIntent, QueryPlan, RetrievalStep, UserRequest
from app.modules.query_engine.service import QueryEngineService
from app.modules.retrieval.models import (
    Citation,
    RetrievalStatistics,
    RetrievedContext,
    SearchQuery,
    SearchResult,
)
from app.modules.retrieval.service import RetrievalService

logger = structlog.get_logger(__name__)


class RepositoryQueryPipeline:
    """Coordinate the full read-side query workflow.

    Composes domain services into a single fault-tolerant pipeline that
    sequences query planning, hybrid retrieval, evidence context building,
    and LLM response generation — superseding orchestration that previously
    lived inside application or domain services.
    """

    _MAX_RELATED_FILES = 10
    _EXPANSION_DEPTH = 1
    _CONVENTION_BUDGET = 2000

    def __init__(
        self,
        query_engine: QueryEngineService,
        retrieval_service: RetrievalService,
        context_builder: ContextBuilderService,
        orchestrator: OrchestratorService,
        *,
        dependency_store: DependencyRepository | None = None,
        file_content_store: FileContentRepository | None = None,
        conversation_store: ConversationStore | None = None,
    ) -> None:
        self._query_engine = query_engine
        self._retrieval_service = retrieval_service
        self._context_builder = context_builder
        self._orchestrator = orchestrator
        self._dependency_store = dependency_store
        self._file_content_store = file_content_store
        self._conversation_store = conversation_store

    async def execute(self, request: UserRequest) -> QueryResult:
        """Plan, retrieve, build context, and respond — returning a structured result."""
        context = QueryPipelineContext(request=request, started_at=datetime.now(UTC))
        try:
            await self._init_conversation(context)
            plan = await self._plan(context)
            retrieved = await self._retrieve(context, plan)
            llm_context = await self._build_context(context, retrieved)
            await self._respond(context, llm_context)
            await self._persist_conversation(context)
            return self._build_result(context, success=True)
        except Exception:
            logger.exception("query_pipeline_execution_failed")
            context.errors.append(traceback.format_exc())
            return self._build_result(context, success=False)

    async def stream(self, request: UserRequest) -> AsyncIterator[StreamEvent]:
        """Plan, retrieve, build context, and stream a response.

        Yields ``StreamEvent`` objects that the transport layer can
        serialise as Server-Sent Events.  If the setup steps (plan,
        retrieve, build) fail, the generator raises an exception that
        the caller should catch.  If streaming itself fails, an END
        event with no response is emitted so the client receives a
        well-formed termination signal.
        """
        context = QueryPipelineContext(request=request, started_at=datetime.now(UTC))
        try:
            await self._init_conversation(context)
            plan = await self._plan(context)
            retrieved = await self._retrieve(context, plan)
            llm_context = await self._build_context(context, retrieved)
        except Exception as exc:
            logger.exception("query_pipeline_stream_setup_failed")
            context.errors.append(traceback.format_exc())
            raise PipelineError(f"Query pipeline setup failed: {exc}") from exc

        try:
            async for event in self._orchestrator.stream(llm_context):
                yield event
            await self._persist_conversation(context)
        except Exception:
            logger.exception("query_pipeline_stream_failed")
            context.errors.append(traceback.format_exc())
            yield StreamEvent(type=StreamEventType.END, response=None)

    async def _plan(self, context: QueryPipelineContext) -> QueryPlan:
        try:
            plan = await self._query_engine.plan(context.request)
            context.plan = plan
            logger.info("query_pipeline_planned", intent=plan.intent.value)
            return plan
        except Exception as exc:
            raise PipelineError(f"Query planning step failed: {exc}") from exc

    async def _retrieve(self, context: QueryPipelineContext, plan: QueryPlan) -> RetrievedContext:
        steps = plan.retrieval_steps
        if not steps:
            retrieved = await self._retrieval_service.retrieve(plan.search_query)
            context.retrieved_context = retrieved
            context.retrieval_results = [retrieved]
            logger.info("query_pipeline_retrieved", result_count=len(retrieved.results))
            return retrieved

        results: list[RetrievedContext] = []

        for step in steps:
            try:
                if step.source == "code_search":
                    result = await self._dispatch_code_search(step, plan)
                    results.append(result)

                elif step.source == "related_files" and self._dependency_store is not None:
                    expanded = await self._dispatch_related_files(step, plan, results)
                    results.extend(expanded)

                elif step.source == "exact_file" and self._file_content_store is not None:
                    result = await self._dispatch_exact_file(step, plan)
                    if result is not None:
                        results.append(result)

            except Exception as exc:
                logger.warning(
                    "query_pipeline_retrieval_step_failed",
                    source=step.source,
                    error=str(exc),
                )

        primary = (
            results[0] if results else await self._retrieval_service.retrieve(plan.search_query)
        )
        if not results:
            results.append(primary)
        context.retrieved_context = primary
        context.retrieval_results = results
        logger.info(
            "query_pipeline_retrieved",
            step_count=len(steps),
            result_count=sum(len(r.results) for r in results),
        )
        return primary

    async def _dispatch_code_search(self, step: RetrievalStep, plan: QueryPlan) -> RetrievedContext:
        search_query = SearchQuery(
            text=step.query,
            repository_id=plan.search_query.repository_id,
            filters=step.filters,
            limit=step.limit,
        )
        result = await self._retrieval_service.retrieve(search_query)
        logger.info(
            "query_pipeline_retrieved_step",
            source=step.source,
            result_count=len(result.results),
        )
        return result

    async def _dispatch_related_files(
        self,
        step: RetrievalStep,
        plan: QueryPlan,
        existing_results: list[RetrievedContext],
    ) -> list[RetrievedContext]:
        repo_id = plan.search_query.repository_id
        if repo_id is None or self._dependency_store is None:
            return []

        records = await self._dependency_store.get_dependencies(repo_id)
        logger.info("query_pipeline_related_files_step", edge_count=len(records))

        primary_file_paths = {
            result.metadata.get("file_path", "")
            for ctx in existing_results
            for result in ctx.results
        }
        primary_file_paths.discard("")

        related_paths = self._collect_related_paths(records, primary_file_paths)

        expanded: list[RetrievedContext] = []
        if related_paths:
            for path in sorted(related_paths)[: self._MAX_RELATED_FILES]:
                try:
                    search_query = SearchQuery(
                        text=path,
                        repository_id=repo_id,
                        filters={"file_path_prefix": path},
                        limit=5,
                    )
                    result = await self._retrieval_service.retrieve(search_query)
                    if result.results:
                        expanded.append(result)
                except Exception:
                    continue

        return expanded

    @staticmethod
    def _collect_related_paths(
        records: Sequence[FileDependencyRecord],
        primary_paths: set[str],
    ) -> set[str]:
        related: set[str] = set()
        for record in records:
            if record.source_path in primary_paths:
                related.add(record.target_path)
            if record.target_path in primary_paths:
                related.add(record.source_path)
        related.difference_update(primary_paths)
        return related

    async def _dispatch_exact_file(
        self,
        step: RetrievalStep,
        plan: QueryPlan,
    ) -> RetrievedContext | None:
        repo_id = plan.search_query.repository_id
        if repo_id is None or self._file_content_store is None:
            return None

        path_prefix = step.filters.get("file_path_prefix", "")
        if not isinstance(path_prefix, str) or not path_prefix:
            return None

        record = await self._file_content_store.get_file_content(repo_id, path_prefix.rstrip("/"))
        if record is None:
            return None

        result = SearchResult(
            chunk_id=f"exact:{record.file_path}",
            score=1.0,
            text=record.content,
            metadata={"file_path": record.file_path},
        )
        citation = Citation(
            chunk_id=result.chunk_id,
            file_path=record.file_path,
            qualified_symbol_name=None,
            line_start=None,
            line_end=None,
        )
        logger.info("query_pipeline_exact_file_step", path=record.file_path)
        return RetrievedContext(
            query=plan.search_query,
            results=(result,),
            citations=(citation,),
            statistics=RetrievalStatistics(
                vector_hits=0,
                keyword_hits=0,
                rrf_time_seconds=0.0,
                retrieval_time_seconds=0.0,
                rerank_time_seconds=0.0,
            ),
        )

    async def _init_conversation(self, context: QueryPipelineContext) -> None:
        if self._conversation_store is None:
            return
        repo_id = context.request.repository_id
        if repo_id is None:
            return
        conversation = await self._conversation_store.get_or_create(repo_id)
        context.conversation_id = conversation.id
        messages = await self._conversation_store.get_messages(conversation.id)
        context.conversation_messages = list(messages)
        logger.info(
            "conversation_loaded",
            conversation_id=str(conversation.id),
            message_count=len(messages),
        )

    async def _persist_conversation(self, context: QueryPipelineContext) -> None:
        if self._conversation_store is None or context.conversation_id is None:
            return
        try:
            await self._conversation_store.add_message(
                context.conversation_id,
                "user",
                context.request.text,
            )
            if context.response is not None:
                citation_json = json.dumps(
                    [
                        {
                            "file_path": c.file_path,
                            "line_start": c.line_start,
                            "line_end": c.line_end,
                        }
                        for c in context.response.citations
                        if c.file_path
                    ]
                )
                await self._conversation_store.add_message(
                    context.conversation_id,
                    "assistant",
                    context.response.text,
                    citation_json=citation_json,
                )
        except Exception:
            logger.warning("conversation_persistence_failed", exc_info=True)

    async def _build_context(
        self, context: QueryPipelineContext, retrieved: RetrievedContext
    ) -> LLMContext:
        try:
            history = format_conversation_history(context.conversation_messages)

            repo_id = context.plan.search_query.repository_id if context.plan else None

            structure_text = ""
            if (
                context.plan is not None
                and context.plan.intent is QueryIntent.SEARCH_ARCHITECTURE
                and self._dependency_store is not None
                and self._file_content_store is not None
                and repo_id is not None
            ):
                dependencies = await self._dependency_store.get_dependencies(repo_id)
                file_paths = list(
                    (await self._file_content_store.get_file_path_hashes(repo_id)).keys()
                )
                formatter = RepositoryContextFormatter()
                structure_text = formatter.format(
                    dependencies=dependencies,
                    file_paths=file_paths,
                    retrieval_results=context.retrieval_results,
                )

            conventions_text = ""
            if (
                context.plan is not None
                and context.plan.intent in (QueryIntent.GENERATE, QueryIntent.REFACTOR)
                and self._file_content_store is not None
                and repo_id is not None
            ):
                conventions_text = await self._collect_convention_examples(
                    repo_id, context.retrieval_results
                )

            llm_context = await self._context_builder.build(
                retrieved,
                retrieval_results=context.retrieval_results,
                conversation_history=history,
                repository_structure=structure_text,
                convention_examples=conventions_text,
            )
            context.llm_context = llm_context
            logger.info(
                "query_pipeline_context_built",
                token_count=llm_context.statistics.token_count,
            )
            return llm_context
        except Exception as exc:
            raise PipelineError(f"Context building step failed: {exc}") from exc

    async def _collect_convention_examples(
        self,
        repo_id: UUID,
        retrieval_results: list[RetrievedContext],
    ) -> str:
        if not retrieval_results:
            return ""
        token_counter = WhitespaceTokenCounter()
        path_counts: dict[str, int] = {}
        for result in retrieval_results:
            for search_result in result.results:
                fp = search_result.metadata.get("file_path")
                if isinstance(fp, str):
                    path_counts[fp] = path_counts.get(fp, 0) + 1

        ranked = sorted(path_counts, key=path_counts.__getitem__, reverse=True)

        examples: list[str] = []
        used_tokens = 0
        for file_path in ranked:
            record = await self._file_content_store.get_file_content(repo_id, file_path)
            if record is None:
                continue
            tokens = token_counter.count(record.content)
            if used_tokens + tokens > self._CONVENTION_BUDGET:
                continue
            used_tokens += tokens
            examples.append(f"File: {record.file_path}\n```\n{record.content}\n```")

        if not examples:
            return ""

        lines = [
            "--- Convention Examples ---",
            "Complete file contents used as pattern references:",
            "",
        ]
        lines.extend(examples)
        lines.append("--- end convention examples ---")
        return "\n".join(lines)

    async def _respond(
        self, context: QueryPipelineContext, llm_context: LLMContext
    ) -> GeneratedResponse:
        try:
            response = await self._orchestrator.respond(llm_context)
            context.response = response
            logger.info(
                "query_pipeline_responded",
                intent=response.reasoning_metadata.get("response_intent"),
            )
            return response
        except Exception as exc:
            raise PipelineError(f"Response generation step failed: {exc}") from exc

    def _build_result(self, context: QueryPipelineContext, *, success: bool) -> QueryResult:
        now = datetime.now(UTC)
        elapsed = (now - (context.started_at or now)).total_seconds()
        return QueryResult(
            request=context.request,
            success=success,
            response=context.response,
            plan=context.plan,
            retrieved_context=context.retrieved_context,
            llm_context=context.llm_context,
            elapsed_seconds=elapsed,
            errors=tuple(context.errors),
        )
