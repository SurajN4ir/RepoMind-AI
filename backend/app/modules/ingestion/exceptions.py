"""Ingestion bounded-context exceptions."""


class IngestionError(Exception):
    """Base exception for repository workspace and manifest failures."""


class GitCloneError(IngestionError):
    """Raised when Git cannot create the requested shallow clone."""


class RepositoryWorkspaceError(IngestionError):
    """Raised when a temporary ingestion workspace cannot be managed safely."""


class UnsupportedIngestionStatusError(IngestionError):
    """Raised when a repository lifecycle state cannot begin ingestion."""
