"""Add total_files column to repositories and create activity_events table.

Revision ID: 0005_activity_events
Revises: 0004_create_file_dependencies
Create Date: 2026-07-29

Note: the revision id is shorter than this file's name. Alembic's
alembic_version.version_num column is a hardcoded VARCHAR(32) with no
supported way to widen it (see alembic.ddl.impl.DefaultImpl.version_table_impl),
so every revision id in this project must stay within 32 characters -- this
one and 0006 originally didn't and broke `alembic upgrade` against real
PostgreSQL (SQLite ignores VARCHAR length, which is how this went unnoticed).
"""

import sqlalchemy as sa

from alembic import op

revision = "0005_activity_events"
down_revision = "0004_create_file_dependencies"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "repositories",
        sa.Column("total_files", sa.Integer(), nullable=True),
    )
    op.create_table(
        "activity_events",
        sa.Column("repository_id", sa.Uuid(), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("message", sa.String(length=1024), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["repository_id"],
            ["repositories.id"],
            ondelete="CASCADE",
        ),
    )
    op.create_index(
        "ix_activity_events_repository_id",
        "activity_events",
        ["repository_id"],
    )


def downgrade() -> None:
    op.drop_table("activity_events")
    op.drop_column("repositories", "total_files")
