"""Application service that turns a request into a retrieval plan only."""

from collections.abc import Mapping

import structlog

from app.modules.query_engine.filters import MetadataFilterExtractor
from app.modules.query_engine.intent import IntentDetector, RuleBasedIntentDetector
from app.modules.query_engine.models import QueryIntent, QueryPlan, RetrievalStep, UserRequest
from app.modules.query_engine.parser import UserRequestParser
from app.modules.query_engine.planner import RepositoryResolver, RepositoryScopeResolver
from app.modules.query_engine.validators import UserRequestValidator
from app.modules.retrieval.models import SearchQuery

_STEP_PLANS: dict[QueryIntent, tuple[tuple[str, int], ...]] = {
    QueryIntent.SEARCH_CODE: (("code_search", 10),),
    QueryIntent.SEARCH_SYMBOL: (("code_search", 15), ("exact_file", 5)),
    QueryIntent.SEARCH_FILE: (("exact_file", 10), ("code_search", 5)),
    QueryIntent.SEARCH_DOCUMENTATION: (("code_search", 10),),
    QueryIntent.SEARCH_CONFIGURATION: (("code_search", 10), ("exact_file", 5)),
    QueryIntent.SEARCH_ARCHITECTURE: (("code_search", 10), ("related_files", 20)),
    QueryIntent.EXPLAIN: (("code_search", 10), ("related_files", 15)),
    QueryIntent.TRACE: (("code_search", 15), ("related_files", 20), ("exact_file", 5)),
    QueryIntent.GENERATE: (("code_search", 15), ("related_files", 10), ("exact_file", 5)),
    QueryIntent.REFACTOR: (("code_search", 15), ("related_files", 15)),
}


class QueryEngineService:
    """Coordinate deterministic request understanding without invoking retrieval."""

    def __init__(
        self,
        repository_resolver: RepositoryResolver,
        *,
        request_parser: UserRequestParser | None = None,
        intent_detector: IntentDetector | None = None,
        filter_extractor: MetadataFilterExtractor | None = None,
        validator: UserRequestValidator | None = None,
    ) -> None:
        self._request_parser = request_parser or UserRequestParser()
        self._intent_detector = intent_detector or RuleBasedIntentDetector()
        self._filter_extractor = filter_extractor or MetadataFilterExtractor()
        self._validator = validator or UserRequestValidator()
        self._scope_resolver = RepositoryScopeResolver(repository_resolver)
        self._logger = structlog.get_logger(__name__)

    async def plan(self, request: UserRequest) -> QueryPlan:
        """Validate, classify, scope, and translate a request to `SearchQuery`."""
        text = self._request_parser.parse_text(request)
        self._validator.validate(request, text)
        repository_id, warnings = await self._scope_resolver.resolve(request.repository_id, text)
        intent, confidence = self._intent_detector.detect(text)
        filters = self._filter_extractor.extract(text)
        query = SearchQuery(
            text=text,
            repository_id=repository_id,
            filters=filters,
            limit=request.preferences.get("limit", 10),
            offset=request.preferences.get("offset", 0),
        )
        steps = self._build_retrieval_steps(intent, text, filters)
        plan = QueryPlan(
            intent=intent,
            search_query=query,
            confidence=confidence,
            warnings=warnings,
            retrieval_steps=steps,
        )
        self._logger.info(
            "query_plan_created",
            intent=intent.value,
            repository_scoped=repository_id is not None,
            step_count=len(steps),
            warning_count=len(warnings),
        )
        return plan

    def _build_retrieval_steps(
        self,
        intent: QueryIntent,
        text: str,
        filters: Mapping[str, object],
    ) -> tuple[RetrievalStep, ...]:
        step_configs = _STEP_PLANS.get(intent, (("code_search", 10),))
        return tuple(
            RetrievalStep(source=source, query=text, limit=limit, filters=filters)
            for source, limit in step_configs
        )
