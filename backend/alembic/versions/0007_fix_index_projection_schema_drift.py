"""Fix index_entries/keyword_index_entries/metadata_index_entries schema drift.

The models backing these tables (``app.modules.indexing.db_models``) were
refactored after 0002 was written: ``document_id`` moved from a UUID to a
content-derived string (see chunk id generation, a sha256 hex digest), the
per-repository uniqueness constraint replaced a global one, and the keyword
and metadata index tables moved from normalized per-term/per-key rows to one
row per document. 0002 was never updated to match, so applying it against a
real PostgreSQL database produces tables the current ORM models cannot use
(``document_id`` isn't valid UUID input, and the keyword/metadata tables lack
the columns the models expect). This has gone unnoticed because local/test
runs use SQLite, which builds tables straight from the ORM models via
``Base.metadata.create_all`` and never executes Alembic migrations.

No environment has ever run 0002-0006 against real PostgreSQL (per project
history), so these tables are corrected in place rather than patched with
compensating data migrations.

Revision ID: 0007_fix_index_projection_drift
Revises: 0006_conversations
Create Date: 2026-09-09
"""

import sqlalchemy as sa

from alembic import op

revision = "0007_fix_index_projection_drift"
down_revision = "0006_conversations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the old keyword/metadata tables first: their FKs reference
    # index_entries_document_id_key, which must be gone before that unique
    # constraint (and the column it's on) can be altered.
    op.drop_table("metadata_index_entries")
    op.drop_table("keyword_index_entries")

    op.drop_constraint("index_entries_document_id_key", "index_entries", type_="unique")
    op.alter_column(
        "index_entries",
        "document_id",
        type_=sa.String(length=255),
        existing_type=sa.Uuid(),
        postgresql_using="document_id::text",
    )
    op.create_unique_constraint(
        "uq_index_entry_repo_doc",
        "index_entries",
        ["repository_id", "document_id"],
    )

    op.create_table(
        "keyword_index_entries",
        sa.Column("document_id", sa.String(length=255), nullable=False),
        sa.Column("repository_id", sa.Uuid(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "repository_id", "document_id", name="uq_keyword_entry_repo_doc"
        ),
        sa.ForeignKeyConstraint(
            ["repository_id"],
            ["repositories.id"],
            ondelete="CASCADE",
        ),
    )
    op.create_index(
        "ix_keyword_index_entries_repository_id", "keyword_index_entries", ["repository_id"]
    )

    op.create_table(
        "metadata_index_entries",
        sa.Column("document_id", sa.String(length=255), nullable=False),
        sa.Column("repository_id", sa.Uuid(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "repository_id", "document_id", name="uq_metadata_entry_repo_doc"
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


def downgrade() -> None:
    # Drop the current tables and restore document_id to Uuid *before*
    # recreating the old keyword/metadata tables: their FKs reference
    # index_entries.document_id and require its type to match at creation time.
    op.drop_table("metadata_index_entries")
    op.drop_table("keyword_index_entries")

    op.drop_constraint("uq_index_entry_repo_doc", "index_entries", type_="unique")
    op.alter_column(
        "index_entries",
        "document_id",
        type_=sa.Uuid(),
        existing_type=sa.String(length=255),
        postgresql_using="document_id::uuid",
    )
    op.create_unique_constraint("index_entries_document_id_key", "index_entries", ["document_id"])

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
