"""Create file_dependencies table for resolved cross-file import edges.

Revision ID: 0004_create_file_dependencies
Revises: 0003_create_file_contents
Create Date: 2026-07-29
"""

import sqlalchemy as sa

from alembic import op

revision = "0004_create_file_dependencies"
down_revision = "0003_create_file_contents"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "file_dependencies",
        sa.Column("repository_id", sa.Uuid(), nullable=False),
        sa.Column("source_path", sa.String(length=1024), nullable=False),
        sa.Column("target_path", sa.String(length=1024), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "repository_id",
            "source_path",
            "target_path",
            name="uq_file_dep_repo_source_target",
        ),
        sa.ForeignKeyConstraint(
            ["repository_id"],
            ["repositories.id"],
            ondelete="CASCADE",
        ),
    )
    op.create_index(
        "ix_file_dependencies_repository_id",
        "file_dependencies",
        ["repository_id"],
    )


def downgrade() -> None:
    op.drop_table("file_dependencies")
