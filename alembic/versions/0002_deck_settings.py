"""Add extensible settings to decks."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0002_deck_settings"
down_revision = "0001_initial"
branch_labels = None
depends_on = None

def upgrade():
    if "settings" not in {column["name"] for column in inspect(op.get_bind()).get_columns("decks")}:
        op.add_column(
            "decks",
            sa.Column("settings", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        )

def downgrade():
    if "settings" in {column["name"] for column in inspect(op.get_bind()).get_columns("decks")}:
        op.drop_column("decks", "settings")
