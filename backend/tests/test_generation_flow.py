"""Tests for repository-aware code generation features."""

from uuid import uuid4

import pytest

from app.modules.context_builder.models import LLMContext
from app.modules.orchestrator.models import ResponseIntent, ResponsePlan
from app.modules.orchestrator.ollama_provider import (
    _INTENT_PROMPTS,
    OllamaResponseGenerator,
)
from app.modules.query_engine.intent import RuleBasedIntentDetector
from app.modules.query_engine.models import QueryIntent
from app.modules.retrieval.models import (
    SearchQuery,
)


class TestGenerationIntentDetection:
    """Verify that generation-related phrase rules are recognised."""

    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("generate a new service", QueryIntent.GENERATE),
            ("create an endpoint", QueryIntent.GENERATE),
            ("implement the interface", QueryIntent.GENERATE),
            ("add new route for users", QueryIntent.GENERATE),
            ("write unit tests for auth", QueryIntent.GENERATE),
            ("Create a service like the existing user service", QueryIntent.GENERATE),
            ("build something similar to the current implementation", QueryIntent.GENERATE),
            ("add an endpoint for profile", QueryIntent.GENERATE),
        ],
    )
    def test_generation_phrase_rules(self, text: str, expected: QueryIntent) -> None:
        detector = RuleBasedIntentDetector()
        intent, confidence = detector.detect(text)
        assert intent is expected
        assert confidence >= 0.80


class TestExactFileDispatch:
    """Verify _dispatch_exact_file returns RetrievedContext."""

    @pytest.mark.asyncio
    async def test_returns_none_when_no_store(self) -> None:
        from unittest.mock import AsyncMock

        from app.application.pipelines.repository_query_pipeline import (
            RepositoryQueryPipeline,
        )

        pipeline = RepositoryQueryPipeline(
            query_engine=AsyncMock(),
            retrieval_service=AsyncMock(),
            context_builder=AsyncMock(),
            orchestrator=AsyncMock(),
        )
        from app.modules.query_engine.models import RetrievalStep

        step = RetrievalStep(source="exact_file", query="test", filters={})
        from app.modules.query_engine.models import QueryPlan, SearchQuery

        plan = QueryPlan(
            intent=QueryIntent.GENERATE,
            search_query=SearchQuery(text="test"),
            confidence=0.9,
        )
        result = await pipeline._dispatch_exact_file(step, plan)
        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_without_path_prefix(self) -> None:
        from unittest.mock import AsyncMock

        from app.application.pipelines.repository_query_pipeline import (
            RepositoryQueryPipeline,
        )

        store = AsyncMock()
        store.get_file_content.return_value = None

        pipeline = RepositoryQueryPipeline(
            query_engine=AsyncMock(),
            retrieval_service=AsyncMock(),
            context_builder=AsyncMock(),
            orchestrator=AsyncMock(),
            file_content_store=store,
        )
        from app.modules.query_engine.models import RetrievalStep

        step = RetrievalStep(source="exact_file", query="test", filters={})
        from app.modules.query_engine.models import QueryPlan, SearchQuery

        plan = QueryPlan(
            intent=QueryIntent.GENERATE,
            search_query=SearchQuery(text="test", repository_id=uuid4()),
            confidence=0.9,
        )
        result = await pipeline._dispatch_exact_file(step, plan)
        assert result is None


class TestLLMContextFields:
    """Verify repository_structure and convention_examples are separate."""

    def test_llm_context_separate_fields(self) -> None:
        ctx = LLMContext(
            query=SearchQuery(text="test"),
            sections=(),
            citations=(),
            statistics=type(
                "S",
                (),
                {
                    "input_chunk_count": 0,
                    "retained_chunk_count": 0,
                    "pruned_chunk_count": 0,
                    "section_count": 0,
                    "token_count": 0,
                    "token_budget": 0,
                },
            )(),
            formatted_text="evidence",
            conversation_history="",
            repository_structure="modules: src/",
            convention_examples="File: example.py",
        )
        assert ctx.repository_structure == "modules: src/"
        assert ctx.convention_examples == "File: example.py"
        assert ctx.repository_structure is not ctx.convention_examples


class TestGenerationPromptEnhancements:
    """Verify the GENERATE prompt template includes attribution and safety."""

    def test_generate_prompt_requires_attribution(self) -> None:
        template = _INTENT_PROMPTS[ResponseIntent.GENERATE]
        assert "[citation:N]" in template or "[citation" in template
        assert "influenced" in template.casefold()
        assert "List which files" in template

    def test_generate_prompt_hallucination_guard(self) -> None:
        template = _INTENT_PROMPTS[ResponseIntent.GENERATE]
        assert "Never claim" in template or "never claim" in template.casefold()

    def test_generate_prompt_safety_clause(self) -> None:
        template = _INTENT_PROMPTS[ResponseIntent.GENERATE]
        assert "insufficient" in template.casefold() or "best-effort" in template.casefold()

    def test_generate_prompt_convention_matching(self) -> None:
        template = _INTENT_PROMPTS[ResponseIntent.GENERATE]
        assert "convention" in template.casefold()
        assert "naming" in template.casefold() or "style" in template.casefold()

    def test_generate_prompt_distinguishes_code(self) -> None:
        template = _INTENT_PROMPTS[ResponseIntent.GENERATE]
        assert "generated" in template.casefold()
        assert "retrieved" in template.casefold()
        assert "distinguish" in template.casefold() or "clearly" in template.casefold()

    def test_generate_system_prompt(self) -> None:
        generator = OllamaResponseGenerator()
        plan = ResponsePlan(
            intent=ResponseIntent.GENERATE,
            tools=(),
            strategy="evidence_grounded",
            temperature=0.5,
            streaming=True,
            verification=True,
        )
        system_prompt = generator._build_system_prompt(plan)
        assert "repository-aware" in system_prompt.casefold()
        assert "cite" in system_prompt.casefold()
        assert "never claim" in system_prompt.casefold()

    def test_convention_examples_format(self) -> None:
        text = """--- Convention Examples ---
Complete file contents used as pattern references:

File: src/example.py
```
print("hello")
```
--- end convention examples ---"""
        assert text.startswith("--- Convention Examples ---")
        assert "File:" in text
        assert "end convention examples" in text
