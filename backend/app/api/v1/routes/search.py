"""Minimal search endpoint that queries indexed file paths and content."""

from uuid import UUID

from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.api.v1.dependencies import FileContentStoreDependency

router = APIRouter(prefix="/search", tags=["search"])


class SearchResultItem(BaseModel):
    id: str
    repositoryId: str
    repositoryName: str
    filePath: str
    lineStart: int = 0
    lineEnd: int = 0
    content: str
    score: float


@router.get("", response_model=list[SearchResultItem])
async def search(
    store: FileContentStoreDependency,
    q: str = Query(..., min_length=1),
    repository_id: str | None = Query(None),
    limit: int = Query(default=10, ge=1, le=100),
) -> list[SearchResultItem]:
    """Search indexed files by path matching."""
    if repository_id:
        try:
            repo_uuid = UUID(repository_id)
        except ValueError:
            return []
        hashes = await store.get_file_path_hashes(repo_uuid)
    else:
        hashes = {}

    query_lower = q.lower()
    results: list[SearchResultItem] = []

    for file_path in hashes:
        if query_lower in file_path.lower():
            record = None
            if repository_id:
                record = await store.get_file_content(repo_uuid, file_path)
            results.append(
                SearchResultItem(
                    id=file_path,
                    repositoryId=repository_id or "",
                    repositoryName="",
                    filePath=file_path,
                    content=record.content[:500] if record and record.content else "",
                    score=1.0,
                )
            )

    results.sort(key=lambda r: -r.score)
    return results[:limit]
