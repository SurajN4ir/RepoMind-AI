"""Create repositories table.

Revision ID: 0001_create_repositories
Revises:
Create Date: 2026-07-25
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "0001_create_repositories"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create storage for the Repository bounded context."""
    op.create_table(
        "repositories",
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column(
            "provider",
            sa.Enum(
                "GITHUB",
                "GITLAB",
                "BITBUCKET",
                "LOCAL",
                name="repository_provider",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("default_branch", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "NEW",
                "REGISTERED",
                "INDEXING",
                "READY",
                "FAILED",
                "ARCHIVED",
                name="repository_status",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("language_summary", sa.JSON(), nullable=True),
        sa.Column("last_indexed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("url"),
    )


def downgrade() -> None:
    """Remove Repository bounded-context storage."""
    op.drop_table("repositories")
