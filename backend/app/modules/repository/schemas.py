"""HTTP contracts owned by the Repository bounded context."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.repository.enums import RepositoryProvider, RepositoryStatus


class CreateRepositoryRequest(BaseModel):
    """Input accepted when registering a repository."""

    name: str = Field(min_length=1, max_length=255)
    url: str = Field(min_length=1, max_length=2048)
    provider: RepositoryProvider
    default_branch: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=10_000)
    language_summary: dict[str, Any] | list[Any] | None = None


class UpdateRepositoryRequest(BaseModel):
    """Mutable repository metadata and lifecycle fields."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    url: str | None = Field(default=None, min_length=1, max_length=2048)
    provider: RepositoryProvider | None = None
    default_branch: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=10_000)
    language_summary: dict[str, Any] | list[Any] | None = None
    status: RepositoryStatus | None = None
    last_indexed_at: datetime | None = None
    total_files: int | None = None


class RepositoryResponse(BaseModel):
    """Repository representation returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    url: str
    provider: RepositoryProvider
    default_branch: str
    description: str | None
    status: RepositoryStatus
    language_summary: dict[str, Any] | list[Any] | None
    last_indexed_at: datetime | None
    created_at: datetime
    updated_at: datetime
    total_files: int | None = None
    indexed_file_count: int = 0


class RepositoryListResponse(BaseModel):
    """Paginated collection response for registered repositories."""

    items: list[RepositoryResponse]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    total_pages: int = Field(ge=0)
