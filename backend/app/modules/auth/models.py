"""Pure domain model for an authenticated caller."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AuthenticatedUser:
    """The verified identity of the caller, derived from a Clerk session token."""

    user_id: str
