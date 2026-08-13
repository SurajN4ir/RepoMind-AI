"""UUID generation primitives."""

from uuid import UUID, uuid4


def new_uuid() -> UUID:
    """Return a new random UUID suitable for application-owned identifiers."""
    return uuid4()
