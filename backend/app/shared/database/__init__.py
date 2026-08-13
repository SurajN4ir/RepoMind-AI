"""Async-first shared persistence infrastructure."""

from app.shared.database.base import Base
from app.shared.database.repository import BaseRepository

__all__ = ["Base", "BaseRepository"]
