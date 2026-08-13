"""Create file_contents table for storing full file content.

Revision ID: 0003_create_file_contents
Revises: 0002_create_index_entries
Create Date: 2026-07-29
"""

import sqlalchemy as sa

from alembic import op

revision = "0003_create_file_contents"
down_revision = "0002_create_index_entries"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "file_contents",
        sa.Column("repository_id", sa.Uuid(), nullable=False),
        sa.Column("file_path", sa.String(length=1024), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("repository_id", "file_path", name="uq_file_content_repo_path"),
        sa.ForeignKeyConstraint(
            ["repository_id"],
            ["repositories.id"],
            ondelete="CASCADE",
        ),
    )
    op.create_index("ix_file_contents_repository_id", "file_contents", ["repository_id"])


def downgrade() -> None:
    op.drop_table("file_contents")
