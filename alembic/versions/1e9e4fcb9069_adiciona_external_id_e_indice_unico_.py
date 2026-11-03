"""adiciona_external_id_e_indice_unico_entries

Revision ID: 1e9e4fcb9069
Revises: 94349822c2da
Create Date: 2026-11-03 18:35:22.307720

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = "1e9e4fcb9069"
down_revision: Union[str, Sequence[str], None] = "94349822c2da"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "entries", sa.Column("external_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True)
    )
    # guarda anti-duplicata: mantém a entry de menor id por (feed, user_id, external_id)
    op.execute(
        sa.text(
            "DELETE FROM entries a WHERE a.external_id IS NOT NULL AND a.id < "
            "(SELECT min(b.id) FROM entries b WHERE b.feed = a.feed "
            "AND b.user_id = a.user_id AND b.external_id = a.external_id)"
        )
    )
    op.create_index(
        "uq_entries_feed_user_external_id",
        "entries",
        ["feed", "user_id", "external_id"],
        unique=True,
        postgresql_where=sa.text("external_id IS NOT NULL"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "uq_entries_feed_user_external_id",
        table_name="entries",
        postgresql_where=sa.text("external_id IS NOT NULL"),
    )
    op.drop_column("entries", "external_id")
    # ### end Alembic commands ###
