"""Repository bounded-context exceptions."""


class RepositoryDomainError(Exception):
    """Base exception for Repository module failures."""


class RepositoryNotFoundError(RepositoryDomainError):
    """Raised when a requested registered repository does not exist."""


class DuplicateRepositoryError(RepositoryDomainError):
    """Raised when a URL has already been registered."""


class InvalidRepositoryUrlError(RepositoryDomainError):
    """Raised when a repository URL is unsupported or malformed."""


class InvalidRepositoryMetadataError(RepositoryDomainError):
    """Raised when mutable repository metadata fails domain validation."""


class UnsupportedRepositoryProviderError(RepositoryDomainError):
    """Raised when a provider is not one supported by this module."""


class InvalidRepositoryStatusTransitionError(RepositoryDomainError):
    """Raised when a requested lifecycle change violates the status policy."""


class RepositoryPersistenceError(RepositoryDomainError):
    """Raised when repository persistence fails after infrastructure translation."""
