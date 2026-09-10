"""Clerk session token verification and bearer-header extraction."""

from typing import Protocol

import jwt

from app.modules.auth.exceptions import InvalidTokenError, MissingCredentialsError
from app.modules.auth.models import AuthenticatedUser


class SigningKeyResolver(Protocol):
    """Port over PyJWKClient so tests can substitute a fake JWKS source."""

    def get_signing_key_from_jwt(self, token: str) -> object: ...


def extract_bearer_token(authorization_header: str | None) -> str:
    """Return the bearer token from an ``Authorization`` header value.

    Raises ``MissingCredentialsError`` for a missing or malformed header
    without ever including the header's own content in the error.
    """
    if not authorization_header:
        raise MissingCredentialsError("No Authorization header was supplied.")
    scheme, _, token = authorization_header.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise MissingCredentialsError("Authorization header must be a Bearer token.")
    return token


class ClerkTokenVerifier:
    """Verifies a Clerk-issued session JWT against Clerk's public JWKS.

    Only the signature, expiry, and subject claim are treated as required;
    ``issuer`` is checked when configured. Never logs token contents.
    """

    def __init__(
        self,
        jwks_url: str,
        *,
        issuer: str | None = None,
        leeway_seconds: float = 5.0,
        key_resolver: SigningKeyResolver | None = None,
    ) -> None:
        self._key_resolver: SigningKeyResolver = key_resolver or jwt.PyJWKClient(jwks_url)
        self._issuer = issuer
        self._leeway_seconds = leeway_seconds

    def verify(self, token: str) -> AuthenticatedUser:
        """Verify signature, expiry, and required claims; return the caller's identity."""
        try:
            signing_key = self._key_resolver.get_signing_key_from_jwt(token)
            claims = jwt.decode(
                token,
                signing_key.key,  # type: ignore[attr-defined]
                algorithms=["RS256"],
                issuer=self._issuer,
                leeway=self._leeway_seconds,
                options={"require": ["exp", "iat", "sub"], "verify_iss": self._issuer is not None},
            )
        except jwt.PyJWTError as exc:
            raise InvalidTokenError("Token verification failed.") from exc

        user_id = claims.get("sub")
        if not isinstance(user_id, str) or not user_id:
            raise InvalidTokenError("Token is missing a valid subject claim.")
        return AuthenticatedUser(user_id=user_id)
