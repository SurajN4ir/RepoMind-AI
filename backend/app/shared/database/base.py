"""Declarative base shared by future persistence models."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for persistence models owned by feature modules."""
