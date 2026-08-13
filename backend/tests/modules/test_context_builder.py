"""Async unit tests for LLM-neutral evidence context construction."""

import pytest

from app.modules.context_builder.budget import BudgetAllocator
from app.modules.context_builder.service import ContextBuilderService
from app.modules.retrieval.models import (
    Citation,
    RetrievalStatistics,
    RetrievedContext,
    SearchQuery,
    SearchResult,
)


def _context(*results: SearchResult) -> RetrievedContext:
    citations = tuple(
        Citation(
            chunk_id=result.chunk_id,
            file_path=str(result.metadata.get("file_path", "src/unknown.py")),
            qualified_symbol_name=str(
                result.metadata.get("qualified_symbol_name", result.chunk_id)
            ),
            line_start=int(result.metadata.get("line_start", 1)),
            line_end=int(result.metadata.get("line_end", 2)),
        )
        for result in results
    )
    return RetrievedContext(
        query=SearchQuery("authentication"),
        results=results,
        citations=citations,
        statistics=RetrievalStatistics(0, 0, 0.0, 0.0, 0.0),
    )


def _result(chunk_id: str, score: float, text: str, path: str, line: int) -> SearchResult:
    return SearchResult(
        chunk_id=chunk_id,
        score=score,
        text=text,
        metadata={
            "file_path": path,
            "qualified_symbol_name": chunk_id,
            "line_start": line,
            "line_end": line + 1,
        },
    )


@pytest.mark.asyncio
async def test_context_builder_groups_orders_and_preserves_citations() -> None:
    context = _context(
        _result("later", 0.8, "def later(): return authenticate_user()", "src/auth.py", 20),
        _result("first", 0.9, "def first(): return authenticate_user()", "src/auth.py", 5),
        _result(
            "config",
            0.7,
            "AUTH_ENABLED = True and authentication is configured",
            "src/config.py",
            1,
        ),
    )
    built = await ContextBuilderService().build(context)
    assert [section.title for section in built.sections] == [
        "File: src/auth.py",
        "File: src/config.py",
    ]
    assert [chunk.chunk_id for chunk in built.sections[0].chunks] == ["first", "later"]
    assert [citation.chunk_id for citation in built.citations] == ["first", "later", "config"]
    assert "Symbol: first" in built.formatted_text


@pytest.mark.asyncio
async def test_context_builder_prunes_duplicates_and_trivial_snippets() -> None:
    duplicate_text = "def validate_token(token): return token is not None"
    context = _context(
        _result("one", 1.0, duplicate_text, "src/auth.py", 1),
        _result("two", 0.9, duplicate_text, "src/auth.py", 5),
        _result("tiny", 0.8, "pass", "src/auth.py", 7),
    )
    built = await ContextBuilderService().build(context)
    assert built.statistics.retained_chunk_count == 1
    assert built.statistics.pruned_chunk_count == 2
    assert built.citations[0].chunk_id == "one"


@pytest.mark.asyncio
async def test_context_builder_applies_budget_to_oversized_retrieval_set() -> None:
    context = _context(
        _result("first", 1.0, "once twice thrice forth", "src/a.py", 1),
        _result("second", 0.9, "five six seven eight", "src/b.py", 1),
        _result("third", 0.8, "nine ten eleven twelve", "src/c.py", 1),
    )
    built = await ContextBuilderService(budget_allocator=BudgetAllocator(8)).build(context)
    assert built.statistics.token_count == 8
    assert [citation.chunk_id for citation in built.citations] == ["first", "second"]


@pytest.mark.asyncio
async def test_context_builder_handles_empty_context_stably() -> None:
    built = await ContextBuilderService().build(_context())
    assert built.sections == ()
    assert built.citations == ()
    assert built.formatted_text == ""
    assert built.statistics.input_chunk_count == 0
