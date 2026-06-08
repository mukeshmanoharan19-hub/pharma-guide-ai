"""routing_logs: supervisor routing analytics

Revision ID: 0004_routing_logs
Revises: 0003_commerce
Create Date: 2026-06-08

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0004_routing_logs"
down_revision: Union[str, Sequence[str], None] = "0003_commerce"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "routing_logs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("session_id", sa.Uuid(), nullable=True),
        sa.Column("query", sa.Text(), nullable=False),
        sa.Column("intent", sa.String(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("secondary_intents", sa.JSON(), nullable=True),
        sa.Column("route", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["session_id"], ["chat_sessions.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_routing_logs_user_id", "routing_logs", ["user_id"], unique=False
    )
    op.create_index(
        "ix_routing_logs_session_id",
        "routing_logs",
        ["session_id"],
        unique=False,
    )
    op.create_index(
        "ix_routing_logs_intent", "routing_logs", ["intent"], unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_routing_logs_intent", table_name="routing_logs")
    op.drop_index("ix_routing_logs_session_id", table_name="routing_logs")
    op.drop_index("ix_routing_logs_user_id", table_name="routing_logs")
    op.drop_table("routing_logs")
