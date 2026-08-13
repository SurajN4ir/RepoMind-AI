"""Feature-local errors raised while planning repository searches."""


class QueryEngineError(Exception):
    """Base class for query-engine failures."""


class InvalidUserRequestError(QueryEngineError):
    """Raised when a user request cannot produce a valid search request."""


class UnknownRepositoryError(QueryEngineError):
    """Raised when an explicitly selected repository is unavailable."""
