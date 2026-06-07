"""Order operations with mock (auto-confirmed) payments."""

from __future__ import annotations

import uuid
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.order import Order, OrderItem
from app.services import cart_service


class OrderError(Exception):
    """Raised on invalid order operations (empty cart, missing order)."""


def _coerce_uuid(order_id) -> Optional[uuid.UUID]:
    if isinstance(order_id, uuid.UUID):
        return order_id
    try:
        return uuid.UUID(str(order_id))
    except (ValueError, TypeError):
        return None


def create_order_from_cart(db: Session, user_id: int) -> Order:
    """Convert the user's active cart into a confirmed (mock-paid) order."""
    cart = cart_service.get_or_create_active_cart(db, user_id)
    if not cart.items:
        raise OrderError("Cannot create an order from an empty cart.")

    order = Order(
        user_id=user_id,
        status="confirmed",
        payment_status="mock_paid",
        total_amount=cart_service.cart_total(cart),
    )

    for item in cart.items:
        medicine = item.medicine
        order.items.append(
            OrderItem(
                medicine_id=item.medicine_id,
                sku=item.sku,
                title=medicine.title if medicine else None,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
        )

    db.add(order)

    # Mark the cart as converted and clear its items.
    cart.status = "converted"
    for item in list(cart.items):
        cart.items.remove(item)

    db.commit()
    db.refresh(order)
    return order


def get_order(db: Session, user_id: int, order_id) -> Optional[Order]:
    parsed = _coerce_uuid(order_id)
    if parsed is None:
        return None
    return (
        db.query(Order)
        .filter(Order.id == parsed, Order.user_id == user_id)
        .first()
    )


def list_orders(db: Session, user_id: int, limit: int = 10) -> List[Order]:
    return (
        db.query(Order)
        .filter(Order.user_id == user_id)
        .order_by(Order.created_at.desc())
        .limit(limit)
        .all()
    )
