"""checkout_confirmations: human-in-the-loop order review tokens

Revision ID: 0006_checkout_confirmations
Revises: 0005_seed_medicines
Create Date: 2026-06-10
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0006_checkout_confirmations"
down_revision: Union[str, Sequence[str], None] = "0005_seed_medicines"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "checkout_confirmations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("cart_id", sa.Uuid(), nullable=False),
        sa.Column("items_snapshot", sa.JSON(), nullable=False),
        sa.Column("total_amount", sa.Float(), nullable=False),
        sa.Column("cart_version_hash", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="pending"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "requires_manual_review",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["cart_id"], ["carts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_checkout_confirmations_user_id",
        "checkout_confirmations",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_checkout_confirmations_cart_id",
        "checkout_confirmations",
        ["cart_id"],
        unique=False,
    )
    op.create_index(
        "ix_checkout_confirmations_cart_version_hash",
        "checkout_confirmations",
        ["cart_version_hash"],
        unique=False,
    )
    op.create_index(
        "ix_checkout_confirmations_status",
        "checkout_confirmations",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_checkout_confirmations_status", table_name="checkout_confirmations"
    )
    op.drop_index(
        "ix_checkout_confirmations_cart_version_hash",
        table_name="checkout_confirmations",
    )
    op.drop_index(
        "ix_checkout_confirmations_cart_id", table_name="checkout_confirmations"
    )
    op.drop_index(
        "ix_checkout_confirmations_user_id", table_name="checkout_confirmations"
    )
    op.drop_table("checkout_confirmations")
