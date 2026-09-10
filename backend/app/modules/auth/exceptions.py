"""Domain exceptions for the auth bounded context."""


class AuthenticationError(Exception):
    """Base class for all authentication failures."""


class MissingCredentialsError(AuthenticationError):
    """Raised when no (or a malformed) Authorization header was supplied."""


class InvalidTokenError(AuthenticationError):
    """Raised when a bearer token fails signature, claim, or expiry checks."""
