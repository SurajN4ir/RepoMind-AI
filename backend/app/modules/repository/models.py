"""Persistence model owned by the Repository bounded context."""

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.repository.enums import RepositoryProvider, RepositoryStatus
from app.shared.database.base import Base
from app.shared.database.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Repository(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A registered source-code repository and its lifecycle metadata."""

    __tablename__ = "repositories"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False, unique=True)
    provider: Mapped[RepositoryProvider] = mapped_column(
        Enum(
            RepositoryProvider,
            name="repository_provider",
            native_enum=False,
            create_constraint=True,
        ),
        nullable=False,
    )
    default_branch: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[RepositoryStatus] = mapped_column(
        Enum(
            RepositoryStatus,
            name="repository_status",
            native_enum=False,
            create_constraint=True,
        ),
        nullable=False,
        default=RepositoryStatus.NEW,
    )
    language_summary: Mapped[dict[str, Any] | list[Any] | None] = mapped_column(JSON, nullable=True)
    last_indexed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    total_files: Mapped[int | None] = mapped_column(Integer, nullable=True)
