"""Database operations for the medicine catalog."""

from __future__ import annotations

from typing import List, Optional, Tuple

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.medicine import Medicine

# Quantity assumed available when a row has no explicit inventory (mock data).
DEFAULT_STOCK = 100


def search_medicines(db: Session, query: str, limit: int = 5) -> List[Medicine]:
    like = f"%{query.strip()}%"
    return (
        db.query(Medicine)
        .filter(
            Medicine.is_active.is_(True),
            or_(
                Medicine.title.ilike(like),
                Medicine.compositions.ilike(like),
                Medicine.salt_type.ilike(like),
                Medicine.description.ilike(like),
            ),
        )
        .limit(limit)
        .all()
    )


def get_by_sku(db: Session, sku: str) -> Optional[Medicine]:
    return db.query(Medicine).filter(Medicine.sku == sku).first()


def resolve_for_cart(db: Session, identifier: str) -> Optional[Medicine]:
    """Resolve a medicine from SKU or product title for cart operations.

    The cart agent usually passes SKU, but in natural conversation it may pass
    an exact product title instead. This resolver supports both without
    changing the external tool contract.
    """
    if not identifier or not identifier.strip():
        return None

    value = identifier.strip()
    lowered = value.lower()

    # 1) SKU exact (case-insensitive).
    by_sku = (
        db.query(Medicine)
        .filter(Medicine.sku.isnot(None), func.lower(Medicine.sku) == lowered)
        .first()
    )
    if by_sku:
        return by_sku

    # 2) Title exact (case-insensitive), active products only.
    return (
        db.query(Medicine)
        .filter(Medicine.is_active.is_(True), func.lower(Medicine.title) == lowered)
        .first()
    )


def get_by_id(db: Session, medicine_id: int) -> Optional[Medicine]:
    return db.query(Medicine).filter(Medicine.id == medicine_id).first()


def find_alternatives(
    db: Session, medicine: Medicine, limit: int = 5
) -> List[Medicine]:
    """Find active medicines sharing a composition/salt with ``medicine``."""
    conditions = []
    if medicine.composition_key:
        conditions.append(Medicine.composition_key == medicine.composition_key)
    if medicine.salt_type:
        conditions.append(Medicine.salt_type == medicine.salt_type)

    if not conditions:
        return []

    return (
        db.query(Medicine)
        .filter(
            Medicine.is_active.is_(True),
            Medicine.id != medicine.id,
            or_(*conditions),
        )
        .limit(limit)
        .all()
    )


def stock_for(medicine: Medicine) -> Tuple[bool, int]:
    """Return ``(in_stock, available_quantity)`` for a medicine."""
    if not medicine.is_active:
        return False, 0
    if medicine.stock_quantity is None:
        return True, DEFAULT_STOCK
    return medicine.stock_quantity > 0, medicine.stock_quantity


def price_for(medicine: Medicine) -> float:
    """Best-effort unit price from available pricing fields."""
    for value in (
        medicine.final_price,
        medicine.unit_price,
        medicine.maximum_retail_price,
    ):
        if value is not None:
            return float(value)
    return 0.0
