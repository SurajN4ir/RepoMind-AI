"""Database-layer exceptions that do not leak SQLAlchemy details upward."""


class PersistenceError(Exception):
    """Base exception for persistence infrastructure failures."""


class IntegrityConstraintError(PersistenceError):
    """Raised when a database integrity constraint is violated."""


class EntityNotFoundError(PersistenceError):
    """Raised when a requested persisted entity does not exist."""


class TransactionError(PersistenceError):
    """Raised when a transaction cannot be completed safely."""
