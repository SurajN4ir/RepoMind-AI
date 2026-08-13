"""Reusable SQLAlchemy model mixins."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.clock.utc import utc_now
from app.shared.identifiers.uuid import new_uuid


class UUIDPrimaryKeyMixin:
    """Add an application-generated UUID primary key named ``id``."""

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=new_uuid)


class TimestampMixin:
    """Add UTC-aware creation and modification timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )
