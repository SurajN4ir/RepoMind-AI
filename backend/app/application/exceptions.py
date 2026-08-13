"""Application-layer exceptions that abstract domain errors for transport."""


class ApplicationError(Exception):
    """Base exception for all application-layer failures."""


class EntityNotFoundError(ApplicationError):
    """Requested resource does not exist."""


class ConflictError(ApplicationError):
    """Request conflicts with current resource state."""


class ValidationError(ApplicationError):
    """Request data failed application-level validation."""


class ExternalServiceError(ApplicationError):
    """An external dependency (Git, embedding provider, etc.) failed."""


class UnhandledDomainError(ApplicationError):
    """A domain exception was not explicitly mapped to an application error."""


class WorkspaceError(ApplicationError):
    """Pipeline workspace could not be created, written to, or cleaned up."""


class PipelineError(ApplicationError):
    """A pipeline step encountered an unexpected failure."""
