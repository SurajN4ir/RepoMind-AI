"""Unit tests for Clerk JWT verification and bearer-header extraction.

Uses a locally generated RSA keypair and real jwt.encode/jwt.decode calls, so
signature and claim verification are exercised for real. Only the network
fetch of Clerk's JWKS is faked (via a substitutable key resolver) -- tests
should not depend on a real Clerk instance being reachable.
"""

import time
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from app.modules.auth.exceptions import InvalidTokenError, MissingCredentialsError
from app.modules.auth.models import AuthenticatedUser
from app.modules.auth.verifier import ClerkTokenVerifier, extract_bearer_token

_PRIVATE_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
_OTHER_PRIVATE_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)


class _FakeSigningKey:
    def __init__(self, key: object) -> None:
        self.key = key


class _FakeKeyResolver:
    """Always resolves to the same (real, locally generated) public key."""

    def get_signing_key_from_jwt(self, token: str) -> _FakeSigningKey:
        return _FakeSigningKey(_PRIVATE_KEY.public_key())


def _verifier(**kwargs: object) -> ClerkTokenVerifier:
    return ClerkTokenVerifier(
        "https://example.invalid/.well-known/jwks.json",
        key_resolver=_FakeKeyResolver(),
        **kwargs,  # type: ignore[arg-type]
    )


def _token(
    *,
    sub: str | None = "user_123",
    exp_delta: timedelta = timedelta(minutes=5),
    private_key: rsa.RSAPrivateKey = _PRIVATE_KEY,
    **extra_claims: object,
) -> str:
    now = datetime.now(UTC)
    claims: dict[str, object] = {"iat": now, "exp": now + exp_delta, **extra_claims}
    if sub is not None:
        claims["sub"] = sub
    return jwt.encode(claims, private_key, algorithm="RS256")


class TestExtractBearerToken:
    def test_missing_header_raises(self) -> None:
        with pytest.raises(MissingCredentialsError):
            extract_bearer_token(None)

    def test_empty_header_raises(self) -> None:
        with pytest.raises(MissingCredentialsError):
            extract_bearer_token("")

    def test_wrong_scheme_raises(self) -> None:
        with pytest.raises(MissingCredentialsError):
            extract_bearer_token("Basic dXNlcjpwYXNz")

    def test_bearer_with_no_token_raises(self) -> None:
        with pytest.raises(MissingCredentialsError):
            extract_bearer_token("Bearer ")

    def test_valid_bearer_header_returns_token(self) -> None:
        assert extract_bearer_token("Bearer abc.def.ghi") == "abc.def.ghi"


class TestClerkTokenVerifier:
    def test_valid_token_returns_authenticated_user(self) -> None:
        user = _verifier().verify(_token(sub="user_abc"))

        assert user == AuthenticatedUser(user_id="user_abc")

    def test_expired_token_is_rejected(self) -> None:
        expired = _token(exp_delta=timedelta(minutes=-5))

        with pytest.raises(InvalidTokenError):
            _verifier().verify(expired)

    def test_not_yet_valid_token_is_rejected(self) -> None:
        now = datetime.now(UTC)
        not_yet_valid = jwt.encode(
            {
                "sub": "user_123",
                "iat": now,
                "nbf": now + timedelta(minutes=10),
                "exp": now + timedelta(minutes=20),
            },
            _PRIVATE_KEY,
            algorithm="RS256",
        )

        with pytest.raises(InvalidTokenError):
            _verifier().verify(not_yet_valid)

    def test_bad_signature_is_rejected(self) -> None:
        signed_by_someone_else = _token(private_key=_OTHER_PRIVATE_KEY)

        with pytest.raises(InvalidTokenError):
            _verifier().verify(signed_by_someone_else)

    def test_missing_subject_claim_is_rejected(self) -> None:
        no_sub = _token(sub=None)

        with pytest.raises(InvalidTokenError):
            _verifier().verify(no_sub)

    def test_malformed_token_is_rejected(self) -> None:
        with pytest.raises(InvalidTokenError):
            _verifier().verify("not-a-jwt-at-all")

    def test_missing_expiry_claim_is_rejected(self) -> None:
        now = int(time.time())
        no_exp = jwt.encode({"sub": "user_123", "iat": now}, _PRIVATE_KEY, algorithm="RS256")

        with pytest.raises(InvalidTokenError):
            _verifier().verify(no_exp)

    def test_issuer_mismatch_is_rejected_when_issuer_configured(self) -> None:
        now = datetime.now(UTC)
        token = jwt.encode(
            {
                "sub": "user_123",
                "iat": now,
                "exp": now + timedelta(minutes=5),
                "iss": "https://wrong-instance.clerk.accounts.dev",
            },
            _PRIVATE_KEY,
            algorithm="RS256",
        )

        verifier = _verifier(issuer="https://expected-instance.clerk.accounts.dev")

        with pytest.raises(InvalidTokenError):
            verifier.verify(token)

    def test_matching_issuer_is_accepted(self) -> None:
        now = datetime.now(UTC)
        token = jwt.encode(
            {
                "sub": "user_123",
                "iat": now,
                "exp": now + timedelta(minutes=5),
                "iss": "https://expected-instance.clerk.accounts.dev",
            },
            _PRIVATE_KEY,
            algorithm="RS256",
        )

        verifier = _verifier(issuer="https://expected-instance.clerk.accounts.dev")

        assert verifier.verify(token) == AuthenticatedUser(user_id="user_123")
