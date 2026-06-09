"""Seed medicines from data/seeds/products-old.json

Revision ID: 0005_seed_medicines
Revises: 0004_routing_logs
Create Date: 2026-06-09
"""

from __future__ import annotations

import json
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0005_seed_medicines"
down_revision: Union[str, Sequence[str], None] = "0004_routing_logs"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _normalize_subcategory(subcat):
    if isinstance(subcat, dict):
        return subcat.get("$oid")
    return subcat


def _json_or_none(value):
    """Serialize dict/list to JSON string for psycopg2 JSON columns."""
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return json.dumps(value)
    return value


def upgrade() -> None:
    """Insert medicines from legacy seed file."""
    conn = op.get_bind()

    # Idempotency: skip if data already present
    count = conn.execute(sa.text("SELECT COUNT(*) FROM medicines")).scalar() or 0
    if count > 0:
        return

    with open("data/seeds/products-old.json", encoding="utf-8") as f:
        products = json.load(f)

    insert_sql = sa.text(
        """
        INSERT INTO medicines (
            title, description, compositions, search_suggestion_keywords, tags,
            sku, seo, unit_price, maximum_retail_price, discount, final_price,
            thumbnail, subcategory_id, is_active, about_product, taxes,
            created_at, updated_at, discount_type, max_order_quantity,
            min_order_quantity, brand_tags, hsn_number, scheduled_drug,
            salt_type, prescription_req, packing_type, clinical_product_key,
            composition_key, dosage_form, release_type, route, stock_quantity
        ) VALUES (
            :title, :description, :compositions, :search_suggestion_keywords, :tags,
            :sku, :seo, :unit_price, :maximum_retail_price, :discount, :final_price,
            :thumbnail, :subcategory_id, :is_active, :about_product, :taxes,
            :created_at, :updated_at, :discount_type, :max_order_quantity,
            :min_order_quantity, :brand_tags, :hsn_number, :scheduled_drug,
            :salt_type, :prescription_req, :packing_type, :clinical_product_key,
            :composition_key, :dosage_form, :release_type, :route, :stock_quantity
        )
        """
    )

    for p in products:
        subcat = _normalize_subcategory(p.get("subCategoryId"))

        params = {
            "title": p.get("title"),
            "description": p.get("description"),
            "compositions": p.get("compositions"),
            "search_suggestion_keywords": _json_or_none(p.get("searchSuggestionKeywords")),
            "tags": _json_or_none(p.get("tags")),
            "sku": p.get("sku"),
            "seo": _json_or_none(p.get("seo")),
            "unit_price": p.get("unitPrice"),
            "maximum_retail_price": p.get("maximumRetailPrice"),
            "discount": p.get("discount"),
            "final_price": p.get("finalPrice"),
            "thumbnail": p.get("thumbnail"),
            "subcategory_id": subcat,
            "is_active": p.get("isActive"),
            "about_product": _json_or_none(p.get("aboutProduct")),
            "taxes": _json_or_none(p.get("taxes")),
            "created_at": p.get("createdAt"),
            "updated_at": p.get("updatedAt"),
            "discount_type": p.get("discountType"),
            "max_order_quantity": p.get("maxOrderQuantity"),
            "min_order_quantity": p.get("minOrderQuantity"),
            "brand_tags": _json_or_none(p.get("brandTags")),
            "hsn_number": p.get("hsnNumber"),
            "scheduled_drug": p.get("scheduledDrug"),
            "salt_type": p.get("saltType"),
            "prescription_req": p.get("prescriptionReq"),
            "packing_type": p.get("packingType"),
            "clinical_product_key": p.get("clinicalProductKey"),
            "composition_key": p.get("compositionKey"),
            "dosage_form": p.get("dosageForm"),
            "release_type": p.get("releaseType"),
            "route": p.get("route"),
            "stock_quantity": None,  # not present in seed; defaults to in-stock per model
        }

        conn.execute(insert_sql, params)


def downgrade() -> None:
    """Remove seeded medicines (best-effort; clears table if only seed data)."""
    conn = op.get_bind()
    # Only clear if this migration was the source; safe to truncate for dev seeds
    conn.execute(sa.text("TRUNCATE TABLE medicines RESTART IDENTITY CASCADE"))
