"""Human-in-the-loop checkout review/confirmation service (Phase 8.5)."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.checkout_confirmation import CheckoutConfirmation
from app.services import cart_service, order_service


class CheckoutError(Exception):
    """Raised when checkout review/confirmation is invalid."""


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _coerce_uuid(value) -> Optional[uuid.UUID]:
    if isinstance(value, uuid.UUID):
        return value
    try:
        return uuid.UUID(str(value))
    except (TypeError, ValueError):
        return None


def _cart_snapshot_and_hash(cart) -> Tuple[list, float, str]:
    snapshot = [
        {
            "sku": item.sku,
            "title": item.medicine.title if item.medicine else None,
            "quantity": int(item.quantity),
            "unit_price": float(item.unit_price or 0.0),
            "line_total": round(float(item.unit_price or 0.0) * int(item.quantity), 2),
        }
        for item in cart.items
    ]
    # Stable cart version signature to detect stale confirmations.
    fingerprint_payload = [
        {
            "sku": row.get("sku"),
            "quantity": row.get("quantity"),
            "unit_price": row.get("unit_price"),
        }
        for row in snapshot
    ]
    fingerprint_payload.sort(
        key=lambda row: (
            row.get("sku") or "",
            int(row.get("quantity") or 0),
            float(row.get("unit_price") or 0.0),
        )
    )
    digest = hashlib.sha256(
        json.dumps(fingerprint_payload, sort_keys=True).encode("utf-8")
    ).hexdigest()
    total = cart_service.cart_total(cart)
    return snapshot, total, digest


def _expire_if_needed(conf: CheckoutConfirmation) -> bool:
    now = _now()
    expires_at = conf.expires_at
    # SQLite commonly returns naive datetimes even for timezone=True columns.
    if expires_at.tzinfo is None:
        now = now.replace(tzinfo=None)
    if conf.status == "pending" and expires_at <= now:
        conf.status = "expired"
        return True
    return False


def prepare_checkout(db: Session, user_id: int) -> CheckoutConfirmation:
    cart = cart_service.get_cart(db, user_id)
    if not cart.items:
        raise CheckoutError("Cannot prepare checkout from an empty cart.")

    snapshot, total, cart_hash = _cart_snapshot_and_hash(cart)
    expires_at = _now() + timedelta(
        minutes=settings.CHECKOUT_CONFIRMATION_TTL_MINUTES
    )
    confirmation = CheckoutConfirmation(
        user_id=user_id,
        cart_id=cart.id,
        items_snapshot=snapshot,
        total_amount=total,
        cart_version_hash=cart_hash,
        status="pending",
        expires_at=expires_at,
    )
    db.add(confirmation)
    db.commit()
    db.refresh(confirmation)
    return confirmation


def get_confirmation(
    db: Session, user_id: int, confirmation_id
) -> Optional[CheckoutConfirmation]:
    parsed = _coerce_uuid(confirmation_id)
    if parsed is None:
        return None
    confirmation = (
        db.query(CheckoutConfirmation)
        .filter(
            CheckoutConfirmation.id == parsed,
            CheckoutConfirmation.user_id == user_id,
        )
        .first()
    )
    if confirmation and _expire_if_needed(confirmation):
        db.commit()
    return confirmation


def confirm_checkout(db: Session, user_id: int, confirmation_id):
    confirmation = get_confirmation(db, user_id, confirmation_id)
    if confirmation is None:
        raise CheckoutError(
            f"No checkout confirmation found with id '{confirmation_id}'."
        )
    if confirmation.status == "expired":
        raise CheckoutError("This checkout confirmation has expired. Please review again.")
    if confirmation.status != "pending":
        raise CheckoutError(
            f"Checkout confirmation is already {confirmation.status}. "
            "Please start a new checkout review."
        )

    cart = cart_service.get_cart(db, user_id)
    if not cart.items:
        confirmation.status = "cancelled"
        confirmation.cancelled_at = _now()
        db.commit()
        raise CheckoutError("Your cart is empty. Please review your cart again.")

    _, _, live_hash = _cart_snapshot_and_hash(cart)
    if live_hash != confirmation.cart_version_hash:
        confirmation.status = "cancelled"
        confirmation.cancelled_at = _now()
        db.commit()
        raise CheckoutError("Cart changed since review. Please review again.")

    order = order_service.create_order_from_cart(db, user_id)
    confirmation.status = "confirmed"
    confirmation.confirmed_at = _now()
    db.commit()
    return order


def cancel_checkout(db: Session, user_id: int, confirmation_id) -> None:
    confirmation = get_confirmation(db, user_id, confirmation_id)
    if confirmation is None:
        raise CheckoutError(
            f"No checkout confirmation found with id '{confirmation_id}'."
        )
    if confirmation.status != "pending":
        return
    confirmation.status = "cancelled"
    confirmation.cancelled_at = _now()
    db.commit()
