"""HTTP transport for the Repository bounded context (moved from domain module)."""

from pathlib import PurePosixPath
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Response, status
from pydantic import BaseModel

from app.api.v1.dependencies import (
    ActivityStoreDependency,
    DependencyStoreDependency,
    FileContentStoreDependency,
    RepositoryAppServiceDependency,
)
from app.application.exceptions import ApplicationError
from app.application.http_exceptions import to_http_exception
from app.modules.repository.schemas import (
    CreateRepositoryRequest,
    RepositoryListResponse,
    RepositoryResponse,
    UpdateRepositoryRequest,
)
from app.shared.database.pagination import PaginationParams

router = APIRouter(prefix="/repositories", tags=["repositories"])


@router.post("", response_model=RepositoryResponse, status_code=status.HTTP_201_CREATED)
async def create_repository(
    request: CreateRepositoryRequest,
    service: RepositoryAppServiceDependency,
    response: Response,
) -> RepositoryResponse:
    """Register repository metadata without performing any ingestion work."""
    try:
        repository = await service.register(request)
    except ApplicationError as exc:
        raise to_http_exception(exc) from exc
    response.headers["Location"] = f"/api/v1/repositories/{repository.id}"
    return RepositoryResponse.model_validate(repository)


@router.get("", response_model=RepositoryListResponse)
async def list_repositories(
    service: RepositoryAppServiceDependency,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
) -> RepositoryListResponse:
    """List registered repositories using offset pagination."""
    try:
        result = await service.list(PaginationParams(page=page, page_size=page_size))
    except ApplicationError as exc:
        raise to_http_exception(exc) from exc
    return RepositoryListResponse(
        items=[RepositoryResponse.model_validate(item) for item in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        total_pages=result.total_pages,
    )


@router.get("/{repository_id}", response_model=RepositoryResponse)
async def get_repository(
    repository_id: UUID,
    service: RepositoryAppServiceDependency,
    store: FileContentStoreDependency,
) -> RepositoryResponse:
    """Return one registered repository with computed indexing metrics."""
    try:
        repo = await service.get(repository_id)
        response = RepositoryResponse.model_validate(repo)
        response.indexed_file_count = await store.get_file_count(repository_id)
        return response
    except ApplicationError as exc:
        raise to_http_exception(exc) from exc


@router.patch("/{repository_id}", response_model=RepositoryResponse)
async def update_repository(
    repository_id: UUID,
    request: UpdateRepositoryRequest,
    service: RepositoryAppServiceDependency,
) -> RepositoryResponse:
    """Update repository metadata or its lifecycle status."""
    try:
        return RepositoryResponse.model_validate(await service.update(repository_id, request))
    except ApplicationError as exc:
        raise to_http_exception(exc) from exc


@router.delete("/{repository_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_repository(
    repository_id: UUID,
    service: RepositoryAppServiceDependency,
) -> Response:
    """Delete a repository record; external repository work is out of scope."""
    try:
        await service.delete(repository_id)
    except ApplicationError as exc:
        raise to_http_exception(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


class FileContentResponse(BaseModel):
    """File content returned by the file content endpoint."""

    path: str
    content: str


def _validate_file_path(file_path: str) -> str:
    normalized = file_path.replace("\\", "/")
    parts = PurePosixPath(normalized).parts
    if ".." in parts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file path: path traversal is not allowed",
        )
    return normalized


@router.get("/{repository_id}/files/content", response_model=FileContentResponse)
async def get_file_content(
    repository_id: UUID,
    store: FileContentStoreDependency,
    file_path: str = Query(..., description="Path to the file within the repository"),
) -> FileContentResponse:
    """Return the full content of a file within a repository."""
    safe_path = _validate_file_path(file_path)
    record = await store.get_file_content(repository_id, safe_path)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File '{file_path}' not found in repository {repository_id}",
        )
    return FileContentResponse(path=record.file_path, content=record.content)


class GraphNode(BaseModel):
    """One node in the dependency graph."""

    id: str
    label: str
    type: str


class GraphEdge(BaseModel):
    """One directed edge in the dependency graph."""

    source: str
    target: str


class GraphResponse(BaseModel):
    """Dependency graph nodes and edges for visualisation."""

    nodes: list[GraphNode]
    edges: list[GraphEdge]


class FileNodeResponse(BaseModel):
    """One file or directory in the file tree."""

    name: str
    type: str
    path: str
    children: list["FileNodeResponse"] | None = None


class FileTreeResponse(BaseModel):
    """File tree structure for a repository."""

    items: list[FileNodeResponse]


def _build_file_tree(file_paths: list[str]) -> list[FileNodeResponse]:
    """Build a hierarchical file tree from flat file path list."""
    root: dict[str, object] = {}

    for path in sorted(file_paths):
        parts = path.split("/")
        current = root
        for i, part in enumerate(parts):
            is_file = i == len(parts) - 1
            if part not in current:
                current[part] = {
                    "__type": "file" if is_file else "directory",
                    "__path": "/".join(parts[: i + 1]),
                    "children": {},
                }
            current = current[part]["children"]

    def _to_node(name: str, data: dict) -> FileNodeResponse:
        node_type = data["__type"]
        path = data["__path"]
        children = data.get("children", {})
        return FileNodeResponse(
            name=name,
            type=node_type,
            path=path,
            children=[_to_node(k, v) for k, v in children.items()] if children else None,
        )

    return [_to_node(k, v) for k, v in root.items()]


@router.get("/{repository_id}/files", response_model=FileTreeResponse)
async def get_repository_file_tree(
    repository_id: UUID,
    store: FileContentStoreDependency,
) -> FileTreeResponse:
    """Return the hierarchical file tree for a repository."""
    hashes = await store.get_file_path_hashes(repository_id)
    paths = list(hashes.keys())
    items = _build_file_tree(paths)
    return FileTreeResponse(items=items)


@router.get("/{repository_id}/graph", response_model=GraphResponse)
async def get_repository_graph(
    repository_id: UUID,
    store: DependencyStoreDependency,
) -> GraphResponse:
    """Return the resolved dependency graph for a repository.

    Nodes are the indexed file paths; edges represent import relationships
    resolved during the last successful indexing run.
    """
    dependencies = await store.get_dependencies(repository_id)
    file_paths: set[str] = set()
    edges: list[GraphEdge] = []
    for dep in dependencies:
        file_paths.add(dep.source_path)
        file_paths.add(dep.target_path)
        edges.append(GraphEdge(source=dep.source_path, target=dep.target_path))

    nodes = [
        GraphNode(
            id=fp,
            label=fp.rsplit("/", 1)[-1] if "/" in fp else fp,
            type="file",
        )
        for fp in sorted(file_paths)
    ]

    return GraphResponse(nodes=nodes, edges=edges)


class ActivityEventResponse(BaseModel):
    """One activity event returned by the activity feed endpoint."""

    id: str
    event_type: str
    message: str
    timestamp: str


@router.get("/{repository_id}/activity", response_model=list[ActivityEventResponse])
async def get_repository_activity(
    repository_id: UUID,
    store: ActivityStoreDependency,
) -> list[ActivityEventResponse]:
    """Return recent activity events for the repository."""
    events = await store.get_activity(repository_id)
    return [
        ActivityEventResponse(
            id=str(id(ev)),
            event_type=ev.event_type,
            message=ev.message,
            timestamp=(ev.created_at.isoformat() if ev.created_at else ""),
        )
        for ev in events
    ]
