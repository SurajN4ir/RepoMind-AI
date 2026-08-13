"""Feature-local failures for evidence context construction."""


class ContextBuilderError(Exception):
    """Base class for context construction failures."""


class InvalidContextBudgetError(ContextBuilderError):
    """Raised when an invalid token budget is configured."""
