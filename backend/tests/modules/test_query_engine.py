"""Async unit tests for pure Query Engine planning."""

from collections.abc import Sequence

import pytest

from app.modules.query_engine.exceptions import InvalidUserRequestError, UnknownRepositoryError
from app.modules.query_engine.models import QueryIntent, RepositoryReference, UserRequest
from app.modules.query_engine.planner import RepositoryResolver
from app.modules.query_engine.service import QueryEngineService
from app.shared.identifiers.uuid import new_uuid


class _Resolver(RepositoryResolver):
    def __init__(self, repositories: Sequence[RepositoryReference]) -> None:
        self._repositories = repositories

    async def list_repositories(self) -> Sequence[RepositoryReference]:
        return self._repositories


@pytest.mark.asyncio
async def test_planning_detects_symbol_intent_extracts_filters_and_auto_scopes() -> None:
    repository_id = new_uuid()
    service = QueryEngineService(_Resolver((RepositoryReference(repository_id, "api"),)))
    plan = await service.plan(
        UserRequest("Show me Python authentication middleware inside auth folder")
    )
    assert plan.intent is QueryIntent.SEARCH_SYMBOL
    assert plan.search_query.repository_id == repository_id
    assert plan.search_query.filters == {"language": "python", "file_path_prefix": "auth/"}
    assert plan.search_query.text == "Python authentication middleware inside auth folder"
    assert plan.warnings == ()


@pytest.mark.asyncio
async def test_planning_resolves_explicit_repository_name_when_multiple_exist() -> None:
    api_id, web_id = new_uuid(), new_uuid()
    service = QueryEngineService(
        _Resolver((RepositoryReference(api_id, "api"), RepositoryReference(web_id, "web")))
    )
    plan = await service.plan(UserRequest("Find docs in the web repository"))
    assert plan.intent is QueryIntent.SEARCH_DOCUMENTATION
    assert plan.search_query.repository_id == web_id


@pytest.mark.asyncio
async def test_planning_warns_when_multiple_repositories_are_ambiguous() -> None:
    service = QueryEngineService(
        _Resolver((RepositoryReference(new_uuid(), "api"), RepositoryReference(new_uuid(), "web")))
    )
    plan = await service.plan(UserRequest("Find authentication"))
    assert plan.search_query.repository_id is None
    assert "Multiple repositories" in plan.warnings[0]


@pytest.mark.asyncio
async def test_planning_rejects_unknown_explicit_repository() -> None:
    service = QueryEngineService(_Resolver(()))
    with pytest.raises(UnknownRepositoryError):
        await service.plan(UserRequest("Find auth", repository_id=new_uuid()))


@pytest.mark.asyncio
async def test_planning_rejects_blank_text_and_invalid_preferences() -> None:
    service = QueryEngineService(_Resolver(()))
    with pytest.raises(InvalidUserRequestError):
        await service.plan(UserRequest("   "))
    with pytest.raises(InvalidUserRequestError):
        await service.plan(UserRequest("auth", preferences={"limit": -1}))


@pytest.mark.asyncio
async def test_planning_preserves_pagination_preferences() -> None:
    service = QueryEngineService(_Resolver(()))
    plan = await service.plan(UserRequest("configuration", preferences={"limit": 5, "offset": 2}))
    assert plan.intent is QueryIntent.SEARCH_CONFIGURATION
    assert plan.search_query.limit == 5
    assert plan.search_query.offset == 2
