"""commerce: carts, cart_items, orders, order_items + medicine stock

Revision ID: 0003_commerce
Revises: 0002_chat_memory
Create Date: 2026-06-07

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0003_commerce"
down_revision: Union[str, Sequence[str], None] = "0002_chat_memory"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "medicines", sa.Column("stock_quantity", sa.Integer(), nullable=True)
    )

    op.create_table(
        "carts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
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
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_carts_user_id", "carts", ["user_id"], unique=False)

    op.create_table(
        "cart_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("cart_id", sa.Uuid(), nullable=False),
        sa.Column("medicine_id", sa.Integer(), nullable=False),
        sa.Column("sku", sa.String(), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Float(), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["cart_id"], ["carts.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["medicine_id"], ["medicines.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cart_id", "medicine_id", name="uq_cart_item"),
    )
    op.create_index(
        "ix_cart_items_cart_id", "cart_items", ["cart_id"], unique=False
    )

    op.create_table(
        "orders",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("payment_status", sa.String(), nullable=False),
        sa.Column("total_amount", sa.Float(), nullable=False),
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
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_orders_user_id", "orders", ["user_id"], unique=False)

    op.create_table(
        "order_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("order_id", sa.Uuid(), nullable=False),
        sa.Column("medicine_id", sa.Integer(), nullable=False),
        sa.Column("sku", sa.String(), nullable=True),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Float(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["order_id"], ["orders.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["medicine_id"], ["medicines.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_order_items_order_id", "order_items", ["order_id"], unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_order_items_order_id", table_name="order_items")
    op.drop_table("order_items")
    op.drop_index("ix_orders_user_id", table_name="orders")
    op.drop_table("orders")
    op.drop_index("ix_cart_items_cart_id", table_name="cart_items")
    op.drop_table("cart_items")
    op.drop_index("ix_carts_user_id", table_name="carts")
    op.drop_table("carts")
    op.drop_column("medicines", "stock_quantity")
