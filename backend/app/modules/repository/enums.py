"""Repository domain enumerations."""

from enum import StrEnum


class RepositoryProvider(StrEnum):
    """Supported source-code repository providers."""

    GITHUB = "GITHUB"
    GITLAB = "GITLAB"
    BITBUCKET = "BITBUCKET"
    LOCAL = "LOCAL"


class RepositoryStatus(StrEnum):
    """Repository lifecycle states independent of ingestion implementation details."""

    NEW = "NEW"
    REGISTERED = "REGISTERED"
    INDEXING = "INDEXING"
    READY = "READY"
    FAILED = "FAILED"
    ARCHIVED = "ARCHIVED"
