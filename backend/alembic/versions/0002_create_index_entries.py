"""Create index_entry, keyword_index_entry, metadata_index_entry tables.

Revision ID: 0002_create_index_entries
Revises: 0001_create_repositories
Create Date: 2026-07-28
"""

import sqlalchemy as sa
from sqlalchemy import JSON

from alembic import op

revision = "0002_create_index_entries"
down_revision = "0001_create_repositories"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "index_entries",
        sa.Column("document_id", sa.Uuid(), nullable=False),
        sa.Column("repository_id", sa.Uuid(), nullable=False),
        sa.Column("embedding", JSON(), nullable=True),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("metadata", JSON(), nullable=True, server_default=sa.text("'{}'::json")),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("model", sa.String(length=128), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("document_id"),
        sa.ForeignKeyConstraint(
            ["repository_id"],
            ["repositories.id"],
            ondelete="CASCADE",
        ),
    )
    op.create_index("ix_index_entries_repository_id", "index_entries", ["repository_id"])
    op.create_index("ix_index_entries_content_hash", "index_entries", ["content_hash"])

    op.create_table(
        "keyword_index_entries",
        sa.Column("keyword", sa.String(length=255), nullable=False),
        sa.Column("repository_id", sa.Uuid(), nullable=False),
        sa.Column("document_id", sa.Uuid(), nullable=False),
        sa.Column("frequency", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("keyword", "document_id"),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["index_entries.document_id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["repository_id"],
            ["repositories.id"],
            ondelete="CASCADE",
        ),
    )
    op.create_index("ix_keyword_index_entries_keyword", "keyword_index_entries", ["keyword"])
    op.create_index(
        "ix_keyword_index_entries_repository_id", "keyword_index_entries", ["repository_id"]
    )

    op.create_table(
        "metadata_index_entries",
        sa.Column("key", sa.String(length=255), nullable=False),
        sa.Column("value", sa.Text(), nullable=True),
        sa.Column("repository_id", sa.Uuid(), nullable=False),
        sa.Column("document_id", sa.Uuid(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["index_entries.document_id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["repository_id"],
            ["repositories.id"],
            ondelete="CASCADE",
        ),
    )
    op.create_index(
        "ix_metadata_index_entries_repository_id", "metadata_index_entries", ["repository_id"]
    )
    op.create_index("ix_metadata_index_entries_key", "metadata_index_entries", ["key"])


def downgrade() -> None:
    op.drop_table("metadata_index_entries")
    op.drop_table("keyword_index_entries")
    op.drop_table("index_entries")
