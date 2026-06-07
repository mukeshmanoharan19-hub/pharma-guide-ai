"""initial schema: users and medicines

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-07

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0001_initial"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Check if table already exists in the target database
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    if not inspector.has_table("users"):
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("email", sa.String(), nullable=True),
            sa.Column("password", sa.String(), nullable=True),
            sa.Column("full_name", sa.String(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("email"),
        )
        
    if not inspector.has_table("medicines"):
        op.create_table(
            "medicines",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("compositions", sa.Text(), nullable=True),
            sa.Column("search_suggestion_keywords", sa.JSON(), nullable=True),
            sa.Column("tags", sa.JSON(), nullable=True),
            sa.Column("sku", sa.String(), nullable=True),
            sa.Column("seo", sa.JSON(), nullable=True),
            sa.Column("unit_price", sa.Float(), nullable=True),
            sa.Column("maximum_retail_price", sa.Float(), nullable=True),
            sa.Column("discount", sa.Float(), nullable=True),
            sa.Column("final_price", sa.Float(), nullable=True),
            sa.Column("thumbnail", sa.String(), nullable=True),
            sa.Column("subcategory_id", sa.String(), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=True),
            sa.Column("about_product", sa.JSON(), nullable=True),
            sa.Column("taxes", sa.JSON(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.Column("discount_type", sa.String(), nullable=True),
            sa.Column("max_order_quantity", sa.Integer(), nullable=True),
            sa.Column("min_order_quantity", sa.Integer(), nullable=True),
            sa.Column("brand_tags", sa.JSON(), nullable=True),
            sa.Column("hsn_number", sa.String(), nullable=True),
            sa.Column("scheduled_drug", sa.String(), nullable=True),
            sa.Column("salt_type", sa.String(), nullable=True),
            sa.Column("prescription_req", sa.Boolean(), nullable=True),
            sa.Column("packing_type", sa.String(), nullable=True),
            sa.Column("clinical_product_key", sa.String(), nullable=True),
            sa.Column("composition_key", sa.String(), nullable=True),
            sa.Column("dosage_form", sa.String(), nullable=True),
            sa.Column("release_type", sa.String(), nullable=True),
            sa.Column("route", sa.String(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_medicines_sku", "medicines", ["sku"], unique=False)
        op.create_index(
            "ix_medicines_subcategory_id", "medicines", ["subcategory_id"], unique=False
        )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_medicines_subcategory_id", table_name="medicines")
    op.drop_index("ix_medicines_sku", table_name="medicines")
    op.drop_table("medicines")
    op.drop_table("users")
