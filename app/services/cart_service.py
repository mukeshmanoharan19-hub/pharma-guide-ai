"""Cart operations backed by the ``carts`` / ``cart_items`` tables."""

from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.cart import Cart, CartItem
from app.models.medicine import Medicine
from app.services import medicine_service


class CartError(Exception):
    """Raised on invalid cart operations (bad sku, quantity bounds)."""


def get_or_create_active_cart(db: Session, user_id: int) -> Cart:
    cart = (
        db.query(Cart)
        .filter(Cart.user_id == user_id, Cart.status == "active")
        .order_by(Cart.created_at.desc())
        .first()
    )
    if cart is None:
        cart = Cart(user_id=user_id, status="active")
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


def _get_item(cart: Cart, medicine_id: int) -> Optional[CartItem]:
    for item in cart.items:
        if item.medicine_id == medicine_id:
            return item
    return None


def _validate_quantity(medicine: Medicine, quantity: int) -> None:
    if quantity < 1:
        raise CartError("Quantity must be at least 1.")
    if (
        medicine.min_order_quantity is not None
        and quantity < medicine.min_order_quantity
    ):
        raise CartError(
            f"Minimum order quantity for {medicine.title} is "
            f"{medicine.min_order_quantity}."
        )
    if (
        medicine.max_order_quantity is not None
        and quantity > medicine.max_order_quantity
    ):
        raise CartError(
            f"Maximum order quantity for {medicine.title} is "
            f"{medicine.max_order_quantity}."
        )


def add_item(db: Session, user_id: int, sku: str, quantity: int = 1) -> Cart:
    medicine = medicine_service.get_by_sku(db, sku)
    if medicine is None:
        raise CartError(f"No medicine found for sku '{sku}'.")

    # Safety guardrail: prescription-only items require a verified prescription.
    if settings.BLOCK_RX_WITHOUT_PRESCRIPTION and getattr(
        medicine, "prescription_req", False
    ):
        raise CartError(
            f"{medicine.title} is a prescription-only medicine. A valid "
            "prescription is required and our pharmacist must verify it before "
            "this item can be purchased. Please consult a doctor or upload your "
            "prescription to proceed."
        )

    in_stock, _ = medicine_service.stock_for(medicine)
    if not in_stock:
        raise CartError(f"{medicine.title} is out of stock.")

    cart = get_or_create_active_cart(db, user_id)
    existing = _get_item(cart, medicine.id)
    new_quantity = quantity + (existing.quantity if existing else 0)
    _validate_quantity(medicine, new_quantity)

    if existing:
        existing.quantity = new_quantity
    else:
        cart.items.append(
            CartItem(
                medicine_id=medicine.id,
                sku=medicine.sku,
                quantity=quantity,
                unit_price=medicine_service.price_for(medicine),
            )
        )
    db.commit()
    db.refresh(cart)
    return cart


def update_item(db: Session, user_id: int, sku: str, quantity: int) -> Cart:
    medicine = medicine_service.get_by_sku(db, sku)
    if medicine is None:
        raise CartError(f"No medicine found for sku '{sku}'.")

    cart = get_or_create_active_cart(db, user_id)
    item = _get_item(cart, medicine.id)
    if item is None:
        raise CartError(f"{medicine.title} is not in the cart.")

    if quantity <= 0:
        cart.items.remove(item)
    else:
        _validate_quantity(medicine, quantity)
        item.quantity = quantity

    db.commit()
    db.refresh(cart)
    return cart


def remove_item(db: Session, user_id: int, sku: str) -> Cart:
    medicine = medicine_service.get_by_sku(db, sku)
    if medicine is None:
        raise CartError(f"No medicine found for sku '{sku}'.")

    cart = get_or_create_active_cart(db, user_id)
    item = _get_item(cart, medicine.id)
    if item is None:
        raise CartError(f"{medicine.title} is not in the cart.")

    cart.items.remove(item)
    db.commit()
    db.refresh(cart)
    return cart


def get_cart(db: Session, user_id: int) -> Cart:
    return get_or_create_active_cart(db, user_id)


def cart_total(cart: Cart) -> float:
    return round(
        sum((item.unit_price or 0.0) * item.quantity for item in cart.items), 2
    )
