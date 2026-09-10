"""Ingestion bounded-context exceptions."""


class GitCloneError(Exception):
    """Raised when Git cannot create the requested shallow clone."""
