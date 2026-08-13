"""Repository-scope resolution and QueryPlan assembly."""

from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from app.modules.query_engine.exceptions import UnknownRepositoryError
from app.modules.query_engine.models import RepositoryReference


class RepositoryResolver(Protocol):
    """Read-only port for resolving a query's repository scope."""

    async def list_repositories(self) -> Sequence[RepositoryReference]:
        """Return repositories available to the caller's planning context."""


class RepositoryScopeResolver:
    """Apply explicit-ID, single-repository, and explicit-name scope rules."""

    def __init__(self, resolver: RepositoryResolver) -> None:
        self._resolver = resolver

    async def resolve(
        self, repository_id: UUID | None, text: str
    ) -> tuple[UUID | None, tuple[str, ...]]:
        """Resolve scope, rejecting unknown explicit IDs and warning on ambiguity."""
        repositories = tuple(await self._resolver.list_repositories())
        if repository_id is not None:
            if any(repository.id == repository_id for repository in repositories):
                return repository_id, ()
            raise UnknownRepositoryError("The selected repository is unavailable.")
        if len(repositories) == 1:
            return repositories[0].id, ()
        matches = tuple(
            repository
            for repository in repositories
            if repository.name.casefold() in text.casefold()
        )
        if len(matches) == 1:
            return matches[0].id, ()
        if len(matches) > 1:
            return None, ("Repository name is ambiguous; search scope was not selected.",)
        if len(repositories) > 1:
            return None, (
                "Multiple repositories are available; specify a repository to narrow results.",
            )
        return None, ("No registered repositories are available for scope resolution.",)
