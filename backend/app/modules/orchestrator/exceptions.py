"""Feature-local exceptions for response orchestration."""


class OrchestratorError(Exception):
    """Base class for orchestration failures."""


class ResponseGenerationError(OrchestratorError):
    """Raised when the configured response generator cannot produce output."""


class ToolExecutionError(OrchestratorError):
    """Raised when a required orchestration tool fails."""


class ResponseVerificationError(OrchestratorError):
    """Raised when configured verification rejects a generated response."""
