"""Create conversations and messages tables.

Revision ID: 0006_conversations
Revises: 0005_activity_events
Create Date: 2026-07-29

Note: shortened revision id -- see 0005_add_total_files_and_activity_events.py
for why every revision id here must stay within 32 characters.
"""

import sqlalchemy as sa

from alembic import op

revision = "0006_conversations"
down_revision = "0005_activity_events"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "conversations",
        sa.Column("repository_id", sa.Uuid(), nullable=False, index=True),
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
    op.create_table(
        "messages",
        sa.Column("conversation_id", sa.Uuid(), nullable=False, index=True),
        sa.Column("role", sa.String(length=16), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("citation_json", sa.Text(), nullable=False, server_default=""),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["conversations.id"],
            ondelete="CASCADE",
        ),
    )


def downgrade() -> None:
    op.drop_table("messages")
    op.drop_table("conversations")
