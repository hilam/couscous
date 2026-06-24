"""add-search-vector

Revision ID: eb14f9ff4729
Revises: a1a8bc64dc2e
Create Date: 2026-06-24 13:02:48.120397

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "eb14f9ff4729"
down_revision: Union[str, Sequence[str], None] = "a1a8bc64dc2e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        ALTER TABLE entries ADD COLUMN search_vector tsvector
          GENERATED ALWAYS AS (
            to_tsvector('simple',
              regexp_replace(
                coalesce(title, '') || ' ' ||
                coalesce(summary, '') || ' ' ||
                coalesce(content, ''),
                '<[^>]+>', '', 'g'
              )
            )
          ) STORED;
    """)
    op.execute("""
        CREATE INDEX idx_entries_search_vector
        ON entries USING GIN (search_vector);
    """)
    op.execute("""
        CREATE INDEX idx_entries_user_published
        ON entries (user_id, published DESC);
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP INDEX IF EXISTS idx_entries_user_published;")
    op.execute("DROP INDEX IF EXISTS idx_entries_search_vector;")
    op.execute("ALTER TABLE entries DROP COLUMN IF EXISTS search_vector;")
