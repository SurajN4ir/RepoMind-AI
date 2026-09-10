"""Add repositories.owner_id for per-user ownership.

Migration safety
-----------------
This column is added NULLABLE, with no default value and no backfill for
existing rows. That is deliberate.

No environment has ever run these migrations against a real PostgreSQL
database with real repository data in it (see 0007's docstring -- the same
"no environment has ever run this against real Postgres" history applies
here), so in practice there is nothing to migrate. But the correct strategy
doesn't depend on that being true: a repository row created before ownership
existed has no real owner_id to backfill, and inventing one (an empty
string, a placeholder, the first Clerk user we can find) would be actively
wrong -- it would either silently grant that repository to whichever user
happens to match the placeholder, or silently and permanently hide it behind
a value nothing can ever authenticate as.

Leaving owner_id NULL for such rows is the safe choice: RepositoryService's
ownership check is `repository.owner_id != owner_id`, and NULL compares
unequal to every real Clerk user id, so a legacy row is simply invisible
through the API to everyone -- inert, not misattributed. Recovering it is a
deliberate, auditable operator action (an `UPDATE repositories SET owner_id
= '<clerk_user_id>' WHERE id = '<repository_id>'`), not something this
migration should guess at.

Every repository created going forward always has a real owner_id --
RepositoryService.register() requires one as a parameter; there is no code
path that inserts a repository without one.

Revision ID: 0009_repo_owner_id
Revises: 0008_pgvector_embedding_column
Create Date: 2026-09-10
"""

import sqlalchemy as sa

from alembic import op

revision = "0009_repo_owner_id"
down_revision = "0008_pgvector_embedding_column"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "repositories",
        sa.Column("owner_id", sa.String(length=255), nullable=True),
    )
    op.create_index("ix_repositories_owner_id", "repositories", ["owner_id"])


def downgrade() -> None:
    op.drop_index("ix_repositories_owner_id", "repositories")
    op.drop_column("repositories", "owner_id")
