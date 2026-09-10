"""Enable pgvector and store index_entries.embedding as a native vector column.

Replaces the Python-side cosine-similarity search (which loaded every row for
a repository into memory) with database-side pgvector similarity search. The
``embedding`` column moves from JSON to ``vector(EMBEDDING_DIMENSIONS)`` so
PostgreSQL can rank by distance directly.

The column is dropped and recreated rather than cast in place: no environment
has ever run these migrations against real PostgreSQL (see 0007), so there is
no production data to preserve, and drop/recreate avoids relying on pgvector's
text-literal parser tolerating whatever formatting ``json::text`` happens to
produce.

The vector width comes from ``settings.embedding_dimensions`` so it always
matches the configured embedding provider's output. Changing embedding models
to one with a different width requires a follow-up migration to resize this
column (pgvector fixes width per column).

Revision ID: 0008_pgvector_embedding_column
Revises: 0007_fix_index_projection_drift
Create Date: 2026-09-09
"""

import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

from alembic import op
from app.config.settings import get_settings

revision = "0008_pgvector_embedding_column"
down_revision = "0007_fix_index_projection_drift"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    dimensions = get_settings().embedding_dimensions
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.drop_column("index_entries", "embedding")
    op.add_column(
        "index_entries",
        sa.Column("embedding", Vector(dimensions), nullable=False),
    )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    op.drop_column("index_entries", "embedding")
    op.add_column(
        "index_entries",
        sa.Column("embedding", sa.JSON(), nullable=False),
    )
