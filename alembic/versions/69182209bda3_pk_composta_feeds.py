"""pk_composta_feeds

Revision ID: 69182209bda3
Revises: 1e9e4fcb9069
Create Date: 2026-11-03 19:49:27.601177

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "69182209bda3"
down_revision: Union[str, Sequence[str], None] = "1e9e4fcb9069"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # entries.feed deixa de ser FK (vira coluna str pura, escopada por user_id).
    op.drop_constraint("entries_feed_fkey", "entries", type_="foreignkey")
    # PK de feeds passa de (url) para composta (url, user_id).
    op.drop_constraint("feeds_pkey", "feeds", type_="primary")
    op.create_primary_key("feeds_pkey", "feeds", ["url", "user_id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("feeds_pkey", "feeds", type_="primary")
    op.create_primary_key("feeds_pkey", "feeds", ["url"])
    op.create_foreign_key("entries_feed_fkey", "entries", "feeds", ["feed"], ["url"])
