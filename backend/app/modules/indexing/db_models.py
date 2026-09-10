"""SQLAlchemy models for persistent write-side index projections."""

from uuid import UUID

from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.config.settings import get_settings
from app.shared.database.base import Base
from app.shared.database.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class ActivityEventModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Persistent activity event log for repository indexing operations."""

    __tablename__ = "activity_events"

    repository_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    message: Mapped[str] = mapped_column(String(1024), nullable=False)


class FileDependencyModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Persistent resolved cross-file dependency edges for a repository."""

    __tablename__ = "file_dependencies"

    repository_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    source_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    target_path: Mapped[str] = mapped_column(String(1024), nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "repository_id",
            "source_path",
            "target_path",
            name="uq_file_dep_repo_source_target",
        ),
    )


class IndexEntryModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Persistent vector, text, and metadata record for one indexed document."""

    __tablename__ = "index_entries"

    document_id: Mapped[str] = mapped_column(String(255), nullable=False)
    repository_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    # JSON on SQLite (dev/tests); a real pgvector column on PostgreSQL, sized from
    # settings so it always matches the configured embedding provider's output width.
    embedding: Mapped[list[float]] = mapped_column(
        JSON().with_variant(Vector(get_settings().embedding_dimensions), "postgresql"),
        nullable=False,
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    entry_metadata: Mapped[dict] = mapped_column("metadata", JSON, nullable=False, default=dict)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    model: Mapped[str] = mapped_column(String(64), nullable=False)

    __table_args__ = (
        UniqueConstraint("repository_id", "document_id", name="uq_index_entry_repo_doc"),
    )


class KeywordIndexEntryModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Persistent keyword-index representation derived from an index entry."""

    __tablename__ = "keyword_index_entries"

    document_id: Mapped[str] = mapped_column(String(255), nullable=False)
    repository_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (
        UniqueConstraint("repository_id", "document_id", name="uq_keyword_entry_repo_doc"),
    )


class MetadataIndexEntryModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Persistent metadata-index representation derived from an index entry."""

    __tablename__ = "metadata_index_entries"

    document_id: Mapped[str] = mapped_column(String(255), nullable=False)
    repository_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    entry_metadata: Mapped[dict] = mapped_column("metadata", JSON, nullable=False, default=dict)

    __table_args__ = (
        UniqueConstraint("repository_id", "document_id", name="uq_metadata_entry_repo_doc"),
    )


class FileContentModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Persistent full file content for indexed repository files."""

    __tablename__ = "file_contents"

    repository_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    __table_args__ = (
        UniqueConstraint("repository_id", "file_path", name="uq_file_content_repo_path"),
    )
